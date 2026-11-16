"""Apply a pronounced backward lower-leg bend to the current saved project."""
from pathlib import Path
import copy, math, shutil
import numpy as np
from project_tools import load,world,corners,write,export_geometry,preview,render
from PIL import Image,ImageDraw,ImageFont

HERE=Path(__file__).resolve().parent
path=HERE/'yata.bbmodel'
project,bones,parents,owners,cubes,texture=load(path)
before=copy.deepcopy(project)
backup=HERE/'versions/before_leg_fix'
backup.mkdir(parents=True,exist_ok=True)
for name in ['yata.bbmodel','yata.png']:
    if not (backup/name).exists():shutil.copy2(HERE/name,backup/name)

for side in ['left','right']:
    thigh=side+'_thigh';shin=side+'_shin';foot=side+'_foot'
    pieces=[e for e in cubes if owners[e['uuid']]==foot]
    floor=min(corners(e,bones,parents,owners)[:,1].min() for e in pieces)
    bones[thigh]['rotation']=[32,0,0]
    bones[shin]['rotation']=[-72,0,0]
    bones[foot]['rotation']=[40,0,0]
    raised=min(corners(e,bones,parents,owners)[:,1].min() for e in pieces)
    # Extend the lower leg along its own axis until the original foot sole is
    # planted again. Torso height and foot pitch remain unchanged.
    delta=(floor-raised)/math.cos(math.radians(40))
    bones[foot]['origin'][1]=round(bones[foot]['origin'][1]+delta,6)
    for e in pieces:
        for key in ['from','to','origin']:
            if key in e:e[key][1]=round(e[key][1]+delta,6)
    lower=next(e for e in cubes if e['name']==side+' lower leg')
    lower['from'][1]=round(lower['from'][1]+delta,6)
    print(side,'foot planted at',min(corners(e,bones,parents,owners)[:,1].min() for e in pieces),'lower leg extension',round(-delta,3))

assert project['animations']==before['animations']
assert project['textures']==before['textures']
assert len(project['elements'])==len(before['elements'])
write(path,project)
write(HERE/'yata.geo.json',export_geometry(project,bones,parents,owners,cubes))
layout_path=HERE/'yata_uv_layout.json'
if layout_path.exists():
    import json
    names={e['name'] for e in cubes}
    write(layout_path,[f for f in json.loads(layout_path.read_text()) if f['cube'] in names])
texture.save(HERE/'yata.png')
preview(HERE/'yata_legs_preview.png',cubes,texture,bones,parents,owners)
preview(HERE/'yata_preview.png',cubes,texture,bones,parents,owners)
render(cubes,texture,bones,parents,owners,180).save(HERE/'yata_front.png')
ear_demo=Image.new('RGB',(1700,920),(30,36,42))
ear_demo.paste(render(cubes,texture,bones,parents,owners,ear_joints=True),(0,55))
saved_rotations={n:list(bones[n]['rotation']) for n in ['ear_left_tip','ear_right_tip']}
bones['ear_left_tip']['rotation']=[-70,0,12]
bones['ear_right_tip']['rotation']=[-50,0,-10]
ear_demo.paste(render(cubes,texture,bones,parents,owners,ear_joints=True),(850,55))
for name,rotation in saved_rotations.items():bones[name]['rotation']=rotation
d=ImageDraw.Draw(ear_demo);font=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',27)
small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',19)
d.text((30,16),'YATA / FLOPPY EAR HINGES + REVISED LEGS',font=font,fill=(231,220,202))
d.text((30,865),'NEUTRAL / cyan dots mark the ear hinges',font=small,fill=(174,188,193))
d.text((880,865),'POSE EXAMPLE / independent ear-tip movement',font=small,fill=(174,188,193))
ear_demo.save(HERE/'yata_ear_pivots.png')
points=np.vstack([corners(e,bones,parents,owners) for e in cubes]);lo=points.min(axis=0);hi=points.max(axis=0)
seat=world(bones['rider_seat']['origin'],'rider_seat',bones,parents)
write(HERE/'yata_scale.json',dict(model_units_per_block=16,model_bounds_units=dict(min=lo.tolist(),max=hi.tolist()),
    visual_size_blocks=dict(zip(['width','height','length'],((hi-lo)/16).tolist())),
    rider_seat_model_units=seat.tolist(),rider_seat_blocks=(seat/16).tolist(),
    suggested_entity_hitbox_blocks=dict(width=1.3964844,height=1.6),
    note='Visual bounds include ears and tail. Riding guide only; no runtime mount behavior.'))
print('Updated current saved project, geometry, scale and previews without replacing texture or animation data.')
