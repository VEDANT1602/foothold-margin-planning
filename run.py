"""Finite-candidate footstep benchmark. Requires Python 3.10+ and NumPy."""
import argparse
import csv
from pathlib import Path
import platform
from time import perf_counter_ns
import numpy as np


HERE = Path(__file__).resolve().parent
STEPS, FOOT, REACH = 6, 23., 56.
MARGINS = [0, 4, 8, 10, 12, 14]


def terrain(seed, n, narrow):
    rng=np.random.default_rng(seed)
    mid=rng.uniform(-26,26,(n,STEPS,1))
    lanes=mid+np.array([-36.,36.])+rng.uniform(-9,9,(n,STEPS,2))
    widths=rng.uniform(39,60,lanes.shape)
    if narrow: widths[:,[2,4],:]=rng.uniform(25,42,(n,2,2))
    x=lanes[:,:,:,None]+(widths-FOOT)[:,:,:,None]*np.array([-.65,0,.65])
    x=x.reshape(n,STEPS,6)
    left=np.repeat(lanes-widths,3,axis=2)
    right=np.repeat(lanes+widths,3,axis=2)
    return x,left,right,rng


def search(x, valid):
    n,s,k=x.shape
    cost=np.where(valid[:,0] & (np.abs(x[:,0])<=REACH),1.25*np.abs(x[:,0]),np.inf)
    back=[]
    for i in range(1,s):
        dist=np.abs(x[:,i-1,:,None]-x[:,i,None,:])
        edge=np.where(dist<=REACH,dist+.25*np.abs(x[:,i,None,:]),np.inf)
        values=cost[:,:,None]+edge
        back.append(np.argmin(values,axis=1))
        cost=np.where(valid[:,i],np.min(values,axis=1),np.inf)
    path=np.empty((n,s),int)
    path[:,-1]=np.argmin(cost,axis=1)
    for i in range(s-2,-1,-1):
        path[:,i]=back[i][np.arange(n),path[:,i+1]]
    best=cost[np.arange(n),path[:,-1]]
    return path,np.isfinite(best),best


def exhaustive(x,valid):
    def visit(i,prev):
        if i==len(x): return 0.
        return min((abs(v-prev)+.25*abs(v)+visit(i+1,v) for v,ok in zip(x[i],valid[i])
                    if ok and abs(v-prev)<=REACH), default=np.inf)
    return visit(0,0.)


def max_clearance(x,clear):
    # Among paths with greatest minimum clearance, use the usual travel cost to break ties.
    best=np.where(np.abs(x[:,0])<=REACH,clear[:,0],-np.inf)
    for j in range(1,x.shape[1]):
        ok=np.abs(x[:,j-1,:,None]-x[:,j,None,:])<=REACH
        best=np.max(np.where(ok,np.minimum(best[:,:,None],clear[:,j,None,:]),-np.inf),axis=1)
    threshold=np.maximum(0.,np.max(best,axis=1))[:,None,None]
    return search(x,clear>=threshold)


def write(name,rows):
    with (HERE/name).open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main(timing):
    rows=[]
    latency=[]
    for split,seed,n,narrow in [("calibration",1708,600,False),("wide_test",8508,1400,False),("pinch_test",9508,1400,True)]:
        x,l,r,rng=terrain(seed,n,narrow)
        clear=np.minimum(x-l,r-x)-FOOT
        error_common=rng.uniform(-8,8,(n,1,1))
        error_local=rng.uniform(-8,8,(n,STEPS,2))
        loss_l=rng.uniform(0,6,(n,STEPS,2));loss_r=rng.uniform(0,6,(n,STEPS,2))
        for corr,shift in [("shared",np.broadcast_to(error_common,loss_l.shape)),("independent",error_local)]:
            for scale in [1.,1.75]:
                true_l=l+scale*np.repeat(shift+loss_l,3,axis=2)
                true_r=r+scale*np.repeat(shift-loss_r,3,axis=2)
                viable=np.minimum(x-true_l,true_r-x)>=FOOT
                _,oracle,oracle_cost=search(x,viable)
                for j in range(2):
                    assert np.isclose(exhaustive(x[j],viable[j]),oracle_cost[j])
                wide_path,wide_ok,_=max_clearance(x,clear)
                worst=clear[np.arange(n)[:,None],np.arange(STEPS),wide_path].min(axis=1)
                for m in MARGINS+["widest","widest_8","widest_12","widest_14"]:
                    if isinstance(m,str):
                        cutoff=int(m.split("_")[1]) if "_" in m else 0
                        path,accepted=wide_path,wide_ok & (worst>=cutoff)
                    else:
                        path,accepted,_=search(x,clear>=m)
                    supports=viable[np.arange(n)[:,None],np.arange(STEPS),path]
                    invalid=accepted & ~supports.all(axis=1)
                    if m==14 and scale==1.: assert not invalid.any()
                    rows.append(dict(split=split,correlation=corr,error_scale=scale,margin_mm=m,layouts=n,
                        oracle_feasible=int(oracle.sum()),accepted=int(accepted.sum()),valid_accepted=int((accepted & ~invalid).sum()),
                        false_feasible=int(invalid.sum()),rejected_feasible=int((~accepted & oracle).sum()),
                        alternative_exists=int((invalid & oracle).sum()),invalid_contacts=int((~supports & accepted[:,None]).sum())))
                    if timing and split=="pinch_test" and corr=="independent" and scale==1. and m==0:
                        # A pre-execution rescan reveals both boundaries of the first bad assigned patch.
                        for j in np.flatnonzero(invalid)[:160]:
                            step=int(np.flatnonzero(~supports[j])[0]); lane=path[j,step]//3
                            sl=slice(3*lane,3*lane+3)
                            start=perf_counter_ns()
                            updated=clear[j:j+1]>=0
                            updated[0,step,sl]=viable[j,step,sl]
                            _,yes,_=search(x[j:j+1],updated)
                            dt=(perf_counter_ns()-start)/1e6
                            latency.append(dict(layout=int(j),elapsed_ms=round(dt,6),path_found=int(yes[0]),
                                                platform=platform.machine(),python=platform.python_version(),numpy=np.__version__))
    write("results.csv",rows)
    if timing: write("timings.csv",latency)
    print(len(rows),"condition rows written.")


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--timings",action="store_true",help="also repeat the machine-dependent repair timing probe")
    main(parser.parse_args().timings)
