"""Build the black male variant's code-native UV atlas and 130%-scale project.

Reference: ScreenShot0015/16/17. The female rig and all existing sex assets are
read without modification; runtime uses the shared animated rig at 1.3 scale.
"""
from pathlib import Path
import base64,copy,hashlib,io,json,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from project_tools import load,write,render,export_geometry

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=HERE/'variants/black';OUT.mkdir(parents=True,exist_ok=True)
source=HERE/'yata.bbmodel';project,bones,parents,owners,cubes,female_texture=load(source)
source_bytes=source.read_bytes();black=copy.deepcopy(project)
materials={(f['cube'],f['face']):f['material'] for f in json.loads((HERE/'yata_uv_layout.json').read_text())}
texture=female_texture.copy();rng=np.random.default_rng(31017)
ear_inner=[e for e in cubes if 'inner ear' in e['name'] and 'flap' not in e['name']]
ear_low=min(e['from'][1] for e in ear_inner);ear_high=max(e['to'][1] for e in ear_inner)

def patch(point,face):
    x,y,z=point
    if face in ('up','down'):a=abs(x)/2.65;b=(z+.45*math.sin(x))/3.5
    elif face in ('north','south'):a=x/2.65;b=y/3.15
    else:a=(z+.35*math.sin(y))/3.5;b=y/3.15
    ia,ib=math.floor(a),math.floor(b)
    if (ia*13+ib*7)%7==0:return 10
    # Small irregular diamonds, offset rows and a darker border: readable at
    # Minecraft UV resolution, with the back and flanks spotted rather than striped.
    u=(a+.16*math.sin(ib*2.1))%1-.5;v=(b+.10*math.sin(ia*1.7))%1-.5
    return abs(u)/.31+abs(v)/.30

def paint(point,material,name,face,e):
    x,y,z=point;noise=int(rng.integers(-5,6));coat=np.array([48,46,48],dtype=float)
    color=coat.copy()
    if material=='fur':
        spotted=any(word in name.lower() for word in ['haunch','back and shoulders','upper thigh','knee','neck','tail root'])
        if spotted and not (face=='down' or ('neck' in name.lower() and face=='north')):
            distance=patch(point,face)
            if distance<.80:color=np.array([187,187,185],dtype=float)
            elif distance<1.10:color=np.array([145,145,141],dtype=float)
        if 'forearm' in name.lower():color=np.array([186,186,183],dtype=float)
        if name=='Head' and abs(x)>2.4:
            zc=(e['from'][2]+e['to'][2])/2+.7;yc=e['from'][1]+.65
            if ((z-zc)/1.05)**2+((y-yc)/.8)**2<1:color=np.array([183,183,180],dtype=float)
    elif material=='cream':
        if any(s in name.lower() for s in ['muzzle','jaw','brush']):color=np.array([196,196,194],dtype=float)
        else:color=coat.copy()
    elif material=='inner':
        high=(y-ear_low)/(ear_high-ear_low);color=np.array([192,192,190],dtype=float)
        if high>.91:color=np.array([143,143,139],dtype=float)
    elif material=='foot':
        if 'paw' in name:color=np.array([185,185,182],dtype=float)
        elif 'lower leg' in name or 'ankle' in name:
            color=np.array([75,62,61],dtype=float)
            if (y*2)%2<.4:color*=.72
        else:color=np.array([48,40,40],dtype=float)
    elif material in ('claw','nose'):color=np.array([23,22,25],dtype=float)
    elif material=='eyelid':color=np.array([41,39,42],dtype=float)
    elif material=='eye':color=np.array([13,16,18],dtype=float)
    elif material=='white':color=np.array([197,197,196],dtype=float)
    return tuple(np.clip(color+noise,0,255).astype(int))+(255,)

for e in cubes:
    x0,y0,z0=e['from'];x1,y1,z1=e['to']
    surfaces={
        'north':((x1,y1,z0),(x0,y1,z0),(x1,y0,z0)),
        'south':((x0,y1,z1),(x1,y1,z1),(x0,y0,z1)),
        'east':((x1,y1,z1),(x1,y1,z0),(x1,y0,z1)),
        'west':((x0,y1,z0),(x0,y1,z1),(x0,y0,z0)),
        'up':((x0,y1,z0),(x1,y1,z0),(x0,y1,z1)),
        'down':((x0,y0,z1),(x1,y0,z1),(x0,y0,z0))}
    for face,data in e['faces'].items():
        if data.get('texture') is None:continue
        u,v,u1,v1=map(int,data['uv']);a,b,c=map(np.array,surfaces[face])
        for py in range(v,v1):
            for px in range(u,u1):
                s=(px-u+.5)/(u1-u);t=(py-v+.5)/(v1-v)
                texture.putpixel((px,py),paint(a+(b-a)*s+(c-a)*t,materials[e['name'],face],e['name'],face,e))

for e in black['elements']:
    for key in ['from','to','origin']:e[key]=[round(v*1.3,8) for v in e[key]]
for g in black.get('groups',[]):g['origin']=[round(v*1.3,8) for v in g['origin']]
def legacy(nodes):
    for node in nodes:
        if isinstance(node,dict):
            if 'origin' in node:node['origin']=[round(v*1.3,8) for v in node['origin']]
            legacy(node.get('children',[]))
legacy(black['outliner'])
for clip in black['animations']:
    for animator in clip.get('animators',{}).values():
        for k in animator.get('keyframes',[]):
            if k['channel']=='position':
                for p in k['data_points']:
                    for axis in 'xyz':p[axis]=round(float(p[axis])*1.3,8)
buffer=io.BytesIO();texture.save(buffer,format='PNG')
black['textures'][0].update(name='yata_black.png',source='data:image/png;base64,'+base64.b64encode(buffer.getvalue()).decode())
black['name']='Black Male Yata';write(OUT/'yata_black.bbmodel',black);texture.save(OUT/'yata_black.png')
runtime=ROOT/'src/main/resources/assets/archecraft/textures/entity/yata_black.png';texture.save(runtime)
_,bb,bp,bo,bc,bt=load(OUT/'yata_black.bbmodel')
geometry=export_geometry(black,bb,bp,bo,bc);geometry['minecraft:geometry'][0]['description']['identifier']='geometry.archecraft.yata_black'
write(OUT/'yata_black.geo.json',geometry)
external=json.loads((HERE/'yata.animation.json').read_text())
for animation in external['animations'].values():
    for channels in animation.get('bones',{}).values():
        if 'position' in channels:
            for t,values in channels['position'].items():channels['position'][t]=[round(float(v)*1.3,8) for v in values]
write(OUT/'yata_black.animation.json',external)
comparison=Image.new('RGB',(1700,850),(30,36,42))
comparison.paste(render(cubes,female_texture,bones,parents,owners,view_scale=11,baseline=740),(0,0))
comparison.paste(render(bc,bt,bb,bp,bo,view_scale=11,baseline=740),(850,0))
d=ImageDraw.Draw(comparison);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',25)
d.text((30,25),'FEMALE / ORIGINAL SIZE',font=font,fill=(231,220,202));d.text((880,25),'BLACK MALE / 30% LARGER',font=font,fill=(231,220,202))
comparison.save(OUT/'yata_black_comparison.png')
render(bc,bt,bb,bp,bo,angle=110,center=(0,0,10),view_scale=10.7,baseline=740).save(OUT/'yata_black_side.png')
assert source.read_bytes()==source_bytes
write(OUT/'black_model_manifest.json',dict(female_source='art/models/yata/yata.bbmodel',
    female_source_sha256=hashlib.sha256(source_bytes).hexdigest(),male_only=True,variant='black',variant_scale=1.3,
    cuboids=len(bc),bones=len(bb),source_sha256=hashlib.sha256((OUT/'yata_black.bbmodel').read_bytes()).hexdigest(),
    texture_sha256=hashlib.sha256(runtime.read_bytes()).hexdigest(),
    notes='Shared canonical runtime rig with variant scale 1.3. Dark charcoal fur with soft light-gray markings, ears, muzzle, forepaws and tail tuft.'))
print('Built Black Male Yata: 1.3x female, 92 cubes/29 bones, all six clips, separate atlas. Existing Yata assets untouched.')
