"""Original Archeum workbench model based on the supplied reference."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import base64, io, json, math, random, uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ASSETS = ROOT / 'src/main/resources/assets/archecraft'
rng = random.Random(914)
atlas = Image.new('RGBA', (128,64))
palette = [(104,82,55),(66,48,31),(124,99,68),(45,51,49),
           (132,235,245),(85,101,105),(87,220,183),(25,32,33)]
for tile,base in enumerate(palette):
    ox,oy=(tile%4)*32,(tile//4)*32
    for y in range(32):
        for x in range(32):
            n=rng.choice([-5,-2,0,0,2,4])
            if tile < 3: n += -8 if y%7 in (0,1) else 0
            if tile in (4,6): n += (x//4-y//8)%3*7
            atlas.putpixel((ox+x,oy+y),tuple(max(0,min(255,c+n)) for c in base)+(255,))
    d=ImageDraw.Draw(atlas)
    if tile < 3:
        for _ in range(18):
            x,y=rng.randrange(32),rng.randrange(32)
            d.line((ox+x,oy+y,ox+min(31,x+rng.randint(2,8)),oy+y),fill=tuple(max(0,c-18) for c in base)+(255,))
    if tile==3:
        # Small golden star/flower engravings on the weathered metal casing.
        for cx in range(4,32,8):
            for cy in range(4,32,8):
                d.line((ox+cx-2,oy+cy,ox+cx+2,oy+cy),fill=(165,143,82,255))
                d.line((ox+cx,oy+cy-2,ox+cx,oy+cy+2),fill=(165,143,82,255))
                d.point((ox+cx-1,oy+cy-1),fill=(120,108,65,255))
                d.point((ox+cx+1,oy+cy+1),fill=(120,108,65,255))

pieces=[]
def cube(name,lo,hi,tile,group='Frame'):
    pieces.append(dict(name=name,lo=list(lo),hi=list(hi),tile=tile,group=group))

for x,label in [(2,'left'),(27.5,'right')]:
    for z,side in [(2,'back'),(11.5,'front')]:
        cube(f'{label} {side} wooden leg',(x,0,z),(x+2.5,12.5,z+2.5),1)
        cube(f'{label} {side} foot',(x-0.25,0,z-0.25),(x+2.75,1,z+2.75),2)
cube('Front apron',(1,10.5,12),(31,12.5,14),0)
cube('Back apron',(1,10.5,2),(31,12.5,4),0)
cube('Left apron',(2,10.5,3),(4,12.5,13),1)
cube('Right apron',(28,10.5,3),(30,12.5,13),1)
cube('Lower stretcher',(3,3.5,7),(29,5,9),1)
for i in range(5):
    z=0.5+i*3
    cube(f'Weathered tabletop plank {i+1}',(0.5,12.5,z),(31.5,14,z+2.9),0 if i%2 else 2,'Tabletop')
cube('Left end cap',(0,12,0.5),(1,14,15.4),1,'Tabletop')
cube('Right end cap',(31,12,0.5),(32,14,15.4),1,'Tabletop')
for x in [2,29]:
    for z in [2,12.5]: cube('Iron tabletop nail',(x,14,z),(x+0.5,14.1,z+0.5),5,'Tabletop')

# The tall, dark hand-cranked Archeum processor on the left.
for x in [3,11]:
    for z in [3,10]: cube('Processor iron foot',(x,14,z),(x+1,16,z+1),7,'Processor')
cube('Processor base plate',(2,15.5,2),(14,16.5,12),7,'Processor')
cube('Engraved processor casing',(3,16.5,3),(13,23,11),3,'Processor')
cube('Processor upper lip',(2,23,2),(14,24,12),7,'Processor')
cube('Front brass panel edge',(3,16.5,11),(3.5,23,11.25),2,'Processor')
cube('Front brass panel edge',(12.5,16.5,11),(13,23,11.25),2,'Processor')
cube('Front brass lower trim',(3,16.5,11),(13,17,11.25),2,'Processor')
cube('Left brass trim',(3,17,3),(3.25,23,11),2,'Processor')
cube('Processor neck',(6,24,5),(10,25.5,9),7,'Hopper')
cube('Hopper lowest step',(5,25,4),(11,26,10),7,'Hopper')
cube('Hopper middle step',(3.5,26,2.5),(12.5,27,11.5),3,'Hopper')
cube('Hopper broad step',(2,27,1),(14,28,13),7,'Hopper')
cube('Hopper front rim',(1.5,28,12),(14.5,29,13.5),7,'Hopper')
cube('Hopper back rim',(1.5,28,0.5),(14.5,29,2),7,'Hopper')
cube('Hopper left rim',(1.5,28,2),(3,29,12),7,'Hopper')
cube('Hopper right rim',(13,28,2),(14.5,29,12),7,'Hopper')
cube('Crank vertical shaft',(7.5,28,6.5),(8.5,31.5,7.5),5,'Crank')
cube('Crank horizontal arm',(3,30.5,6.5),(8.5,31.5,7.5),7,'Crank')
cube('Crank wooden handle',(2.5,30,6),(3.75,32,8),2,'Crank')
cube('Front discharge spout',(7,17,11),(9,18.5,13),7,'Processor')

def crystal(name,x,y,z,w,h,d,tile):
    cube(name+' lower facet',(x,y,z),(x+w,y+h*0.65,z+d),tile,'Archeum crystals')
    cube(name+' upper facet',(x+w*0.15,y+h*0.65,z+d*0.15),(x+w*0.85,y+h*0.88,z+d*0.85),tile,'Archeum crystals')
    cube(name+' tip',(x+w*0.32,y+h*0.88,z+d*0.32),(x+w*0.68,y+h,z+d*0.68),tile,'Archeum crystals')

crystal('Large blue crystal',26,14,5,3.5,5,3,4)
crystal('Blue cluster branch',28.5,14,6.5,2,3,2,4)
crystal('Blue cluster branch',24.8,14,7,2,2.5,2,4)
crystal('Mint crystal',21,14,6.5,2.5,3.5,2.5,6)
crystal('Mint cluster branch',19.5,14,8,1.7,2,1.7,6)
crystal('Loose blue shard',16.5,14,4.5,1.3,1.7,1.1,4)
crystal('Loose blue shard',18,14,6,1.1,1.3,1.2,4)
crystal('Freshly processed shard',10.5,14,12,1.4,1.5,1.4,4)
crystal('Freshly processed shard',8.8,14,13,1.1,1.2,1.1,4)
cube('Tongs first arm',(20,14,11),(26,14.5,11.6),5,'Tools')
cube('Tongs second arm',(21,14,12),(26,14.5,12.6),5,'Tools')
cube('Tongs joint',(25,14,11),(26,14.7,12.6),7,'Tools')
cube('Small hammer handle',(26,14,13),(30,14.6,13.6),1,'Tools')
cube('Small hammer head',(26,14,12),(27.2,15.4,14.5),5,'Tools')

directions=['north','east','south','west','up','down']
def faces(p):
    dx,dy,dz=[b-a for a,b in zip(p['lo'],p['hi'])]
    ox,oy=(p['tile']%4)*32,(p['tile']//4)*32
    output={}
    for face in directions:
        w,h=(dx,dz) if face in ('up','down') else (dz,dy) if face in ('east','west') else (dx,dy)
        t=p['tile']
        x,y=(t%4)*32,(t//4)*32
        output[face]={'uv':[x,y,x+w,y+h],'texture':0}
    return output
elements=[]
for p in pieces:
    p['faces']=faces(p)
    p['uuid']=str(uuid.uuid5(uuid.NAMESPACE_URL,'archecraft:archeum/'+str(len(elements))+'/'+p['name']))
    elements.append({'name':p['name'],'type':'cube','uuid':p['uuid'],'from':p['lo'],'to':p['hi'],
                     'origin':[16,0,8],'box_uv':False,'autouv':0,'faces':p['faces']})
texture_name='archecraft:block/archeum_workbench'
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
    write(ASSETS/f'models/block/archeum_workbench_{label}.json',{
        'parent':'minecraft:block/block','texture_size':[128,64],'textures':tex,'elements':halves[i]})
display={
 'gui':{'rotation':[25,225,0],'translation':[0,-1,0],'scale':[0.48]*3},
 'ground':{'rotation':[0,0,0],'translation':[0,3,0],'scale':[0.2]*3},
 'fixed':{'rotation':[0,0,0],'translation':[0,0,0],'scale':[0.4]*3},
 'thirdperson_righthand':{'rotation':[75,45,0],'translation':[0,2.5,0],'scale':[0.3]*3},
 'firstperson_righthand':{'rotation':[0,45,0],'translation':[0,0,0],'scale':[0.35]*3}}
write(ASSETS/'models/item/archeum_workbench.json',{'parent':'minecraft:block/block','textures':tex,
       'elements':[java_element(e,shift=8) for e in elements],'display':display})
variants={}
# The authoring front is south; keep the source halves aligned when facing the player.
for facing,rotation in [('north',0),('east',90),('south',180),('west',270)]:
    for part in ['left','right']:
        source_part='right' if part=='left' else 'left'
        variants[f'facing={facing},part={part}']={'model':f'archecraft:block/archeum_workbench_{source_part}','y':(rotation+180)%360}
write(ASSETS/'blockstates/archeum_workbench.json',{'variants':variants})
(ASSETS/'textures/block').mkdir(parents=True,exist_ok=True)
atlas.save(ASSETS/'textures/block/archeum_workbench.png');atlas.save(HERE/'archeum_workbench.png')
buf=io.BytesIO();atlas.save(buf,format='PNG')
groups=[]
for group in dict.fromkeys(p['group'] for p in pieces):
    groups.append({'name':group,'origin':[16,0,8],'uuid':str(uuid.uuid5(uuid.NAMESPACE_URL,group)),
                   'children':[p['uuid'] for p in pieces if p['group']==group]})
write(HERE/'archeum_workbench.bbmodel',{'meta':{'format_version':'4.10','model_format':'java_block','box_uv':False},
 'name':'archeum_workbench','resolution':{'width':128,'height':64},'elements':elements,'outliner':groups,
 'textures':[{'name':'archeum_workbench.png','uuid':str(uuid.uuid5(uuid.NAMESPACE_URL,texture_name)),'id':'0','namespace':'archecraft','folder':'block',
              'width':128,'height':64,'uv_width':128,'uv_height':64,'mode':'bitmap','saved':True,
              'source':'data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode()}],'display':display})

# Generate collision and selection boxes from the actual split model.
lines=['package com.redcookies.archecraft.workbench;','','import net.minecraft.core.Direction;',
       'import net.minecraft.world.level.block.Block;','import net.minecraft.world.phys.shapes.Shapes;',
       'import net.minecraft.world.phys.shapes.VoxelShape;','','// Generated by art/models/archeum_workbench/build_model.py.',
       'final class ArcheumWorkbenchShapes {','    static VoxelShape[][] create() {',
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
shape_path=ROOT/'src/main/java/com/redcookies/archecraft/workbench/ArcheumWorkbenchShapes.java'
shape_path.write_text('\n'.join(lines)+'\n',encoding='utf-8')

# Preview these exact textured cuboids from front and reverse angles.
def render(angle):
    yaw,pitch=math.radians(angle),math.radians(26)
    def project(p):
        x,y,z=p[0]-16,p[1],p[2]-8
        h=x*math.cos(yaw)-z*math.sin(yaw);f=x*math.sin(yaw)+z*math.cos(yaw)
        return (350+h*15,510-y*math.cos(pitch)*15+f*math.sin(pitch)*15,f*math.cos(pitch)+y*math.sin(pitch))
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
    canvas=Image.new('RGB',(700,650),(27,33,38));d=ImageDraw.Draw(canvas)
    d.ellipse((75,465,625,625),fill=(20,25,28))
    for _,pts,c in sorted(quads,key=lambda q:q[0]):d.polygon(pts,fill=c)
    return canvas
preview=Image.new('RGB',(1400,710),(27,33,38))
preview.paste(render(32),(0,45));preview.paste(render(212),(700,45))
d=ImageDraw.Draw(preview)
font=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',25)
small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16)
d.text((30,15),'ARCHEUM WORKBENCH / two-block model',font=font,fill=(226,226,215))
d.text((30,680),'3-QUARTER VIEW',font=small,fill=(167,180,186))
d.text((730,680),'REVERSE VIEW',font=small,fill=(167,180,186))
preview.save(HERE/'archeum_workbench_preview.png')
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
