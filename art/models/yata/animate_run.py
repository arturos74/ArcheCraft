"""Author the slowed reference's run on the saved model, without altering idle.

The useful repeating section is approximately 1.0--4.3s in 20%-speed footage:
3.3 * .20 = .66 seconds at normal speed. This is a hand-authored approximation.
"""
from pathlib import Path
import copy,hashlib,json,math,shutil,uuid
import numpy as np
from project_tools import load,write,matrix,world,corners

HERE=Path(__file__).resolve().parent
DURATION=.66
project,bones,parents,owners,cubes,texture=load(HERE/'yata.bbmodel')
backup=HERE/'versions/before_run_animation'
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

def motion(phase):
    channels={}
    def rot(name,x=0,y=0,z=0):channels.setdefault(name,{})['rotation']=np.array([x,y,z])
    def pos(name,x=0,y=0,z=0):channels.setdefault(name,{})['position']=np.array([x,y,z])
    wave=math.sin(2*math.pi*phase)
    rot('body',-12+3*wave)
    rot('chest',-8-2*wave)
    rot('neck',8+2*math.sin(2*math.pi*(phase-.08)))
    rot('head',10-3*math.sin(2*math.pi*(phase-.12)))
    for side,sign,lag in [('left',1,0),('right',-1,.16)]:
        p=(phase-lag)%1
        # Ankle trajectory: contact/push, lift, tucked recovery, forward reach.
        z=curve([(0,-3),(.18,5.5),(.28,6.5),(.43,.5),(.58,-5),(.75,-6.5),(1,-3)],p)
        y=curve([(0,6.1),(.18,5.5),(.28,8),(.43,11.5),(.58,10.8),(.75,8),(1,6.1)],p)
        thigh=side+'_thigh';shin=side+'_shin';foot=side+'_foot'
        hip=np.array(bones[thigh]['origin']);knee=np.array(bones[shin]['origin']);ankle=np.array(bones[foot]['origin'])
        upper=np.linalg.norm(knee-hip);lower=np.linalg.norm(ankle-knee)
        dy=y-hip[1];dz=z
        flex=-math.acos(np.clip((dy*dy+dz*dz-upper*upper-lower*lower)/(2*upper*lower),-.9999,.9999))
        angle=math.atan2(-dz,-dy)-math.atan2(lower*math.sin(flex),upper+lower*math.cos(flex))
        a,b=map(math.degrees,[angle,flex])
        pitch=curve([(0,0),(.13,0),(.24,-22),(.4,-36),(.58,-12),(.75,8),(1,0)],p)
        rot(thigh,a-bones[thigh]['rotation'][0]);rot(shin,b-bones[shin]['rotation'][0])
        rot(foot,pitch-a-b-bones[foot]['rotation'][0])
        arm=math.sin(2*math.pi*(phase-lag*.4))
        rot(side+'_upper_arm',8+9*arm,0,sign*3)
        rot(side+'_forearm',12-11*arm)
        rot(side+'_hand',-6+4*arm)
        # Swept-back ears with secondary tip/flap motion trailing the head bob.
        ear_wave=math.sin(2*math.pi*(phase-.12-lag*.2))
        rot('ear_'+side,67+5*ear_wave,sign*3,-sign*5)
        rot('ear_'+side+'_tip',18+9*math.sin(2*math.pi*(phase-.22-lag*.2)),0,sign*2)
        rot('ear_'+side+'_flap',20+7*math.sin(2*math.pi*(phase-.2)),0,-sign*8)
    rot('tail_base',10+3*math.sin(2*math.pi*(phase-.1)),2*math.sin(2*math.pi*phase))
    rot('tail_mid',8+4*math.sin(2*math.pi*(phase-.2)))
    rot('tail_tip',15+5*math.sin(2*math.pi*(phase-.3)))

    # Keep the lowest sole above the floor. The flight portion adds a small hop;
    # animation translates the visual root only, never the entity's physics.
    posed=copy.deepcopy(bones)
    for name,ch in channels.items():posed[name]['rotation']=(np.array(bones[name]['rotation'])+ch['rotation']).tolist()
    feet=[e for e in cubes if owners[e['uuid']] in ('left_foot','right_foot')]
    floor=min(corners(e,posed,parents,owners)[:,1].min() for e in feet)
    flight=curve([(0,0),(.2,.05),(.38,.65),(.53,.9),(.7,.35),(.86,0),(1,0)],phase)
    pos('root',y=max(0,-floor)+max(0,flight))
    return channels

clip=next((c for c in project['animations'] if c['name']=='animation.yata.run'),None)
if clip is None:
    clip=dict(uuid=str(uuid.uuid4()),name='animation.yata.run',loop='loop',override=False,
        length=DURATION,snapping=100,selected=False,saved=True,path='',animators={})
    project['animations'].append(clip)
clip.update(length=DURATION,loop='loop',snapping=100,animators={})
for frame in range(67):
    t=round(frame/100,4)
    channels=motion(frame/66 if frame<66 else 0)
    for name,values in channels.items():
        animator=clip['animators'].setdefault(bones[name]['uuid'],dict(name=name,type='bone',keyframes=[]))
        for channel,value in values.items():
            animator['keyframes'].append(dict(channel=channel,data_points=[dict(zip('xyz',[round(float(v),6) for v in value]))],
                uuid=str(uuid.uuid4()),time=t,color=-1,interpolation='linear'))

for field in before:
    if field!='animations':assert before[field]==project[field]
for old in before['animations']:
    if old['name']!='animation.yata.run':assert old==next(c for c in project['animations'] if c['name']==old['name'])
write(HERE/'yata.bbmodel',project)
external=json.loads((HERE/'yata.animation.json').read_text())
export=dict(loop=True,animation_length=DURATION,bones={})
for animator in clip['animators'].values():
    out={}
    for k in animator['keyframes']:
        channel=k['channel'];p=k['data_points'][0];v=[float(p[a]) for a in 'xyz']
        if channel=='rotation':v=[-v[0],-v[1],v[2]]
        if channel=='position':v=[-v[0],v[1],v[2]]
        out.setdefault(channel,{})[str(k['time'])]=v
    export['bones'][animator['name']]=out
external['animations'][clip['name']]=export
write(HERE/'yata.animation.json',external)
reference=Path('G:/Temp Recording Location/Yata Run.mp4')
write(HERE/'run_motion.json',dict(duration_seconds=DURATION,reference=reference.name,
    reference_sha256=hashlib.sha256(reference.read_bytes()).hexdigest(),reference_playback_speed=.2,
    reference_cycle_seconds=[1,4.3],notes='Approximate repeating stride, restored to normal speed (5x). '
        'Staggered hind-leg push/tuck/reach, forward lean, swept ears and delayed tail. Artist model and idle unchanged.'))
print(f'Authored {DURATION}s run on {len(clip["animators"])} bones; all existing artist data and clips preserved.')
