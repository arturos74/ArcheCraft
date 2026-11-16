"""Build a small bone-attached saddle accessory without modifying the Yata rig.

The texture is a code-authored pixel atlas for these cuboids, not a repaint of
the artist's embedded fur texture. Edit the boxes below to change the accessory.
"""
from pathlib import Path
import json,uuid
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from project_tools import load,render,write

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
ASSETS=ROOT/'src/main/resources/assets/archecraft'
project,bones,parents,owners,cubes,fur=load(HERE/'yata.bbmodel')
atlas=Image.new('RGBA',(32,32));rng=np.random.default_rng(419)
materials={'leather':((0,0,16,16),(109,62,37)),
           'edge':((16,0,32,16),(69,39,28)),
           'metal':((0,16,16,32),(170,160,130)),
           'blanket':((16,16,32,32),(116,43,38))}
for name,(uv,color) in materials.items():
    for x in range(uv[0],uv[2]):
        for y in range(uv[1],uv[3]):
            noise=int(rng.integers(-7,8));atlas.putpixel((x,y),tuple(max(0,min(255,c+noise)) for c in color)+(255,))
d=ImageDraw.Draw(atlas)
for x in range(1,16,4):d.point((x,1),fill=(185,136,82));d.point((x,14),fill=(185,136,82))
for y in range(1,16,4):d.point((1,y),fill=(185,136,82));d.point((14,y),fill=(185,136,82))
for y in range(18,32,4):d.line((17,y,30,y),fill=(143,57,43))
texture_path=ASSETS/'textures/entity/yata_saddle.png';texture_path.parent.mkdir(exist_ok=True,parents=True);atlas.save(texture_path)

boxes=[]
def box(name,lo,hi,material):boxes.append(dict(name=name,from_=lo,to=hi,material=material))
box('Saddle blanket',[-5.12,21.10,.6],[5.12,21.4,8.3],'blanket')
box('Leather seat',[-3.5,21.4,2],[3.5,22.1,6.8],'leather')
box('Front pommel',[-3.6,22.05,1.4],[3.6,22.75,2.3],'edge')
box('Rear cantle',[-3.6,22,6.7],[3.6,22.95,7.6],'edge')
for side,sign in [('left',-1),('right',1)]:
    def side_box(name,x0,x1,y0,y1,z0,z1,material):
        xs=sorted([sign*x0,sign*x1]);box(side+' '+name,[xs[0],y0,z0],[xs[1],y1,z1],material)
    side_box('blanket side',4.8,5.28,18.6,21.35,.7,8.2,'blanket')
    side_box('stirrup leather',5.30,5.52,14.8,21.4,3.3,4.05,'leather')
    side_box('buckle',5.5,5.64,18.1,18.85,3.16,4.17,'metal')
    for name,y0,y1,z0,z1 in [('stirrup top',15.7,15.92,2.8,4.6),('stirrup base',14.1,14.35,2.8,4.6),
        ('stirrup front',14.3,15.7,2.8,3.03),('stirrup back',14.3,15.7,4.37,4.6)]:
        side_box(name,5.32,5.62,y0,y1,z0,z1,'metal')

quads=[];preview_cubes=[];pivot=np.array(bones['body']['origin'])
for e in boxes:
    x0,y0,z0=e['from_'];x1,y1,z1=e['to'];uv=materials[e['material']][0]
    surfaces={
        'north':([(x1,y1,z0),(x0,y1,z0),(x0,y0,z0),(x1,y0,z0)],(0,0,-1)),
        'south':([(x0,y1,z1),(x1,y1,z1),(x1,y0,z1),(x0,y0,z1)],(0,0,1)),
        'east':([(x1,y1,z1),(x1,y1,z0),(x1,y0,z0),(x1,y0,z1)],(1,0,0)),
        'west':([(x0,y1,z0),(x0,y1,z1),(x0,y0,z1),(x0,y0,z0)],(-1,0,0)),
        'up':([(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)],(0,1,0)),
        'down':([(x0,y0,z1),(x1,y0,z1),(x1,y0,z0),(x0,y0,z0)],(0,-1,0))}
    for name,(vertices,normal) in surfaces.items():
        u,v,u1,v1=np.array(uv)/32;coords=[(u,v),(u1,v),(u1,v1),(u,v1)]
        points=[(np.array(p)-pivot)*np.array([-1,-1,1])/16 for p in vertices]
        n=np.array(normal)*np.array([-1,-1,1]);indices=[0,1,2,3]
        if np.dot(np.cross(points[1]-points[0],points[2]-points[0]),n)<0:indices=[0,3,2,1]
        quads.append(dict(bone='body',normal=n.tolist(),vertices=[[*points[i],*coords[i]] for i in indices]))
    uid=str(uuid.uuid5(uuid.NAMESPACE_DNS,'archecraft.yata.saddle.'+e['name']));owners[uid]='body'
    preview_cubes.append(dict(uuid=uid,name=e['name'],**{'from':e['from_']},to=e['to'],
        faces={name:dict(texture=0,uv=[uv[0]+256,uv[1],uv[2]+256,uv[3]]) for name in surfaces}))
write(ASSETS/'entity/yata_saddle.json',dict(format_version=1,quads=quads))
write(HERE/'yata_saddle_model.json',dict(bone='body',boxes=boxes,materials={k:list(v[0]) for k,v in materials.items()}))
combined=Image.new('RGBA',(288,256));combined.paste(fur,(0,0));combined.paste(atlas,(256,0))
preview=render(cubes+preview_cubes,combined,bones,parents,owners)
d=ImageDraw.Draw(preview);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',24)
d.text((28,24),'YATA / EQUIPPED SADDLE',font=font,fill=(231,220,202));preview.save(HERE/'yata_saddle_preview.png')
print(f'Built saddle: {len(boxes)} accessory cuboids, {len(quads)} quads, 32x32 pixel atlas. Original model/texture untouched.')
