"""Compare local ANYmal lidar floor patches with the DARPA Finals course survey."""
import argparse
import csv
import hashlib
from pathlib import Path
import struct
import numpy as np
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation

HERE = Path(__file__).resolve().parent
FIELDS = ['scan','required_robot','required_survey','candidate_tiles','selected','supported','contradicted','unresolved']
GT_SHA = '0fb919c8addede3828da84316e6170b309ac5707e03bd3ef5da533188d77a854'
SURVEY_SHA = '7c1502d83767de3dd112d23c294739a6c481bfbe6abb0f4d3ba563dac35ed0f7'

def fields(block):
    offset = 0
    out = {}
    while offset < len(block):
        size = struct.unpack_from('<I',block,offset)[0]
        offset += 4
        name,value = block[offset:offset+size].split(b'=',1)
        out[name.decode()] = value
        offset += size
    return out

def record(block,offset):
    hlen = struct.unpack_from('<I',block,offset)[0]
    header = fields(block[offset+4:offset+4+hlen])
    start = offset+8+hlen
    size = struct.unpack_from('<I',block,start-4)[0]
    return header,start,start+size

def stamped(data):
    _,sec,ns,n = struct.unpack_from('<4I',data)
    return sec+ns*1.e-9,data[16:16+n],16+n

def poses(filename):
    raw=filename.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=GT_SHA:raise ValueError("Unexpected ANYmal 1 reference trajectory")
    h,_,end=record(raw,13)
    if raw[:13]!=b'#ROSBAG V2.0\n' or h['op']!=b'\x03':raise ValueError("Expected ROS1 v2 bag")
    values=[]
    while end<len(raw):
        h,start,end=record(raw,end)
        if h['op']!=b'\x05':continue
        if h['compression']!=b'none':raise ValueError("Expected uncompressed pose chunk")
        chunk=raw[start:end]; off=0
        while off<len(chunk):
            hh,begin,off=record(chunk,off)
            if hh['op']==b'\x02':
                data=chunk[begin:off];t,frame,pos=stamped(data)
                if frame!=b'map':raise ValueError("Unexpected pose frame")
                values.append((t,*struct.unpack_from('<7d',data,pos)))
    return np.array(values)

def decode(raw):
    seq=struct.unpack_from('<I',raw)[0];time,frame,off=stamped(raw)
    if frame!=b'lidar':raise ValueError("Expected lidar frame")
    packets=struct.unpack_from('<I',raw,off)[0]
    elevation=np.deg2rad(np.tile([-15,1,-13,3,-11,5,-9,7,-7,9,-5,11,-3,13,-1,15],2))
    delays=np.arange(32)%16*2.304+(np.arange(32)//16)*55.296
    pts=[]
    for j in range(packets):
        # ROS VelodynePacket is an eight-byte packet stamp followed by 1206 bytes.
        begin=off+4+1214*j+8;payload=raw[begin:begin+1206]
        if payload[-2:]!=b'\x37\x22':raise ValueError("Expected VLP-16 strongest-return packets")
        blocks=np.frombuffer(payload[:1200],np.uint8).reshape(12,100)
        if not np.all(blocks[:,:2]==[255,238]):raise ValueError("Invalid packet header")
        azimuth=blocks[:,2].astype(int)+256*blocks[:,3].astype(int)
        change=np.diff(azimuth)%36000
        change=np.append(change,change[-1])
        theta=np.deg2rad((azimuth[:,None]+change[:,None]*delays/110.592)*.01)
        channels=blocks[:,4:].reshape(12,32,3)
        distance=.002*(channels[:,:,0].astype(float)+256*channels[:,:,1].astype(float))
        xy=distance*np.cos(elevation)
        xyz=np.stack((xy*np.cos(theta),-xy*np.sin(theta),distance*np.sin(elevation)),axis=-1)
        pts.append(xyz[(distance>=.75)&(distance<=8.)])
    return seq,time,np.vstack(pts)

def first_scan(chunk_bytes):
    h,start,end=record(chunk_bytes,0)
    if h['op']!=b'\x05' or h['compression']!=b'none':raise ValueError("Unexpected sensor chunk")
    chunk=chunk_bytes[start:end];off=0
    while off<len(chunk):
        hh,k,off=record(chunk,off)
        if hh['op']==b'\x02' and struct.unpack('<I',hh['conn'])[0]==4:return decode(chunk[k:off])
    raise ValueError('Selected chunk has no Velodyne scan')

def elevation_grid(points,origin,yaw):
    # Square axes follow the horizontal projection of the laser's x axis.
    c,s=np.cos(yaw),np.sin(yaw)
    rel=(points-origin)@np.array([[c,-s,0],[s,c,0],[0,0,1]])
    keep=(abs(rel[:,0])<4.5)&(abs(rel[:,1])<4.5)&(rel[:,2]>=-1.4)&(rel[:,2]<=-.2)
    rel=rel[keep]
    bins=np.floor((rel[:,:2]+4.5)/.1).astype(int)
    height=np.full((90,90),np.nan)
    by_cell={}
    for (x,y),z in zip(bins,rel[:,2]):by_cell.setdefault((x,y),[]).append(z)
    for ij,z in by_cell.items():height[ij]=np.median(z)
    return height

def footprints(grid):
    cells=grid.reshape(30,3,30,3).transpose(0,2,1,3).reshape(900,9)
    seen=np.isfinite(cells)
    high=np.max(np.where(seen,cells,-np.inf),axis=1)
    low=np.min(np.where(seen,cells,np.inf),axis=1)
    return seen.sum(axis=1),high-low

def analyze(pts,pose,survey,search):
    origin=pose[1:4]
    rotation=Rotation.from_quat(pose[4:])
    matrix=rotation.as_matrix();yaw=np.arctan2(matrix[1,0],matrix[0,0])
    robot=elevation_grid(rotation.apply(pts)+origin,origin,yaw)
    ref=elevation_grid(survey[search.query_ball_point(origin[:2],7.)],origin,yaw)
    n,z=footprints(robot);m,height=footprints(ref)
    g=np.arange(30)*.3-4.35
    radius=np.hypot(*np.meshgrid(g,g,indexing='ij')).ravel()
    candidates=(radius>=2.5)&(radius<=4.)
    common=np.isfinite(robot)&np.isfinite(ref)
    errors=abs(robot[common]-ref[common])
    results=[]
    for k in (3,5,7,9):
        selected=candidates&(n>=k)&(z<=.1)
        for l in ((k,9) if k!=9 else (9,)):
            observed=m>=l;passes=observed&(height<=.1)
            counts=(candidates.sum(),selected.sum(),(selected&passes).sum(),(selected&observed&~passes).sum(),(selected&~observed).sum())
            if counts[1]!=sum(counts[2:]):raise ArithmeticError('Incomplete outcome accounting')
            results.append((k,l,*counts))
    return results,(common.sum(),np.median(errors) if len(errors) else np.nan)

def write(path,head,rows):
    with path.open('w',newline='') as f:
        w=csv.writer(f);w.writerow(head);w.writerows(rows)

def main():
    p=argparse.ArgumentParser()
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument('--bag',type=Path,help='Complete published ANYmal 1 raw sensor bag')
    group.add_argument('--chunks',type=Path,help='Offline local excerpts named chunk<bag_byte_offset>.bin')
    p.add_argument('--poses',required=True,type=Path);p.add_argument('--survey',required=True,type=Path)
    p.add_argument('--out',type=Path,default=HERE)
    args=p.parse_args()
    if hashlib.sha256(args.survey.read_bytes()).hexdigest()!=SURVEY_SHA:raise ValueError("Unexpected Finals survey")
    with args.survey.open() as f:
        for line in f:
            if line.strip()=='DATA ascii':break
        survey=np.loadtxt(f)
    if survey.shape!=(1000000,3):raise ValueError('Unexpected survey dimensions')
    search=cKDTree(survey[:,:2]);traj=poses(args.poses)
    with (HERE/'quadruped_input_manifest.csv').open() as f:targets=list(csv.DictReader(f))
    out=[];frames=[]
    for row in targets:
        offset=int(row['bag_byte_offset'])
        if args.bag:
            with args.bag.open('rb') as f:f.seek(offset);raw=f.read(int(row['range_length']))
        else:raw=(args.chunks/f'chunk{offset}.bin').read_bytes()
        if hashlib.sha256(raw).hexdigest()!=row['chunk_sha256']:raise ValueError('Chunk checksum mismatch')
        seq,t,pts=first_scan(raw)
        ix=np.argmin(abs(traj[:,0]-t))
        if seq!=int(row['scan']) or abs(traj[ix,0]-t)>.005:raise ValueError('Scan/pose registration mismatch')
        outcomes,frame=analyze(pts,traj[ix],survey,search)
        out.extend((seq,*v) for v in outcomes);frames.append((seq,*frame))
    args.out.mkdir(exist_ok=True,parents=True)
    write(args.out/'quadruped_footprints.csv',FIELDS,out)
    write(args.out/'quadruped_frames.csv',['scan','common_cells','median_absolute_height_gap_m'],frames)

if __name__=='__main__':main()
