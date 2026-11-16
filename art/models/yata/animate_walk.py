"""Author the Yata's alternating walk from the mounted reference; omit the rider.

This is a hand-authored approximation at the supplied clip's speed. Edit saved
keys in Blockbench and use export_runtime.py for normal artist updates.
"""
from pathlib import Path
import copy,hashlib,json,math,shutil,uuid
import numpy as np
from project_tools import load,write,matrix

HERE=Path(__file__).resolve().parent
DURATION=.96
project,bones,parents,owners,cubes,texture=load(HERE/'yata.bbmodel')
backup=HERE/'versions/before_walk_animation'
if not backup.exists():
    backup.mkdir(parents=True)
    for name in ['yata.bbmodel','yata.animation.json']:shutil.copy2(HERE/name,backup/name)
before=copy.deepcopy(project)

def curve(points,phase):
    phase%=1
    for i in range(len(points)-1):
        a,v=points[i];b,w=points[i+1]
        if a<=phase<b:
            prev=points[i-1] if i else (points[-2][0]-1,points[-2][1])
            nex=points[i+2] if i+2<len(points) else (1+points[1][0],points[1][1])
            m=(w-prev[1])/(b-prev[0]);n=(nex[1]-v)/(nex[0]-a);s=(phase-a)/(b-a)
            return (2*s**3-3*s*s+1)*v+(s**3-2*s*s+s)*(b-a)*m+(-2*s**3+3*s*s)*w+(s**3-s*s)*(b-a)*n
    raise ValueError(phase)

# The artist's foot has a raised heel and a rotated foot shaft. Compute actual
# sole height at each pitch, rather than assuming the ankle is at ground level.
foot_points={}
for side in ['left','right']:
    name=side+'_foot';pivot=np.array(bones[name]['origin']);points=[]
    for e in [e for e in cubes if owners[e['uuid']]==name]:
        origin=np.array(e.get('origin',[0,0,0]));r=matrix(e.get('rotation',[0,0,0]))
        for x in [e['from'][0],e['to'][0]]:
            for y in [e['from'][1],e['to'][1]]:
                for z in [e['from'][2],e['to'][2]]:
                    points.append(r@(np.array([x,y,z])-origin)+origin-pivot)
    foot_points[side]=np.array(points)

def motion(phase):
    channels={}
    def rot(name,x=0,y=0,z=0):channels.setdefault(name,{})['rotation']=np.array([x,y,z])
    wave=math.sin(2*math.pi*phase);bob=math.cos(4*math.pi*phase)
    root_y=.18+.14*bob
    channels['root']={'position':np.array([0,root_y,0])}
    rot('body',-2+.7*bob,0,.6*wave)
    rot('chest',-.8*bob)
    rot('neck',.7*bob)
    rot('head',2-.9*math.cos(4*math.pi*(phase-.035)),.8*wave)
    for side,sign,lag in [('left',1,0),('right',-1,.5)]:
        p=(phase-lag)%1
        z=curve([(0,-3),(.12,-1.55),(.4,1.8),(.58,3.9),(.68,3.6),(.8,-.5),(.93,-3.8),(1,-3)],p)
        lift=curve([(0,0),(.58,0),(.66,.6),(.78,2.7),(.88,1.8),(.96,.25),(1,0)],p)
        # No flight phase: the other leg supports the Yata during recovery.
        lift=max(0,lift)
        pitch=curve([(0,0),(.52,0),(.65,-12),(.78,-8),(.9,5),(1,0)],p)
        sole=(matrix([pitch,0,0])@foot_points[side].T).T[:,1].min()
        y=-sole+lift-root_y
        thigh=side+'_thigh';shin=side+'_shin';foot=side+'_foot'
        hip=np.array(bones[thigh]['origin']);knee=np.array(bones[shin]['origin']);ankle=np.array(bones[foot]['origin'])
        upper=np.linalg.norm(knee-hip);lower=np.linalg.norm(ankle-knee)
        dy=y-hip[1];dz=z
        flex=-math.acos(np.clip((dy*dy+dz*dz-upper*upper-lower*lower)/(2*upper*lower),-.9999,.9999))
        angle=math.atan2(-dz,-dy)-math.atan2(lower*math.sin(flex),upper+lower*math.cos(flex))
        a,b=map(math.degrees,[angle,flex])
        rot(thigh,a-bones[thigh]['rotation'][0]);rot(shin,b-bones[shin]['rotation'][0])
        rot(foot,pitch-a-b-bones[foot]['rotation'][0])
        arm=math.sin(2*math.pi*(phase-lag))
        rot(side+'_upper_arm',3+3*arm,0,sign*.5)
        rot(side+'_forearm',2-3*arm)
        rot(side+'_hand',-1+1.5*arm)
        ear=math.sin(4*math.pi*(phase-.065-lag*.04))
        rot('ear_'+side,3+1.5*ear,sign*.5,-sign*.5)
        rot('ear_'+side+'_tip',2+2*math.sin(4*math.pi*(phase-.11-lag*.04)))
        rot('ear_'+side+'_flap',1.5*math.sin(4*math.pi*(phase-.1)),0,sign*wave)
    rot('tail_base',2+math.sin(4*math.pi*(phase-.07)),3*math.sin(2*math.pi*(phase-.05)))
    rot('tail_mid',6+2*math.sin(4*math.pi*(phase-.12)),4*math.sin(2*math.pi*(phase-.13)))
    rot('tail_tip',9+3*math.sin(4*math.pi*(phase-.18)),5*math.sin(2*math.pi*(phase-.2)))
    return channels

clip=next(c for c in project['animations'] if c['name']=='animation.yata.walk')
clip.update(length=DURATION,loop='loop',snapping=100,animators={})
for frame in range(97):
    t=round(frame/100,4);channels=motion(frame/96 if frame<96 else 0)
    for name,values in channels.items():
        animator=clip['animators'].setdefault(bones[name]['uuid'],dict(name=name,type='bone',keyframes=[]))
        for channel,value in values.items():
            animator['keyframes'].append(dict(channel=channel,data_points=[dict(zip('xyz',[round(float(v),6) for v in value]))],
                uuid=str(uuid.uuid4()),time=t,color=-1,interpolation='linear'))
for field in before:
    if field!='animations':assert before[field]==project[field]
for old in before['animations']:
    if old['name']!='animation.yata.walk':assert old==next(c for c in project['animations'] if c['name']==old['name'])
write(HERE/'yata.bbmodel',project)
external=json.loads((HERE/'yata.animation.json').read_text());export=dict(loop=True,animation_length=DURATION,bones={})
for animator in clip['animators'].values():
    out={}
    for k in animator['keyframes']:
        channel=k['channel'];p=k['data_points'][0];v=[float(p[a]) for a in 'xyz']
        if channel=='rotation':v=[-v[0],-v[1],v[2]]
        if channel=='position':v=[-v[0],v[1],v[2]]
        out.setdefault(channel,{})[str(k['time'])]=v
    export['bones'][animator['name']]=out
external['animations'][clip['name']]=export;write(HERE/'yata.animation.json',external)
reference=Path('G:/Temp Recording Location/Yata Walk.mp4')
write(HERE/'walk_motion.json',dict(duration_seconds=DURATION,reference=reference.name,
    reference_sha256=hashlib.sha256(reference.read_bytes()).hexdigest(),reference_playback_speed=1,
    notes='Approximate .95--.96s repeating alternating stride observed in the supplied clip; no speed correction requested. '
        'Ignore the mounted player. Upright torso, low foot clearance, planted support leg, small arm/ear motion and gentle tail sway. '
        'Artist model, idle and run unchanged.'))
print(f'Authored {DURATION}s walk on {len(clip["animators"])} bones; artist model, idle and run preserved.')
