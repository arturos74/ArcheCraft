"""Make an independently editable, quicker ridden walk from the saved wild walk."""
from pathlib import Path
import copy,json,shutil,uuid
from project_tools import load,write
from add_ridden_walk_bounce import bounce_offset,PEAK_UNITS

HERE=Path(__file__).resolve().parent
project,*_=load(HERE/'yata.bbmodel');before=copy.deepcopy(project)
backup=HERE/'versions/before_ridden_walk_animation'
if not backup.exists():
    backup.mkdir(parents=True)
    for name in ['yata.bbmodel','yata.animation.json']:shutil.copy2(HERE/name,backup/name)
source=next(c for c in project['animations'] if c['name']=='animation.yata.walk')
name='animation.yata.ridden_walk';duration=.64
clip=copy.deepcopy(source);clip.update(name=name,uuid=str(uuid.uuid4()),length=duration,snapping=150,selected=False)
ratio=duration/source['length']
for animator in clip['animators'].values():
    for k in animator['keyframes']:
        k['time']=round(k['time']*ratio,8);k['uuid']=str(uuid.uuid4())
        if animator['name']=='root' and k['channel']=='position':
            k['data_points'][0]['y']=round(float(k['data_points'][0]['y'])+bounce_offset(k['time'],duration),6)
index=next((i for i,c in enumerate(project['animations']) if c['name']==name),None)
if index is None:project['animations'].append(clip)
else:project['animations'][index]=clip
for field in before:
    if field!='animations':assert project[field]==before[field]
for old in before['animations']:
    if old['name']!=name:assert old==next(c for c in project['animations'] if c['name']==old['name'])
write(HERE/'yata.bbmodel',project)
external=json.loads((HERE/'yata.animation.json').read_text())
export=copy.deepcopy(external['animations'][source['name']]);export['animation_length']=duration
for channels in export['bones'].values():
    for ch,keys in channels.items():channels[ch]={str(round(float(t)*ratio,8)):v for t,v in keys.items()}
for t,v in export['bones']['root']['position'].items():v[1]=round(float(v[1])+bounce_offset(float(t),duration),6)
external['animations'][name]=export;write(HERE/'yata.animation.json',external)
write(HERE/'ridden_walk_motion.json',dict(source_clip=source['name'],duration_seconds=duration,
    playback_rate=source['length']/duration,
    bounce_peak_model_units=PEAK_UNITS,bounce_beats_per_cycle=2,
    notes='Independent 1.5x-cadence walk with gentle two-beat root bounce for a controlling rider. Wild walk, run, movement speed and artist model unchanged.'))
print('Created .64s ridden walk (1.5x cadence). Existing model and all five earlier clips unchanged.')
