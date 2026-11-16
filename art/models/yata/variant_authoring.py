"""Build a derived variant's UV atlas and scaled authoring rig without editing the base."""
from pathlib import Path
import base64,copy,hashlib,io,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from project_tools import load,write,render,export_geometry

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]

def build_variant(name,label,sex,paint,notes,scale=1.3):
    out=HERE/'variants'/name;out.mkdir(parents=True,exist_ok=True)
    source=HERE/'yata.bbmodel';original=source.read_bytes()
    project,bones,parents,owners,cubes,base_texture=load(source);derived=copy.deepcopy(project)
    materials={(f['cube'],f['face']):f['material'] for f in json.loads((HERE/'yata_uv_layout.json').read_text())}
    texture=base_texture.copy();rng=np.random.default_rng(31018)
    ears=[e for e in cubes if 'inner ear' in e['name'] and 'flap' not in e['name']]
    context=dict(ear_low=min(e['from'][1] for e in ears),ear_high=max(e['to'][1] for e in ears))
    for e in cubes:
        x0,y0,z0=e['from'];x1,y1,z1=e['to']
        faces={
            'north':((x1,y1,z0),(x0,y1,z0),(x1,y0,z0)),
            'south':((x0,y1,z1),(x1,y1,z1),(x0,y0,z1)),
            'east':((x1,y1,z1),(x1,y1,z0),(x1,y0,z1)),
            'west':((x0,y1,z0),(x0,y1,z1),(x0,y0,z0)),
            'up':((x0,y1,z0),(x1,y1,z0),(x0,y1,z1)),
            'down':((x0,y0,z1),(x1,y0,z1),(x0,y0,z0))}
        for face,data in e['faces'].items():
            if data.get('texture') is None:continue
            u,v,u1,v1=map(int,data['uv']);a,b,c=map(np.array,faces[face])
            for py in range(v,v1):
                for px in range(u,u1):
                    s=(px-u+.5)/(u1-u);t=(py-v+.5)/(v1-v)
                    color=np.array(paint(a+(b-a)*s+(c-a)*t,materials[e['name'],face],e['name'],face,e,context))
                    color=np.clip(color+int(rng.integers(-5,6)),0,255).astype(int)
                    texture.putpixel((px,py),tuple(color)+(255,))
    for e in derived['elements']:
        for key in ['from','to','origin']:e[key]=[round(v*scale,8) for v in e[key]]
    for g in derived.get('groups',[]):g['origin']=[round(v*scale,8) for v in g['origin']]
    def legacy(nodes):
        for n in nodes:
            if isinstance(n,dict):
                if 'origin' in n:n['origin']=[round(v*scale,8) for v in n['origin']]
                legacy(n.get('children',[]))
    legacy(derived['outliner'])
    for clip in derived['animations']:
        for animator in clip.get('animators',{}).values():
            for k in animator.get('keyframes',[]):
                if k['channel']=='position':
                    for p in k['data_points']:
                        for axis in 'xyz':p[axis]=round(float(p[axis])*scale,8)
    buffer=io.BytesIO();texture.save(buffer,format='PNG')
    derived['textures'][0].update(name=f'yata_{name}.png',source='data:image/png;base64,'+base64.b64encode(buffer.getvalue()).decode())
    derived['name']=label;model_path=out/f'yata_{name}.bbmodel';write(model_path,derived)
    texture.save(out/f'yata_{name}.png')
    runtime=ROOT/f'src/main/resources/assets/archecraft/textures/entity/yata_{name}.png';texture.save(runtime)
    _,db,dp,do,dc,dt=load(model_path)
    geometry=export_geometry(derived,db,dp,do,dc);geometry['minecraft:geometry'][0]['description']['identifier']='geometry.archecraft.yata_'+name
    write(out/f'yata_{name}.geo.json',geometry)
    external=json.loads((HERE/'yata.animation.json').read_text())
    for animation in external['animations'].values():
        for channels in animation.get('bones',{}).values():
            if 'position' in channels:
                for t,values in channels['position'].items():channels['position'][t]=[round(float(v)*scale,8) for v in values]
    write(out/f'yata_{name}.animation.json',external)
    preview=Image.new('RGB',(1700,850),(30,36,42))
    preview.paste(render(cubes,base_texture,bones,parents,owners,view_scale=11,baseline=740),(0,0))
    preview.paste(render(dc,dt,db,dp,do,view_scale=11,baseline=740),(850,0))
    draw=ImageDraw.Draw(preview);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',25)
    draw.text((30,25),'FEMALE / ORIGINAL SIZE',font=font,fill=(231,220,202))
    draw.text((880,25),label.upper()+' / 30% LARGER',font=font,fill=(231,220,202))
    preview.save(out/f'yata_{name}_comparison.png')
    render(dc,dt,db,dp,do,angle=110,center=(0,0,10),view_scale=10.7,baseline=740).save(out/f'yata_{name}_side.png')
    assert source.read_bytes()==original
    write(out/f'{name}_model_manifest.json',dict(female_source='art/models/yata/yata.bbmodel',
        female_source_sha256=hashlib.sha256(original).hexdigest(),male_only=sex=='male',female_only=sex=='female',
        variant=name,variant_scale=scale,cuboids=len(dc),bones=len(db),
        source_sha256=hashlib.sha256(model_path.read_bytes()).hexdigest(),texture_sha256=hashlib.sha256(runtime.read_bytes()).hexdigest(),notes=notes))
    print(f'Built {label}: {scale}x female, {len(dc)} cubes/{len(db)} bones, all six clips; existing Yata assets untouched.')
