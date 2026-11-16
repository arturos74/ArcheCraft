"""Author the reference idle on the saved rig, preserving geometry and other clips.

Run once to create/recreate this particular idle. For artist changes, edit the
saved project instead and run export_runtime.py (which never reauthors keys).
"""
from pathlib import Path
import copy, hashlib, json, math, shutil, uuid
import numpy as np
from project_tools import load, write

HERE=Path(__file__).resolve().parent
DURATION=4.2
project,bones,parents,owners,cubes,texture=load(HERE/'yata.bbmodel')
backup=HERE/'versions/before_idle_animation'
if not backup.exists():
    backup.mkdir(parents=True)
    for name in ['yata.bbmodel','yata.animation.json']:
        shutil.copy2(HERE/name,backup/name)
before=copy.deepcopy(project)
clip=next(c for c in project['animations'] if c['name']=='animation.yata.idle')
clip.update(length=DURATION,loop='loop',snapping=20,animators={})

# Values use Blockbench's authoring axes, in degrees/model units. A periodic
# Hermite curve is baked to editable linear keys so both players match exactly.
def curve(points,t):
    points=[(float(a),float(b)) for a,b in points]
    assert points[0][0]==0 and points[-1][0]==DURATION and points[0][1]==points[-1][1]
    if t>=DURATION:return points[-1][1]
    for i in range(len(points)-1):
        a,v=points[i];b,w=points[i+1]
        if a<=t<b:
            prev=points[i-1] if i else (points[-2][0]-DURATION,points[-2][1])
            nex=points[i+2] if i+2<len(points) else (DURATION+points[1][0],points[1][1])
            m=(w-prev[1])/(b-prev[0]);n=(nex[1]-v)/(nex[0]-a)
            s=(t-a)/(b-a)
            return (2*s**3-3*s*s+1)*v+(s**3-2*s*s+s)*(b-a)*m+(-2*s**3+3*s*s)*w+(s**3-s*s)*(b-a)*n
    raise ValueError(t)

controls={}
def add(name,channel,axes):
    controls.setdefault(name,{})[channel]=axes

breath=[(0,0),(.9,.12),(2,0),(3.2,-.08),(4.2,0)]
add('body','position',[None,breath,None])
add('body','rotation',[[(0,0),(1,.45),(2.1,0),(3.2,-.35),(4.2,0)],None,None])
add('chest','rotation',[[(0,0),(1,-.7),(2.1,0),(3.2,.5),(4.2,0)],None,None])
add('neck','rotation',[[(0,0),(.8,-.5),(1.6,1),(2.2,-.5),(3,-.3),(4.2,0)],None,None])
add('head','rotation',[
    [(0,0),(.7,0),(1.25,1),(1.7,4),(2,2),(2.25,-1),(2.75,.5),(3.4,-.5),(4.2,0)],
    [(0,0),(1,-1),(1.7,-3),(2.3,0),(3,1),(4.2,0)],
    [(0,0),(1.4,.8),(2.4,-.6),(3.4,.3),(4.2,0)]])
for side,sign in [('left',1),('right',-1)]:
    add('ear_'+side,'rotation',[None,[(0,0),(1.6,sign*1.5),(2.3,-sign),(3.3,0),(4.2,0)],
        [(0,0),(1.5,sign*1.5),(2.15,-sign*2),(2.6,sign),(3.2,0),(4.2,0)]])
    if side=='left':
        flick=[(0,0),(.8,-2),(1.6,-8),(2,-15),(2.25,12),(2.5,4),(3.1,0),(4.2,0)]
    else:
        flick=[(0,0),(1,-1),(1.8,-5),(2.1,-8),(2.4,6),(2.7,2),(3.3,0),(4.2,0)]
    add('ear_'+side+'_tip','rotation',[flick,None,None])
    add('ear_'+side+'_flap','rotation',[
        [(0,0),(1.8,-2),(2.2,4),(2.55,-3),(3.1,0),(4.2,0)],None,
        [(0,0),(1.4,sign),(2.3,-sign*2),(2.65,sign*1.5),(3.3,0),(4.2,0)]])
    add(side+'_upper_arm','rotation',[
        [(0,0),(.9,-1),(1.8,2 if side=='left' else 4),(2.5,-1),(3.4,.5),(4.2,0)],None,None])
    add(side+'_forearm','rotation',[
        [(0,0),(1.1,1.4),(2,-2),(2.7,.8),(3.5,-.5),(4.2,0)],None,None])
    add(side+'_hand','rotation',[[(0,0),(1.2,-1),(2.2,1.8),(3.1,-.5),(4.2,0)],None,None])
for name,values in [
    ('tail_base',[(0,0),(.4,8),(1.1,22),(1.6,26),(2.3,16),(3,1),(3.6,-5),(4.2,0)]),
    ('tail_mid',[(0,0),(.4,5),(1.1,12),(1.6,14),(2.3,7),(3,-2),(3.6,-4),(4.2,0)]),
    ('tail_tip',[(0,0),(.6,1),(1.3,8),(1.9,10),(2.5,5),(3.2,-3),(3.7,-2),(4.2,0)])]:
    add(name,'rotation',[[(0,0),(1.4,1.5),(2.6,-1),(3.5,.5),(4.2,0)],values,None])

for name,channels in controls.items():
    keys=[]
    for channel,axes in channels.items():
        for frame in range(85):
            t=round(frame/20,4)
            values=[round(curve(p,t),6) if p else 0 for p in axes]
            keys.append(dict(channel=channel,data_points=[dict(zip('xyz',values))],
                uuid=str(uuid.uuid4()),time=t,color=-1,interpolation='linear'))
    clip['animators'][bones[name]['uuid']]=dict(name=name,type='bone',keyframes=keys)

for field in before:
    if field!='animations':assert project[field]==before[field],field
for old,new in zip(before['animations'],project['animations']):
    if old['name']!='animation.yata.idle':assert old==new
write(HERE/'yata.bbmodel',project)

# Standalone Bedrock animation export; BB5 stores keys in authoring coordinates.
external=json.loads((HERE/'yata.animation.json').read_text())
idle=dict(loop=True,animation_length=DURATION,bones={})
for animator in clip['animators'].values():
    out={}
    for k in animator['keyframes']:
        channel=k['channel'];p=k['data_points'][0];v=[float(p[a]) for a in 'xyz']
        if channel=='rotation':v=[-v[0],-v[1],v[2]]
        if channel=='position':v=[-v[0],v[1],v[2]]
        out.setdefault(channel,{})[str(k['time'])]=v
    idle['bones'][animator['name']]=out
external['animations'][clip['name']]=idle
write(HERE/'yata.animation.json',external)
reference=Path('G:/Temp Recording Location/Yata Idle.mp4')
write(HERE/'idle_motion.json',dict(duration_seconds=DURATION,samples_per_second=20,
    reference=reference.name,reference_sha256=hashlib.sha256(reference.read_bytes()).hexdigest(),
    notes='Hand-authored approximation: planted feet, gentle breathing/head lift, delayed ear flick and slow tail sweep. No geometry changes.',
    authoring_axes='Blockbench 5 local additive rotation (degrees) and position (model units)',controls=controls))
print(f'Authored {DURATION}s idle, {len(controls)} bones; geometry, texture and other clips unchanged.')
