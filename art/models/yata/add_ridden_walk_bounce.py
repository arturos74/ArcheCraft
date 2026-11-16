"""Add a gentle two-beat root bounce to the saved ridden walk only."""
from pathlib import Path
import copy,json,math,shutil
from project_tools import load,write

PEAK_UNITS=.45
def bounce_offset(time,duration):
    return PEAK_UNITS*(.5+.5*math.cos(4*math.pi*time/duration))

if __name__=='__main__':
    here=Path(__file__).resolve().parent
    project,bones,*_=load(here/'yata.bbmodel');before=copy.deepcopy(project)
    backup=here/'versions/before_ridden_walk_bounce_animation'
    if not backup.exists():
        backup.mkdir(parents=True)
        for name in ['yata.bbmodel','yata.animation.json']:shutil.copy2(here/name,backup/name)
    original=json.loads((backup/'yata.bbmodel').read_text())
    name='animation.yata.ridden_walk'
    clip=next(c for c in project['animations'] if c['name']==name)
    old_clip=next(c for c in original['animations'] if c['name']==name)
    root=clip['animators'][bones['root']['uuid']]
    old_root=old_clip['animators'][bones['root']['uuid']]
    keys={k['time']:k for k in old_root['keyframes'] if k['channel']=='position'}
    for k in root['keyframes']:
        if k['channel']=='position':
            k['data_points'][0]['y']=round(float(keys[k['time']]['data_points'][0]['y'])+bounce_offset(k['time'],clip['length']),6)
    for field in before:
        if field!='animations':assert before[field]==project[field]
    for old in before['animations']:
        if old['name']!=name:assert old==next(c for c in project['animations'] if c['name']==old['name'])
    write(here/'yata.bbmodel',project)
    external=json.loads((here/'yata.animation.json').read_text())
    external['animations'][name]['bones']['root']['position']={str(k['time']):[-float(k['data_points'][0]['x']),float(k['data_points'][0]['y']),float(k['data_points'][0]['z'])]
        for k in root['keyframes'] if k['channel']=='position'}
    write(here/'yata.animation.json',external)
    metadata=json.loads((here/'ridden_walk_motion.json').read_text())
    metadata.update(bounce_peak_model_units=PEAK_UNITS,bounce_beats_per_cycle=2,
        notes='Independent 1.5x-cadence ridden walk with a gentle .45-unit (0.028-block) added root hop, twice per stride. '
            'Cycle timing, movement speed, artist geometry and all other animations preserved.')
    write(here/'ridden_walk_motion.json',metadata)
    print('Added gentle .45-unit root bounce to ridden walk; .64s pace and all other clips unchanged.')
