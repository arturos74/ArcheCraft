"""Original two-block carpenter bench: editable project, split Java models and shapes."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import base64, io, json, math, random, uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ASSETS = ROOT / 'src/main/resources/assets/archecraft'
rng = random.Random(813)
atlas = Image.new('RGBA', (128,64))
palette = [(103,81,55),(69,53,37),(132,107,74),(98,78,54),
           (35,133,150),(64,76,76),(133,101,59),(45,39,30)]
for tile,base in enumerate(palette):
    ox,oy=(tile%4)*32,(tile//4)*32
    for y in range(32):
        for x in range(32):
            grain = rng.choice([-7,-3,0,0,2,5,8])
            if tile not in (3,5):
                grain += -8 if y%7 in (0,1) else 0
            else:
                grain += int(math.sin(math.hypot(x-14,y-17)*1.8)*7) if tile==3 else 0
            atlas.putpixel((ox+x,oy+y),tuple(max(0,min(255,c+grain)) for c in base)+(255,))
    d=ImageDraw.Draw(atlas)
    for _ in range(18):
        x,y=rng.randrange(32),rng.randrange(32)
        shade=tuple(max(0,c-18) for c in base)+(255,)
        d.line((ox+x,oy+y,ox+min(31,x+rng.randint(2,8)),oy+y),fill=shade)
    if tile==4:
        for _ in range(24):
            x,y=rng.randrange(32),rng.randrange(32)
            d.rectangle((ox+x,oy+y,ox+min(31,x+1),oy+min(31,y+1)),fill=(115,101,70,255))

pieces=[]
def cube(name,lo,hi,tile,group='Frame'):
    pieces.append(dict(name=name,lo=list(lo),hi=list(hi),tile=tile,group=group))

# Authoring model: 32 units wide, 16 deep, with its front toward south (+Z).
for x,label in [(2,'left'),(27.5,'right')]:
    for z,side in [(2,'back'),(11.5,'front')]:
        cube(f'{label} {side} leg',(x,0,z),(x+2.5,12,z+2.5),1)
        cube(f'{label} {side} foot',(x-0.3,0,z-0.3),(x+2.8,1.5,z+2.8),2)
cube('Front apron',(1,10,12),(31,12.5,14),1)
cube('Back apron',(1,10,2),(31,12.5,4),1)
cube('Left apron',(2,10,3),(4,12.5,13),1)
cube('Right apron',(28,10,3),(30,12.5,13),1)
for z in [2.7,5.3,7.9,10.5]:
    cube('Lower shelf plank',(3,2,z),(29,3.5,z+2.5),0,'Shelf')
cube('Shelf front lip',(3,2,13),(29,4.5,14),2,'Shelf')
cube('Shelf left support',(3,1.5,3),(5,2,14),1,'Shelf')
cube('Shelf right support',(27,1.5,3),(29,2,14),1,'Shelf')
for i in range(5):
    z=0.5+i*3
    cube(f'Tabletop plank {i+1}',(0.5,12.5,z),(31.5,14,z+2.9),0 if i%2 else 2,'Tabletop')
cube('Left end cap',(0,12,0.5),(1,14,15.4),1,'Tabletop')
cube('Right end cap',(31,12,0.5),(32,14,15.4),1,'Tabletop')
for x in [2,29]:
    for z in [2,12.5]:
        cube('Iron nail',(x,14,z),(x+0.5,14.1,z+0.5),5,'Tabletop')

# Blue-painted stool on the tabletop, with worn wood showing at the feet.
for x in [15.5,21.5]:
    for z in [3.5,9.5]:
        cube('Stool wooden foot',(x,14,z),(x+1,16,z+1),2,'Blue stool')
        cube('Stool painted leg',(x,16,z),(x+1,21,z+1),4,'Blue stool')
cube('Stool left rail',(15.5,17,4.5),(16.5,17.8,9.5),4,'Blue stool')
cube('Stool right rail',(21.5,17,4.5),(22.5,17.8,9.5),4,'Blue stool')
cube('Stool front rail',(16.5,18,9.5),(21.5,18.8,10.5),4,'Blue stool')
cube('Stool seat left',(15,21,3),(19,22,11),4,'Blue stool')
cube('Stool seat right',(19.1,21,3),(23,22,11),4,'Blue stool')

# A hand plane, hammer, saw, chisel and loose timber evoke the reference.
cube('Plane body',(3,14,3),(9,15.1,6),0,'Tools')
cube('Plane sole',(3,14,3),(9,14.2,6),5,'Tools')
cube('Plane blade',(5.5,15.1,3.5),(6.2,16.3,5.5),5,'Tools')
cube('Plane rear handle',(7,15.1,3.8),(8,16.5,5.2),1,'Tools')
cube('Hammer handle',(8,14,10),(15,14.6,10.7),6,'Tools')
cube('Hammer iron head',(8,14,9),(9.5,15.2,12),5,'Tools')
cube('Saw blade',(23,14,7),(29,14.35,9),5,'Tools')
for x in range(23,29):
    cube('Saw tooth',(x,14,9),(x+0.5,14.35,9.5),5,'Tools')
cube('Saw grip top',(29,14,7),(31,15,7.5),6,'Tools')
cube('Saw grip bottom',(29,14,9),(31,15,9.5),6,'Tools')
cube('Saw grip end',(30.5,14,7.5),(31,15,9),6,'Tools')
cube('Chisel grip',(11,14,4),(13.5,14.8,4.8),1,'Tools')
cube('Chisel blade',(13.5,14,4.1),(15,14.4,4.7),5,'Tools')
cube('Top loose board',(19,14,12),(28,14.8,14),6,'Loose boards')
cube('Top short offcut',(23,14.8,12.4),(28,15.4,13.8),0,'Loose boards')
cube('Shelf board one',(7,3.5,6),(21,4.2,8),6,'Loose boards')
cube('Shelf board two',(11,4.2,7),(26,5,9),2,'Loose boards')
cube('Shelf short offcut',(5,3.5,10),(13,4.5,12),0,'Loose boards')
# A small vise built into the left end.
cube('Vise fixed jaw',(0,11,5),(2,15.4,8),1,'Tools')
cube('Vise outer jaw',(0,10,8.5),(2,14.8,10),2,'Tools')
cube('Vise iron screw',(0.5,11.5,7),(1.2,12.2,11),5,'Tools')

directions=['north','east','south','west','up','down']
def faces(p):
    dx,dy,dz=[b-a for a,b in zip(p['lo'],p['hi'])]
    ox,oy=(p['tile']%4)*32,(p['tile']//4)*32
    output={}
    for face in directions:
        w,h=(dx,dz) if face in ('up','down') else (dz,dy) if face in ('east','west') else (dx,dy)
        t=3 if face=='down' and p['group']=='Frame' else p['tile']
        x,y=(t%4)*32,(t//4)*32
        output[face]={'uv':[x,y,x+w,y+h],'texture':0}
    return output
elements=[]
for p in pieces:
    p['faces']=faces(p)
    p['uuid']=str(uuid.uuid5(uuid.NAMESPACE_URL,'archecraft:carpenter/'+str(len(elements))+'/'+p['name']))
    elements.append({'name':p['name'],'type':'cube','uuid':p['uuid'],'from':p['lo'],'to':p['hi'],
                     'origin':[16,0,8],'box_uv':False,'autouv':0,'faces':p['faces']})
texture_name='archecraft:block/carpenter_workbench'
def java_element(e,lo=None,hi=None,shift=0):
    lo=list(lo or e['from']);hi=list(hi or e['to']);lo[0]-=shift;hi[0]-=shift
    fs={f:{'uv':[v/8 if i%2==0 else v/4 for i,v in enumerate(data['uv'])],'texture':'#0'} for f,data in e['faces'].items()}
    return {'name':e['name'],'from':lo,'to':hi,'faces':fs}

halves=[[],[]]
for e in elements:
    for half in range(2):
        a,b=max(e['from'][0],half*16),min(e['to'][0],(half+1)*16)
        if a>=b:continue
        lo=e['from'].copy();hi=e['to'].copy();lo[0]=a;hi[0]=b
        cropped=json.loads(json.dumps(e))
        # Crop the UVs of faces split across the two blocks, maintaining texture density.
        for f in ['north','south','up','down']:
            uv=cropped['faces'][f]['uv']
            offset=e['to'][0]-b if f=='north' else a-e['from'][0]
            uv[0]+=offset;uv[2]=uv[0]+b-a
        halves[half].append(java_element(cropped,lo,hi,half*16))

def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
tex={'0':texture_name,'particle':texture_name}
for i,label in enumerate(['left','right']):
    write(ASSETS/f'models/block/carpenter_workbench_{label}.json',{
        'parent':'minecraft:block/block','texture_size':[128,64],'textures':tex,'elements':halves[i]})
display={
 'gui':{'rotation':[25,225,0],'translation':[0,-1,0],'scale':[0.48]*3},
 'ground':{'rotation':[0,0,0],'translation':[0,3,0],'scale':[0.2]*3},
 'fixed':{'rotation':[0,0,0],'translation':[0,0,0],'scale':[0.4]*3},
 'thirdperson_righthand':{'rotation':[75,45,0],'translation':[0,2.5,0],'scale':[0.3]*3},
 'firstperson_righthand':{'rotation':[0,45,0],'translation':[0,0,0],'scale':[0.35]*3}}
write(ASSETS/'models/item/carpenter_workbench.json',{'parent':'minecraft:block/block','textures':tex,
       'elements':[java_element(e,shift=8) for e in elements],'display':display})
variants={}
# The authoring front is south; keep the source halves aligned when facing the player.
for facing,rotation in [('north',0),('east',90),('south',180),('west',270)]:
    for part in ['left','right']:
        source_part='right' if part=='left' else 'left'
        variants[f'facing={facing},part={part}']={'model':f'archecraft:block/carpenter_workbench_{source_part}','y':(rotation+180)%360}
write(ASSETS/'blockstates/carpenter_workbench.json',{'variants':variants})
(ASSETS/'textures/block').mkdir(parents=True,exist_ok=True)
atlas.save(ASSETS/'textures/block/carpenter_workbench.png');atlas.save(HERE/'carpenter_workbench.png')
buf=io.BytesIO();atlas.save(buf,format='PNG')
groups=[]
for group in dict.fromkeys(p['group'] for p in pieces):
    groups.append({'name':group,'origin':[16,0,8],'uuid':str(uuid.uuid5(uuid.NAMESPACE_URL,group)),
                   'children':[p['uuid'] for p in pieces if p['group']==group]})
write(HERE/'carpenter_workbench.bbmodel',{'meta':{'format_version':'4.10','model_format':'java_block','box_uv':False},
 'name':'carpenter_workbench','resolution':{'width':128,'height':64},'elements':elements,'outliner':groups,
 'textures':[{'name':'carpenter_workbench.png','uuid':str(uuid.uuid5(uuid.NAMESPACE_URL,texture_name)),'id':'0','namespace':'archecraft','folder':'block',
              'width':128,'height':64,'uv_width':128,'uv_height':64,'mode':'bitmap','saved':True,
              'source':'data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode()}],'display':display})

# Generate collision and selection boxes from the actual split model.
lines=['package com.redcookies.archecraft.workbench;','','import net.minecraft.core.Direction;',
       'import net.minecraft.world.level.block.Block;','import net.minecraft.world.phys.shapes.Shapes;',
       'import net.minecraft.world.phys.shapes.VoxelShape;','','// Generated by art/models/carpenter_workbench/build_model.py.',
       'final class CarpenterWorkbenchShapes {','    static VoxelShape[][] create() {',
       '        VoxelShape[][] shapes = new VoxelShape[2][4];']
for h in range(2):
    lines.append(f'        double[][] half{h} = {{')
    for e in halves[h]:lines.append('            {'+', '.join(str(x) for x in e['from']+e['to'])+'},')
    lines.append('        };')
lines += ['        double[][][] halves = {half0, half1};','        for (int half = 0; half < 2; half++) {',
          '            for (Direction facing : Direction.Plane.HORIZONTAL) {',
          '                VoxelShape shape = Shapes.empty();','                for (double[] box : halves[half]) {',
          '                    double x0 = box[0], z0 = box[2], x1 = box[3], z1 = box[5];',
          '                    for (int turn = 0; turn < switch (facing) { case EAST -> 1; case SOUTH -> 2; case WEST -> 3; default -> 0; }; turn++) {',
          '                        double nx0 = 16 - z1, nz0 = x0, nx1 = 16 - z0, nz1 = x1;',
          '                        x0 = nx0; z0 = nz0; x1 = nx1; z1 = nz1;','                    }',
          '                    shape = Shapes.or(shape, Block.box(x0, box[1], z0, x1, box[4], z1));','                }',
          '                shapes[half][facing.get2DDataValue()] = shape.optimize();','            }','        }',
          '        return shapes;','    }','}']
shape_path=ROOT/'src/main/java/com/redcookies/archecraft/workbench/CarpenterWorkbenchShapes.java'
shape_path.write_text('\n'.join(lines)+'\n',encoding='utf-8')

# Preview these exact textured cuboids from front and reverse angles.
def render(angle):
    yaw,pitch=math.radians(angle),math.radians(26)
    def project(p):
        x,y,z=p[0]-16,p[1],p[2]-8
        h=x*math.cos(yaw)-z*math.sin(yaw);f=x*math.sin(yaw)+z*math.cos(yaw)
        return (350+h*16,455-y*math.cos(pitch)*16+f*math.sin(pitch)*16,f*math.cos(pitch)+y*math.sin(pitch))
    quads=[]
    for e in elements:
        x0,y0,z0=e['from'];x1,y1,z1=e['to']
        surfaces={
         'north':([(x1,y1,z0),(x0,y1,z0),(x0,y0,z0),(x1,y0,z0)],(0,0,-1),0.82),
         'south':([(x0,y1,z1),(x1,y1,z1),(x1,y0,z1),(x0,y0,z1)],(0,0,1),0.9),
         'east': ([(x1,y1,z1),(x1,y1,z0),(x1,y0,z0),(x1,y0,z1)],(1,0,0),0.8),
         'west': ([(x0,y1,z0),(x0,y1,z1),(x0,y0,z1),(x0,y0,z0)],(-1,0,0),0.88),
         'up':   ([(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)],(0,1,0),1.15)}
        camera=(math.sin(yaw)*math.cos(pitch),math.sin(pitch),math.cos(yaw)*math.cos(pitch))
        for face,(v,normal,shade) in surfaces.items():
            if sum(a*b for a,b in zip(normal,camera))<=0:continue
            uv=e['faces'][face]['uv'];w=max(1,math.ceil(uv[2]-uv[0]));h=max(1,math.ceil(uv[3]-uv[1]))
            for py in range(h):
                for px in range(w):
                    pts=[]
                    for u,t in [(px/w,py/h),((px+1)/w,py/h),((px+1)/w,(py+1)/h),(px/w,(py+1)/h)]:
                        pts.append(project([v[0][k]+u*(v[1][k]-v[0][k])+t*(v[3][k]-v[0][k]) for k in range(3)]))
                    c=atlas.getpixel((int(uv[0]+px/w*(uv[2]-uv[0])),int(uv[1]+py/h*(uv[3]-uv[1]))))
                    quads.append((sum(p[2] for p in pts)/4,[(p[0],p[1]) for p in pts],tuple(min(255,int(c0*shade)) for c0 in c[:3])))
    canvas=Image.new('RGB',(700,560),(27,33,38));d=ImageDraw.Draw(canvas)
    d.ellipse((75,385,625,525),fill=(20,25,28))
    for _,pts,c in sorted(quads,key=lambda q:q[0]):d.polygon(pts,fill=c)
    return canvas
preview=Image.new('RGB',(1400,625),(27,33,38))
preview.paste(render(32),(0,45));preview.paste(render(212),(700,45))
d=ImageDraw.Draw(preview)
font=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',25)
small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16)
d.text((30,15),'CARPENTER WORKBENCH / two-block model',font=font,fill=(226,226,215))
d.text((30,590),'3-QUARTER VIEW',font=small,fill=(167,180,186))
d.text((730,590),'REVERSE VIEW',font=small,fill=(167,180,186))
preview.save(HERE/'carpenter_workbench_preview.png')
assert len(variants)==8
for h in halves:
    for e in h:
        assert 0<=e['from'][0]<e['to'][0]<=16
        assert 0<=e['from'][2]<e['to'][2]<=16
        assert 0<=e['from'][1]<e['to'][1]<=32
full_volume=sum(math.prod(b-a for a,b in zip(e['from'],e['to'])) for e in elements)
split_volume=sum(math.prod(b-a for a,b in zip(e['from'],e['to'])) for h in halves for e in h)
assert abs(full_volume-split_volume)<0.001
print(f'Created {len(elements)} cuboids, two block models, full item model, editable project, texture, collision shapes, and preview.')
