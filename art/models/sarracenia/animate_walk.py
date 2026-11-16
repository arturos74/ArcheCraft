"""Add a reference-based walk, preserving the current artwork and idle clip."""
from pathlib import Path
import copy
import hashlib
import json
import math
import shutil
import sys
import uuid
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'yata'))
import project_tools as pt

NAME = 'animation.sarracenia.walk'
DURATION = .92
FPS = 50
project,bones,parents,owners,cubes,texture = pt.load(HERE/'sarracenia.bbmodel')
before = copy.deepcopy(project)
backup = HERE/'versions/before_walk_animation'
if not backup.exists():
    backup.mkdir(parents=True)
    for name in ['sarracenia.bbmodel','sarracenia.animation.json','model_manifest.json']:
        shutil.copy2(HERE/name,backup/name)

tracks = {}


def add(name,channel,axes):
    tracks.setdefault(name,{})[channel] = axes


def cosine(t,delay=0): return math.cos(2*math.pi*t/DURATION-delay)
def sine(t,delay=0): return math.sin(2*math.pi*t/DURATION-delay)


# A whole-plant shuffle: body rocks about the base, rather than inventing legs.
# The root's vertical track is solved after posing to keep its short toes above
# the floor, with a small bounce measured relative to the source's body height.
add('root','rotation',[lambda t:3*cosine(t,.15),lambda t:1.2*sine(t),lambda t:2.4*sine(t)])
add('root','position',[None,None,lambda t:.3*sine(t,.2)])
add('lower_roots','rotation',[lambda t:4*cosine(t),None,lambda t:-sine(t)])
add('body','position',[None,lambda t:.2*cosine(t),None])
add('body','rotation',[lambda t:-4+6*cosine(t),lambda t:sine(t),lambda t:1.5*sine(t)])
add('mouth','rotation',[lambda t:-6+5*cosine(t,-.2),None,lambda t:.8*sine(t)])
add('hood','rotation',[lambda t:-52+19*cosine(t,.1),None,lambda t:2*sine(t,.1)])

# Both long tendrils curl up in the side view, with a slight left/right offset
# and progressively delayed bends to reproduce the trailing leaf tips.
for side,sign in [('left',-1),('right',1)]:
    delay = 0 if side=='left' else .12
    stem = 'back_stem_'+side+'_outer'
    add(stem,'rotation',[
        lambda t,d=delay:-13+17*cosine(t,.3+d),
        lambda t,s=sign,d=delay:s*(3+5*sine(t,.2+d)),
        lambda t,s=sign,d=delay:s*(4+7*sine(t,.15+d))])
    add(stem+'_bend_1','rotation',[
        lambda t,d=delay:-13+25*cosine(t,.6+d),
        None,lambda t,s=sign,d=delay:-s*10*sine(t,.45+d)])
    add(stem+'_bend_2','rotation',[
        lambda t,d=delay:-6+20*cosine(t,.9+d),
        None,lambda t,s=sign,d=delay:s*7*sine(t,.7+d)])
    add(stem+'_leaf','rotation',[
        lambda t,d=delay:8+26*cosine(t,1.1+d),
        lambda t,s=sign:s*3*sine(t,.8),
        lambda t,s=sign,d=delay:s*10*sine(t,1+d)])

# Rear blades stay on their common fork and flutter behind the pitching body.
add('rear_stalk','rotation',[lambda t:-8+13*cosine(t,.25),lambda t:2*sine(t),lambda t:2*sine(t,.3)])
add('rear_stalk_tip','rotation',[lambda t:10*cosine(t,.6),None,lambda t:1.5*sine(t,.5)])
for side,sign in [('left',-1),('right',1)]:
    add('rear_fork_'+side,'rotation',[
        lambda t:6*cosine(t,.7),lambda t,s=sign:s*2*sine(t,.4),lambda t,s=sign:s*3*sine(t,.5)])
    add('rear_fork_'+side+'_leaf','rotation',[
        lambda t:-4+17*cosine(t,.9),None,lambda t,s=sign:s*6*sine(t,.8)])


def sample(t):
    return {name:{channel:np.array([axis(t) if axis else 0 for axis in axes])
                  for channel,axes in channels.items()} for name,channels in tracks.items()}


def world(point,name,pose):
    point = np.array(point,dtype=float)
    while name:
        b=bones[name];pivot=np.array(b['origin']);ch=pose.get(name,{})
        point=pt.matrix(np.array(b.get('rotation',[0,0,0]))+ch.get('rotation',0))@(point-pivot)+pivot
        point+=ch.get('position',0)
        name=parents[name]
    return point


root_vertices=[]
for cube in cubes:
    if owners[cube['uuid']]!='lower_roots':continue
    pivot=np.array(cube['origin'])
    for x in (cube['from'][0],cube['to'][0]):
        for y in (cube['from'][1],cube['to'][1]):
            for z in (cube['from'][2],cube['to'][2]):
                root_vertices.append(pt.matrix(cube['rotation'])@(np.array([x,y,z])-pivot)+pivot)

poses=[]
for frame in range(round(DURATION*FPS)+1):
    t=round(frame/FPS,6);pose=sample(t)
    lowest=min(world(v,'lower_roots',pose)[1] for v in root_vertices)
    bounce=.9*(.5+.5*cosine(t,-.3))**2
    pose['root']['position'][1]=-lowest+bounce
    poses.append(pose)
poses[-1]=copy.deepcopy(poses[0])

clip=dict(name=NAME,uuid=str(uuid.uuid5(uuid.NAMESPACE_URL,NAME)),loop='loop',override=False,
          length=DURATION,snapping=FPS,anim_time_update='',blend_weight='',start_delay='',loop_delay='',animators={})
external=dict(loop=True,animation_length=DURATION,bones={})
for name,channels in tracks.items():
    keys=[];out={}
    for channel in channels:
        exported={}
        for frame,pose in enumerate(poses):
            t=round(frame/FPS,6);v=np.round(pose[name][channel],6).tolist()
            keys.append(dict(channel=channel,data_points=[dict(zip('xyz',v))],
                uuid=str(uuid.uuid5(uuid.NAMESPACE_URL,f'{NAME}/{name}/{channel}/{t}')),
                time=t,color=-1,interpolation='linear'))
            converted=[-v[0],-v[1],v[2]] if channel=='rotation' else [-v[0],v[1],v[2]]
            exported[str(t)]=converted
        out[channel]=exported
    clip['animators'][bones[name]['uuid']]=dict(name=name,type='bone',keyframes=keys)
    external['bones'][name]=out
project['animations']=[a for a in project['animations'] if a['name']!=NAME]+[clip]
for field in before:
    if field!='animations':assert before[field]==project[field],field
for old in before['animations']:
    if old['name']!=NAME:assert old in project['animations']
pt.write(HERE/'sarracenia.bbmodel',project)
export_path=HERE/'sarracenia.animation.json'
export=json.loads(export_path.read_text());export['animations'][NAME]=external
pt.write(export_path,export)
references=[]
for label,filename in [('side','2026-11-14 20-30-32.mp4'),('front','2026-11-14 20-31-25.mp4')]:
    src=Path('G:/Temp Recording Location')/filename
    references.append(dict(view=label,file=filename,sha256=hashlib.sha256(src.read_bytes()).hexdigest()))
pt.write(HERE/'walk_motion.json',dict(duration_seconds=DURATION,samples_per_second=FPS,references=references,
    notes='Hand-authored approximation of the moving portion of both references. Roughly .92s repeating shuffle: forward/back body rock, small bounce, subtle lateral sway, synchronized tendril curls and delayed blade flutter. Authored in place for later entity movement; source pauses and camera motion excluded.'))
manifest=json.loads((HERE/'model_manifest.json').read_text())
manifest.update(model_sha256=hashlib.sha256((HERE/'sarracenia.bbmodel').read_bytes()).hexdigest(),animations=len(project['animations']))
pt.write(HERE/'model_manifest.json',manifest)
print(f'Authored {DURATION}s walk on {len(tracks)} bones. Preserved saved artwork and all other animations.')
