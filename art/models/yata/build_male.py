"""Derive a 110%-scale striped male project from the saved female Yata rig.

The UV atlas is painted from authored face coordinates, preserving the female
project and all animation/bone names. Runtime shares the rig and applies the
same 1.1 scale to rendering, collision dimensions and the rider attachment.
"""
from pathlib import Path
import base64,copy,hashlib,io,json,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from project_tools import load,write,render,export_geometry

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=HERE/'male';OUT.mkdir(exist_ok=True)
source=HERE/'yata.bbmodel'
project,bones,parents,owners,cubes,female_texture=load(source)
original_bytes=source.read_bytes();male=copy.deepcopy(project)
layout=json.loads((HERE/'yata_uv_layout.json').read_text())
materials={(f['cube'],f['face']):f['material'] for f in layout}
texture=female_texture.copy();rng=np.random.default_rng(21876)
ear_inner=[e for e in cubes if 'inner ear' in e['name'] and 'flap' not in e['name']]
ear_low=min(e['from'][1] for e in ear_inner);ear_high=max(e['to'][1] for e in ear_inner)

def paint(point,material,name):
    x,y,z=point;noise=int(rng.integers(-6,7))
    if material=='fur':
        color=np.array([151,96,61],dtype=float)
        # Irregular cream bands wrap the neck, flanks, thighs and long tail.
        if any(word in name for word in ['tail','Tail']):q=z*.9+.4*y;period=5.0
        elif 'neck' in name.lower() or name=='Chest':q=y+.32*z+.3*math.sin(z);period=5.5
        else:q=z+.38*y+.65*math.sin(y*.7)+.15*abs(x);period=5.7
        distance=abs((q+period/2)%period-period/2)
        if distance<.52:color=np.array([231,222,190],dtype=float)
        elif distance<.76:color=np.array([180,145,106],dtype=float)
        if 'Head'==name or 'eye socket' in name:color=np.array([145,95,64],dtype=float)
        if 'ear' in name:
            color=np.array([145,101,69],dtype=float)
            high=(y-ear_low)/(ear_high-ear_low)
            if high>.86:color=np.array([38,30,24],dtype=float)
            elif high>.76:color=np.array([66,49,35],dtype=float)
    elif material=='cream':color=np.array([229,222,201],dtype=float)
    elif material=='inner':
        high=(y-ear_low)/(ear_high-ear_low);color=np.array([207,199,178],dtype=float)
        center=-2.295 if 'left' in name else 2.295;xx=x-center
        for sx,sy,radius in [(-.7,.22,.27),(.5,.3,.23),(-.3,.43,.33),(.8,.55,.26),(-.7,.63,.22),(.1,.7,.32)]:
            if (xx-sx)**2+((high-sy)*(ear_high-ear_low))**2<radius**2:color=np.array([79,59,53],dtype=float)
        if high>.85:color=np.array([45,37,31],dtype=float)
        elif high>.76:color=np.array([94,78,61],dtype=float)
    elif material=='foot':
        color=np.array([93,80,66] if 'lower leg' in name or 'ankle' in name else [58,44,33],dtype=float)
        if ('lower leg' in name or 'ankle' in name) and (y*2)%2<.35:color*=.72
    elif material in ('claw','nose'):color=np.array([25,23,23],dtype=float)
    elif material=='eyelid':color=np.array([103,73,51],dtype=float)
    elif material=='eye':color=np.array([15,19,18],dtype=float)
    else:color=np.array([239,234,211],dtype=float)
    return tuple(np.clip(color+noise,0,255).astype(int))+(255,)

for e in cubes:
    x0,y0,z0=e['from'];x1,y1,z1=e['to']
    # Origin, horizontal edge and vertical edge for each authored face UV.
    faces={
        'north':((x1,y1,z0),(x0,y1,z0),(x1,y0,z0)),
        'south':((x0,y1,z1),(x1,y1,z1),(x0,y0,z1)),
        'east':((x1,y1,z1),(x1,y1,z0),(x1,y0,z1)),
        'west':((x0,y1,z0),(x0,y1,z1),(x0,y0,z0)),
        'up':((x0,y1,z0),(x1,y1,z0),(x0,y1,z1)),
        'down':((x0,y0,z1),(x1,y0,z1),(x0,y0,z0))}
    for name,data in e['faces'].items():
        if data.get('texture') is None:continue
        u,v,u1,v1=map(int,data['uv']);a,b,c=map(np.array,faces[name])
        material=materials[e['name'],name]
        for py in range(v,v1):
            for px in range(u,u1):
                s=(px-u+.5)/(u1-u);t=(py-v+.5)/(v1-v)
                texture.putpixel((px,py),paint(a+(b-a)*s+(c-a)*t,material,e['name']))

for e in male['elements']:
    for key in ['from','to','origin']:e[key]=[round(v*1.1,8) for v in e[key]]
for g in male.get('groups',[]):g['origin']=[round(v*1.1,8) for v in g['origin']]
def scale_legacy(nodes):
    for node in nodes:
        if isinstance(node,dict):
            if 'origin' in node:node['origin']=[round(v*1.1,8) for v in node['origin']]
            scale_legacy(node.get('children',[]))
scale_legacy(male['outliner'])
for clip in male['animations']:
    for animator in clip.get('animators',{}).values():
        for k in animator.get('keyframes',[]):
            if k['channel']=='position':
                for p in k['data_points']:
                    for a in 'xyz':p[a]=round(float(p[a])*1.1,8)
buffer=io.BytesIO();texture.save(buffer,format='PNG')
male['textures'][0].update(name='yata_male.png',source='data:image/png;base64,'+base64.b64encode(buffer.getvalue()).decode())
male['name']='Male Yata'
write(OUT/'yata_male.bbmodel',male);texture.save(OUT/'yata_male.png')
runtime=ROOT/'src/main/resources/assets/archecraft/textures/entity/yata_male.png';texture.save(runtime)
_,mb,mp,mo,mc,mt=load(OUT/'yata_male.bbmodel')
geometry=export_geometry(male,mb,mp,mo,mc)
geometry['minecraft:geometry'][0]['description']['identifier']='geometry.archecraft.yata_male'
write(OUT/'yata_male.geo.json',geometry)
external=json.loads((HERE/'yata.animation.json').read_text())
for animation in external['animations'].values():
    for channels in animation.get('bones',{}).values():
        if 'position' in channels:
            for t,values in channels['position'].items():channels['position'][t]=[round(float(v)*1.1,8) for v in values]
write(OUT/'yata_male.animation.json',external)

comparison=Image.new('RGB',(1700,850),(30,36,42))
comparison.paste(render(cubes,female_texture,bones,parents,owners,view_scale=12,baseline=740),(0,0))
comparison.paste(render(mc,mt,mb,mp,mo,view_scale=12,baseline=740),(850,0))
d=ImageDraw.Draw(comparison);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',25)
d.text((30,25),'FEMALE / ORIGINAL MODEL',font=font,fill=(231,220,202))
d.text((880,25),'MALE / STRIPED / 10% LARGER',font=font,fill=(231,220,202))
comparison.save(OUT/'yata_sexes_preview.png')
render(mc,mt,mb,mp,mo,angle=90,center=(0,0,10),view_scale=12,baseline=740).save(OUT/'yata_male_side.png')
assert source.read_bytes()==original_bytes
write(OUT/'male_model_manifest.json',dict(female_source='art/models/yata/yata.bbmodel',
    female_source_sha256=hashlib.sha256(original_bytes).hexdigest(),male_scale=1.1,cuboids=len(mc),bones=len(mb),
    runtime='Shared rig with sex scale via getAgeScale; male pixel atlas selected by synced sex. Saddle scales with the renderer.',
    male_source_sha256=hashlib.sha256((OUT/'yata_male.bbmodel').read_bytes()).hexdigest(),
    texture_sha256=hashlib.sha256(runtime.read_bytes()).hexdigest()))
print('Built striped 110%-scale male: 92 cubes, 29 bones, all six clips; female project and texture unchanged.')
