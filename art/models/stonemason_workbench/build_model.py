"""Stonemason geometry authored natively in a 16-by-16 footprint."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import base64, io, json, math, random, uuid
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ASSETS=ROOT/'src/main/resources/assets/archecraft'
rng=random.Random(4162)
atlas=Image.new('RGBA',(128,64))
palette=[(85,94,86),(105,113,103),(48,160,179),(75,189,200),
         (112,79,48),(57,70,76),(121,128,116),(37,47,51)]
for tile,base in enumerate(palette):
    ox,oy=tile%4*32,tile//4*32
    patches=[[rng.randint(-8,8) for _ in range(8)] for _ in range(8)]
    for y in range(32):
        for x in range(32):
            n=rng.choice([-2,-1,0,0,1,2])+patches[y//4][x//4]*(0.4 if tile in (2,3,5,7) else 0.7)
            if tile==4:n+=-12 if x%5==0 else 0
            if tile in (2,3):n+=4-y/8
            atlas.putpixel((ox+x,oy+y),tuple(max(0,min(255,round(c+n))) for c in base)+(255,))
    d=ImageDraw.Draw(atlas)
    if tile in (0,1,6):
        for _ in range(12):
            x,y=rng.randrange(30),rng.randrange(30)
            d.rectangle((ox+x,oy+y,ox+x+1,oy+y+1),fill=(base[0]-9,base[1]-5,base[2]-9,255))
        for x,y in [(5,9),(20,22)]:
            d.line((ox+x,oy+y,ox+x+2,oy+y,ox+x+3,oy+y+1),fill=tuple(c-17 for c in base)+(255,))
    if tile in (2,3):
        d.line((ox+6,oy+5,ox+7,oy+7,ox+9,oy+8),fill=tuple(c-12 for c in base)+(255,))
        d.line((ox+17,oy+15,ox+19,oy+15,ox+20,oy+17),fill=tuple(c-9 for c in base)+(255,))

pieces=[]
def cube(name,lo,hi,tile,group,top=None,rotation=None):
    pieces.append(dict(name=name,lo=list(lo),hi=list(hi),tile=tile,group=group,top=top,rotation=rotation))

# All coordinates are native model units; no global or per-axis compression.
cube('Hand-hewn foundation',(1.5,0,1.5),(14.5,5.5,14.5),0,'Foundation',top=1)
cube('Broken front footing',(2.5,0,0.5),(12.5,1.5,1.5),0,'Foundation',top=6)
cube('Left rough edge',(0.5,0,4),(1.5,3.5,12),0,'Foundation',top=1)
cube('Right rough edge',(14.5,0,4),(15.5,2,10),0,'Foundation',top=6)
cube('Rear footing',(4,0,14.5),(12.5,1,15.5),0,'Foundation',top=1)
cube('Solid working pedestal',(3,5.5,3),(13,10,13),0,'Working stone',top=1)
cube('Rough front shoulder',(4,5.5,2.5),(11.5,9.5,3),0,'Working stone',top=6)
cube('Chipped left shoulder',(2.5,5.5,5),(3,8.5,12),0,'Working stone',top=6)
cube('Chipped right shoulder',(13,5.5,4),(13.5,8,11),0,'Working stone',top=6)
cube('Blue mineral workpiece',(4.175,10,4.175),(11.825,17.225,11.825),2,'Blue workpiece',top=3)

hammer=dict(axis='z',angle=22.5,origin=[5.125,3,15])
cube('Sledgehammer iron head',(3.25,1.8,14),(7,4.2,15.8),5,'Sledgehammer',rotation=hammer)
cube('Sledgehammer straight ash handle',(4.75,2.4,14.65),(5.5,13,15.35),4,'Sledgehammer',rotation=hammer)
cube('Sledgehammer iron collar',(4.6,4.2,14.5),(5.65,4.8,15.5),7,'Sledgehammer',rotation=hammer)
chisel=dict(axis='z',angle=22.5,origin=[13.15,3,1.25])
cube('Long chisel wooden grip',(12.75,6,0.85),(13.55,13,1.65),4,'Long chisel',rotation=chisel)
cube('Long chisel iron shaft',(12.9,3.2,1),(13.4,6.2,1.5),5,'Long chisel',rotation=chisel)
cube('Long chisel cutting edge',(12.55,2.7,0.85),(13.75,3.4,1.65),5,'Long chisel',rotation=chisel)
short=dict(axis='y',angle=22.5,origin=[11,5.8,14])
cube('Small chisel grip on ledge',(9.5,5.5,13.6),(11,6.1,14.3),4,'Small chisel',rotation=short)
cube('Small chisel blade on ledge',(11,5.6,13.7),(12.8,5.9,14.2),5,'Small chisel',rotation=short)
cube('Loose stone chip left',(0.5,0,13.7),(1.8,0.7,15.4),6,'Loose chips')
cube('Loose stone chip front',(12.9,0,0.4),(14.8,0.6,1.3),0,'Loose chips',top=6)
cube('Loose stone chip on ledge',(2,5.5,10.5),(2.8,6,12),6,'Loose chips')
cube('Loose small flake on ledge',(8.5,5.5,13.3),(9.1,5.8,14),6,'Loose chips')

DIRECTIONS=['north','east','south','west','up','down']
def faces(p):
    dx,dy,dz=[b-a for a,b in zip(p['lo'],p['hi'])]
    output={}
    for face in DIRECTIONS:
        w,h=(dx,dz) if face in ('up','down') else (dz,dy) if face in ('east','west') else (dx,dy)
        t=p['top'] if face=='up' and p['top'] is not None else p['tile']
        x,y=t%4*32,t//4*32
        output[face]=dict(uv=[x,y,x+w,y+h],texture=0)
    return output

elements=[]
for i,p in enumerate(pieces):
    e=dict(name=p['name'],type='cube',uuid=str(uuid.uuid5(uuid.NAMESPACE_URL,'archecraft:stonemason-v2/'+str(i))),
           **{'from':p['lo'],'to':p['hi']},origin=[8,0,8],box_uv=False,autouv=0,faces=faces(p))
    if p['rotation']:
        r=p['rotation'];e['origin']=r['origin']
        e['rotation']=[r['angle'] if a==r['axis'] else 0 for a in 'xyz']
    elements.append(e)

def native_rotation(e):
    for i,angle in enumerate(e.get('rotation',[0,0,0])):
        if angle:return dict(angle=angle,axis='xyz'[i],origin=e['origin'],rescale=False)
    return None

def transform(v,r,normal=False):
    if not r:return np.array(v,dtype=float)
    origin=np.zeros(3) if normal else np.array(r['origin'],dtype=float)
    x,y,z=np.array(v,dtype=float)-origin
    a=math.radians(r['angle']);c,s=math.cos(a),math.sin(a)
    if r['axis']=='z':p=np.array([c*x-s*y,s*x+c*y,z])
    elif r['axis']=='y':p=np.array([c*x+s*z,y,-s*x+c*z])
    else:p=np.array([x,c*y-s*z,s*y+c*z])
    return p+origin

def vertices(lo,hi):
    return [[x,y,z] for x in (lo[0],hi[0]) for y in (lo[1],hi[1]) for z in (lo[2],hi[2])]

def collision_boxes(e):
    lo,hi=np.array(e['from'],float),np.array(e['to'],float);r=native_rotation(e)
    if not r:return [list(lo)+list(hi)]
    # Slice long angled tools to avoid large invisible collision boxes.
    axis=int(np.argmax(hi-lo));count=math.ceil((hi[axis]-lo[axis])/1.2);output=[]
    for i in range(count):
        a,b=lo.copy(),hi.copy()
        a[axis]=lo[axis]+(hi[axis]-lo[axis])*i/count
        b[axis]=lo[axis]+(hi[axis]-lo[axis])*(i+1)/count
        points=np.array([transform(v,r) for v in vertices(a,b)])
        output.append([round(float(n),6) for n in list(points.min(0))+list(points.max(0))])
    return output

def java_element(e):
    result=dict(name=e['name'],**{'from':e['from'],'to':e['to']},
        faces={f:dict(uv=[v/(8 if i%2==0 else 4) for i,v in enumerate(face['uv'])],texture='#0') for f,face in e['faces'].items()})
    if native_rotation(e):result['rotation']=native_rotation(e)
    return result

def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')

texture_name='archecraft:block/stonemason_workbench'
tex={'0':texture_name,'particle':texture_name}
write(ASSETS/'models/block/stonemason_workbench.json',dict(parent='minecraft:block/block',texture_size=[128,64],textures=tex,
      elements=[java_element(e) for e in elements]))
display={
 'gui':dict(rotation=[25,225,0],translation=[0,-1,0],scale=[0.6]*3),
 'ground':dict(rotation=[0,0,0],translation=[0,3,0],scale=[0.25]*3),
 'fixed':dict(rotation=[0,0,0],translation=[0,0,0],scale=[0.5]*3),
 'thirdperson_righthand':dict(rotation=[75,45,0],translation=[0,2.5,0],scale=[0.375]*3),
 'firstperson_righthand':dict(rotation=[0,45,0],translation=[0,0,0],scale=[0.4]*3)}
write(ASSETS/'models/item/stonemason_workbench.json',dict(parent='archecraft:block/stonemason_workbench',display=display))
write(ASSETS/'blockstates/stonemason_workbench.json',dict(variants={
    f'facing={facing}':dict(model='archecraft:block/stonemason_workbench',y=angle)
    for facing,angle in [('north',0),('east',90),('south',180),('west',270)]}))
atlas.save(ASSETS/'textures/block/stonemason_workbench.png');atlas.save(HERE/'stonemason_workbench.png')
buf=io.BytesIO();atlas.save(buf,format='PNG')
groups=[dict(name=g,origin=[8,0,8],uuid=str(uuid.uuid5(uuid.NAMESPACE_URL,'stonemason-v2/'+g)),
        children=[e['uuid'] for p,e in zip(pieces,elements) if p['group']==g]) for g in dict.fromkeys(p['group'] for p in pieces)]
write(HERE/'stonemason_workbench.bbmodel',dict(meta=dict(format_version='4.10',model_format='java_block',box_uv=False),
      name='stonemason_workbench',resolution=dict(width=128,height=64),elements=elements,outliner=groups,display=display,
      textures=[dict(name='stonemason_workbench.png',uuid=str(uuid.uuid5(uuid.NAMESPACE_URL,texture_name)),id='0',namespace='archecraft',
        folder='block',width=128,height=64,uv_width=128,uv_height=64,mode='bitmap',saved=True,
        source='data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode())]))

model_bounds=[box for e in elements for box in collision_boxes(e)]
for b in model_bounds:
    assert 0<=b[0]<b[3]<=16 and 0<=b[2]<b[5]<=16 and 0<=b[1]<b[4]<=32,b
# Outline rendering visits the entire merged voxel grid every frame while targeted.
# Irrational coordinates from sliced, angled tools made that grid prohibitively large.
# Keep gameplay geometry to the three main masses; tools and chips remain visual details.
blue=next(e for e in elements if e['name']=='Blue mineral workpiece')
boxes=[
    [0.5,0,0.5,15.5,5.5,15.5],
    [2.5,5.5,2.5,13.5,10,13.5],
    blue['from']+blue['to'],
]
lines=['package com.redcookies.archecraft.workbench;','','import net.minecraft.core.Direction;',
 'import net.minecraft.world.level.block.Block;','import net.minecraft.world.phys.shapes.Shapes;',
 'import net.minecraft.world.phys.shapes.VoxelShape;','','// Generated by art/models/stonemason_workbench/build_model.py.',
 'final class StonemasonWorkbenchShapes {','    static VoxelShape[] create() {',
 '        VoxelShape[] shapes = new VoxelShape[4];','        double[][] boxes = {']
lines+=['            {'+', '.join(str(n) for n in b)+'},' for b in boxes]
lines+=['        };','        for (Direction facing : Direction.Plane.HORIZONTAL) {',
 '            VoxelShape shape = Shapes.empty();','            for (double[] box : boxes) {',
 '                double x0=box[0], z0=box[2], x1=box[3], z1=box[5];',
 '                for (int turn=0; turn < switch(facing) {case EAST -> 1; case SOUTH -> 2; case WEST -> 3; default -> 0;}; turn++) {',
 '                    double nx0=16-z1, nz0=x0, nx1=16-z0, nz1=x1;',
 '                    x0=nx0; z0=nz0; x1=nx1; z1=nz1;','                }',
 '                shape=Shapes.or(shape,Block.box(x0,box[1],z0,x1,box[4],z1));','            }',
 '            shapes[facing.get2DDataValue()]=shape.optimize();','        }','        return shapes;','    }','}']
(ROOT/'src/main/java/com/redcookies/archecraft/workbench/StonemasonWorkbenchShapes.java').write_text('\n'.join(lines)+'\n')

def render(angle):
    """Depth-buffered orthographic render of these exact rotated textured elements."""
    yaw,pitch=math.radians(angle),math.radians(25)
    camera=np.array([math.sin(yaw)*math.cos(pitch),math.sin(pitch),math.cos(yaw)*math.cos(pitch)])
    def project(v):
        x,y,z=v-[8,0,8];h=x*math.cos(yaw)-z*math.sin(yaw);f=x*math.sin(yaw)+z*math.cos(yaw)
        return [350+h*22,435-y*math.cos(pitch)*22+f*math.sin(pitch)*22,f*math.cos(pitch)+y*math.sin(pitch)]
    canvas=Image.new('RGB',(700,560),(27,33,38))
    ImageDraw.Draw(canvas).ellipse((115,375,585,525),fill=(19,24,28))
    pixels=np.array(canvas);depths=np.full((560,700),-np.inf);texture=np.array(atlas)[:,:,:3]
    def triangle(points,uv,shade):
        points=np.array(points)
        x0=max(0,int(math.floor(points[:,0].min())));x1=min(700,int(math.ceil(points[:,0].max())))
        y0=max(0,int(math.floor(points[:,1].min())));y1=min(560,int(math.ceil(points[:,1].max())))
        if x1<=x0 or y1<=y0:return
        a,b,c=points;divisor=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(divisor)<0.001:return
        xx,yy=np.meshgrid(np.arange(x0,x1)+0.5,np.arange(y0,y1)+0.5)
        wa=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/divisor
        wb=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/divisor
        wc=1-wa-wb;zz=wa*a[2]+wb*b[2]+wc*c[2];region=depths[y0:y1,x0:x1]
        mask=(wa>=-1e-8)&(wb>=-1e-8)&(wc>=-1e-8)&(zz>region);uv=np.array(uv)
        u=np.clip(np.floor(wa*uv[0,0]+wb*uv[1,0]+wc*uv[2,0]).astype(int),0,127)
        v=np.clip(np.floor(wa*uv[0,1]+wb*uv[1,1]+wc*uv[2,1]).astype(int),0,63)
        color=np.clip(texture[v,u]*shade,0,255).astype(np.uint8)
        pixels[y0:y1,x0:x1][mask]=color[mask];region[mask]=zz[mask]
    for e in elements:
        x0,y0,z0=e['from'];x1,y1,z1=e['to'];r=native_rotation(e)
        surfaces={
         'north':([(x1,y1,z0),(x0,y1,z0),(x0,y0,z0),(x1,y0,z0)],(0,0,-1)),
         'south':([(x0,y1,z1),(x1,y1,z1),(x1,y0,z1),(x0,y0,z1)],(0,0,1)),
         'east': ([(x1,y1,z1),(x1,y1,z0),(x1,y0,z0),(x1,y0,z1)],(1,0,0)),
         'west': ([(x0,y1,z0),(x0,y1,z1),(x0,y0,z1),(x0,y0,z0)],(-1,0,0)),
         'up': ([(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)],(0,1,0)),
         'down': ([(x0,y0,z1),(x1,y0,z1),(x1,y0,z0),(x0,y0,z0)],(0,-1,0))}
        for face,(verts,normal) in surfaces.items():
            n=transform(normal,r,normal=True)
            if np.dot(n,camera)<=0:continue
            points=[project(transform(v,r)) for v in verts]
            u0,v0,u1,v1=e['faces'][face]['uv'];uv=[(u0,v0),(u1,v0),(u1,v1),(u0,v1)]
            shade=0.76+max(0,n[1])*0.28+max(0,n[2])*0.1+max(0,-n[0])*0.07
            for inds in [(0,1,2),(0,2,3)]:triangle([points[i] for i in inds],[uv[i] for i in inds],shade)
    return Image.fromarray(pixels)

preview=Image.new('RGB',(1400,625),(27,33,38))
preview.paste(render(32),(0,45));preview.paste(render(212),(700,45))
d=ImageDraw.Draw(preview)
font=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',25);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16)
d.text((30,15),'STONEMASON WORKBENCH / rebuilt for one block',font=font,fill=(226,226,215))
d.text((30,590),'FRONT / 3-QUARTER',font=small,fill=(167,180,186))
d.text((730,590),'REVERSE / 3-QUARTER',font=small,fill=(167,180,186))
preview.save(HERE/'stonemason_workbench_preview.png')
print(f'Built {len(elements)} visual cuboids, {len(boxes)} gameplay boxes, original atlas, Java exports and editable model.')
