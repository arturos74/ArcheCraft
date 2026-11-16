"""Animation-ready, horse-scale Yata base with an original editable pixel atlas.

16 model units = 1 block. Blockbench front is -Z; positive Y points upward.
Only authoring assets are produced: no entity registration or mount behavior.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import base64, copy, io, json, math, random, uuid
import numpy as np

HERE=Path(__file__).resolve().parent
SCALE=0.85
TEX_SIZE=256
bones={}
cubes=[]

def uid(name):return str(uuid.uuid5(uuid.NAMESPACE_URL,'archecraft/yata/'+name))
def write(path,data):path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
def bone(name,pivot,parent='root',rotation=(0,0,0)):
    bones[name]=dict(name=name,origin=list(pivot),rotation=list(rotation),parent=parent,uuid=uid('bone/'+name))
def cube(name,lo,hi,material,parent):
    assert all(b>a for a,b in zip(lo,hi)),name
    cubes.append(dict(name=name,type='cube',uuid=uid('cube/'+name),**{'from':list(lo),'to':list(hi)},
        origin=list(bones[parent]['origin']),rotation=[0,0,0],box_uv=False,autouv=0,
        _material=material,_bone=parent,faces={}))

bone('root',(0,0,0),None)
bone('body',(0,20,5))
bone('chest',(0,24,-3),'body')
bone('neck',(0,29,-7),'chest')
bone('head',(0,35,-11),'neck')
bone('jaw',(0,34,-14),'head')
bone('ear_left',(-2.7,38,-9),'head',(-12,0,25))
bone('ear_right',(2.7,38,-9),'head',(-12,0,-25))
bone('ear_left_tip',(-2.7,46,-8.9),'ear_left')
bone('ear_right_tip',(2.7,46,-8.9),'ear_right')
bone('tail_base',(0,18,16),'body',(8,0,0))
bone('tail_mid',(0,16,24),'tail_base',(-8,0,0))
bone('tail_tip',(0,15,32),'tail_mid',(-15,0,0))
bone('rider_seat',(0,27.5,5),'body')
bone('lead_anchor',(0,35,-20),'head')

cube('Rounded haunch core',(-6,13,1),(6,25,16),'fur','body')
cube('Lower belly',(-5,13,-4),(5,23,5),'cream','body')
cube('Back and shoulders',(-5.5,22,-5),(5.5,26,12),'fur','body')
cube('Chest',(-4.8,22,-9),(4.8,31,0),'fur','chest')
cube('Cream chest bib',(-3.8,20,-9.2),(3.8,29,-8.7),'cream','chest')
cube('Long upright neck',(-3,29,-12),(3,36,-5),'fur','neck')
cube('Throat',(-2.6,29,-12.2),(2.6,35,-11.8),'cream','neck')
cube('Head',(-4,33.5,-15),(4,39,-7),'fur','head')
cube('Long muzzle',(-3,33.5,-20),(3,37.5,-14),'cream','head')
cube('Soft nose',(-2.8,35.7,-20.25),(2.8,37.2,-19.8),'nose','head')
cube('Lower jaw',(-2.7,32.8,-19.5),(2.7,34.4,-12.5),'cream','jaw')
for side,x in [('left',-4.12),('right',4)]:
    cube(side+' eye socket',(x,36.5,-13),(x+0.12,37.9,-10.9),'eyelid','head')
    outer=x-0.06 if side=='left' else x+0.12
    cube(side+' dark eye',(outer,36.8,-12.65),(outer+0.06,37.7,-11.3),'eye','head')
    shine=outer-0.02 if side=='left' else outer+0.06
    cube(side+' eye glint',(shine,37.35,-12.45),(shine+0.02,37.65,-12.1),'white','head')

for side,center in [('left',-2.7),('right',2.7)]:
    b='ear_'+side;tip=b+'_tip'
    cube(side+' ear stem',(center-1.4,38,-9.8),(center+1.4,42,-8),'fur',b)
    # Matching shell/lining boundaries meet at the hinge. Only the upper section
    # follows the new tip bone, so the ear can bend without turning at its root.
    cube(side+' broad ear',(center-3.2,41,-9.8),(center+3.2,46,-8),'fur',b)
    cube(side+' ear upper panel',(center-3.2,46,-9.8),(center+3.2,49,-8),'fur',tip)
    cube(side+' ear taper',(center-2.5,49,-9.6),(center+2.5,52,-8.1),'fur',tip)
    cube(side+' ear tip',(center-1.5,52,-9.4),(center+1.5,53.5,-8.2),'fur',tip)
    cube(side+' inner ear',(center-2.25,42,-9.95),(center+2.25,46,-9.8),'inner',b)
    cube(side+' inner ear upper panel',(center-2.25,46,-9.95),(center+2.25,48.7,-9.8),'inner',tip)
    cube(side+' inner ear taper',(center-1.6,48.7,-9.8),(center+1.6,51.2,-9.6),'inner',tip)

for side,x in [('left',-5.2),('right',5.2)]:
    thigh=side+'_thigh';shin=side+'_shin';foot=side+'_foot'
    # Keep the original torso/sole heights while giving the lower leg a clear
    # backward slope. The foot counter-rotates to stay flat and point forward.
    old_ankle_y=21-10*math.cos(math.radians(20))-8.2*math.cos(math.radians(22))
    knee_y=21-10*math.cos(math.radians(32))
    foot_y=11-(knee_y-old_ankle_y)/math.cos(math.radians(40))
    drop=foot_y-2.8
    bone(thigh,(x,21,8),rotation=(32,0,0))
    bone(shin,(x,11,8),thigh,(-72,0,0))
    bone(foot,(x,foot_y,8),shin,(40,0,0))
    cube(side+' powerful upper thigh',(x-3.8,12,4),(x+3.8,22,13),'fur',thigh)
    cube(side+' knee',(x-2.8,10,5),(x+2.8,14,11),'fur',thigh)
    cube(side+' lower leg',(x-1.9,3+drop,6),(x+1.9,11,10),'foot',shin)
    cube(side+' ankle',(x-2.2,1.5+drop,6),(x+2.2,4+drop,10.5),'foot',foot)
    cube(side+' broad hind foot',(x-3,0.5+drop,1),(x+3,2.7+drop,10.5),'foot',foot)
    for i,dx in enumerate([-2,0,2]):
        front=0 if i==1 else 0.8
        cube(side+f' toe {i+1}',(x+dx-0.85,drop,front),(x+dx+0.85,1.9+drop,4),'foot',foot)
        cube(side+f' claw {i+1}',(x+dx-0.6,0.15+drop,front-0.5),(x+dx+0.6,1.2+drop,front+0.8),'claw',foot)

for side,x in [('left',-4.8),('right',4.8)]:
    upper=side+'_upper_arm';lower=side+'_forearm';hand=side+'_hand'
    bone(upper,(x,28,-6),'chest',(22,0,0))
    bone(lower,(x,22,-6),upper,(65,0,0))
    bone(hand,(x,18,-6),lower,(-35,0,0))
    cube(side+' small upper arm',(x-2.1,22,-7.4),(x+2.1,28,-4.6),'fur',upper)
    cube(side+' forearm',(x-1.65,18,-7.1),(x+1.65,22,-4.9),'fur',lower)
    cube(side+' paw',(x-1.875,16.5,-7.2),(x+1.875,18.5,-4.8),'foot',hand)
    cube(side+' little claws',(x-1.5,16,-7.3),(x+1.5,16.6,-5.5),'claw',hand)

cube('Thick tail root',(-3.5,14,15),(3.5,20,24.5),'fur','tail_base')
cube('Tapered tail middle',(-2.6,13.5,24),(2.6,18.5,33),'fur','tail_mid')
cube('Tail tip stem',(-1.7,13.5,32),(1.7,17,38),'fur','tail_tip')
cube('Pale tail brush',(-2.6,13,36),(2.6,18.2,40),'cream','tail_tip')
cube('Tail brush taper',(-1.9,13.8,40),(1.9,17.7,42.5),'cream','tail_tip')

def rotation_matrix(angles):
    x,y,z=np.radians(angles)
    rx=np.array([[1,0,0],[0,math.cos(x),-math.sin(x)],[0,math.sin(x),math.cos(x)]])
    ry=np.array([[math.cos(y),0,math.sin(y)],[0,1,0],[-math.sin(y),0,math.cos(y)]])
    rz=np.array([[math.cos(z),-math.sin(z),0],[math.sin(z),math.cos(z),0],[0,0,1]])
    return rz@ry@rx

def transform(point,name,normal=False):
    point=np.array(point,dtype=float)
    while name:
        b=bones[name];p=np.zeros(3) if normal else np.array(b['origin'])
        point=rotation_matrix(b['rotation'])@(point-p)+p;name=b['parent']
    return point

def vertices(e):
    return np.array([transform([x,y,z],e['_bone']) for x in (e['from'][0],e['to'][0])
        for y in (e['from'][1],e['to'][1]) for z in (e['from'][2],e['to'][2])])

floor=min(vertices(e)[:,1].min() for e in cubes)
def scaled(point):return [round(v*SCALE,5) for v in [point[0],point[1]-floor,point[2]]]
for b in bones.values():b['origin']=scaled(b['origin']) if b['name']!='root' else [0,0,0]
for e in cubes:
    e['from']=scaled(e['from']);e['to']=scaled(e['to']);e['origin']=list(bones[e['_bone']]['origin'])

# Each face has its own painted rectangle, with a padded non-overlapping layout.
faces=[]
for e in cubes:
    dx,dy,dz=np.array(e['to'])-e['from']
    for face in ['north','east','south','west','up','down']:
        width,height=(dx,dz) if face in ('up','down') else (dz,dy) if face in ('east','west') else (dx,dy)
        faces.append((e,face,max(1,math.ceil(width)),max(1,math.ceil(height))))
atlas=Image.new('RGBA',(TEX_SIZE,TEX_SIZE),(0,0,0,0))
# Muted brown/taupe coat, gray-beige underside and dark toes from the new reference.
# Keep the palette in the native UV painter so future model rebuilds retain it.
palette={'fur':(133,108,77),'cream':(192,173,154),'inner':(146,128,108),'foot':(169,156,139),
    'claw':(24,26,22),'nose':(48,47,38),'eye':(20,22,18),'white':(158,159,146),'eyelid':(129,113,92)}
rng=random.Random(8117)
x=y=2;row_height=0
uv_layout=[]
for e,face,w,h in sorted(faces,key=lambda f:-f[3]):
    if x+w+2>TEX_SIZE:x=2;y+=row_height+2;row_height=0
    assert y+h+2<=TEX_SIZE,'Atlas full'
    e['faces'][face]=dict(uv=[x,y,x+w,y+h],texture=0)
    uv_layout.append(dict(cube=e['name'],face=face,material=e['_material'],uv=[x,y,x+w,y+h]))
    base=palette[e['_material']]
    # Broad pixel patches echo the supplied skin rather than orange fur grain.
    patches={(gx,gy):rng.choice([-12,-7,0,0,4,8])
        for gx in range((w+2)//3) for gy in range((h+2)//3)}
    for py in range(h):
        for px in range(w):
            n=rng.choice([-3,-1,0,0,1,3])
            if e['_material'] in ('fur','cream','foot','inner'):n+=patches[(px//3,py//3)]
            if e['_material'] in ('fur','cream','inner'):
                n+=round((0.5-py/max(1,h-1))*9)
                if (px*3+py+len(e['name']))%11==0:n-=7
            if face=='up':n+=5
            if face=='down':n-=7
            atlas.putpixel((x+px,y+py),tuple(max(0,min(255,c+n)) for c in base)+(255,))
    # One-pixel extrusion prevents visible seams without sharing UV islands.
    for px in range(w):
        atlas.putpixel((x+px,y-1),atlas.getpixel((x+px,y)))
        atlas.putpixel((x+px,y+h),atlas.getpixel((x+px,y+h-1)))
    for py in range(h):
        atlas.putpixel((x-1,y+py),atlas.getpixel((x,y+py)))
        atlas.putpixel((x+w,y+py),atlas.getpixel((x+w-1,y+py)))
    x+=w+2;row_height=max(row_height,h)
atlas.save(HERE/'yata.png')
write(HERE/'yata_uv_layout.json',uv_layout)

def outliner(name):
    b=bones[name]
    return dict(name=name,origin=b['origin'],rotation=b['rotation'],uuid=b['uuid'],export=True,isOpen=False,
        children=[e['uuid'] for e in cubes if e['_bone']==name]+[outliner(n) for n,c in bones.items() if c['parent']==name])

png=io.BytesIO();atlas.save(png,format='PNG')
clips=[('idle',1.5),('walk',0.8),('hop',0.8),('ridden_idle',1.5)]
project=dict(meta=dict(format_version='4.10',model_format='bedrock',box_uv=False),
    name='yata',model_identifier='archecraft.yata',visible_box=[5,4,1.5],resolution=dict(width=TEX_SIZE,height=TEX_SIZE),
    elements=[{k:v for k,v in e.items() if not k.startswith('_')} for e in cubes],outliner=[outliner('root')],
    textures=[dict(name='yata.png',uuid=uid('texture'),id='0',width=TEX_SIZE,height=TEX_SIZE,
        uv_width=TEX_SIZE,uv_height=TEX_SIZE,mode='bitmap',saved=True,
        source='data:image/png;base64,'+base64.b64encode(png.getvalue()).decode())],
    animations=[dict(uuid=uid('animation/'+name),name='animation.yata.'+name,loop='once' if name=='hop' else 'loop',
        override=False,length=length,snapping=20,animators={}) for name,length in clips])
write(HERE/'yata.bbmodel',project)

# Match the official Blockbench Bedrock export: mirror X and negate X/Y angles.
geo_bones=[]
for name,b in bones.items():
    record=dict(name=name,pivot=[-b['origin'][0],b['origin'][1],b['origin'][2]])
    if b['parent']:record['parent']=b['parent']
    if any(b['rotation']):record['rotation']=[-b['rotation'][0],-b['rotation'][1],b['rotation'][2]]
    parts=[]
    for e in cubes:
        if e['_bone']!=name:continue
        lo,hi=e['from'],e['to'];uv={}
        for face,f in e['faces'].items():
            u,v,u1,v1=f['uv']
            uv[face]=dict(uv=[u1,v1],uv_size=[u-u1,v-v1]) if face in ('up','down') else dict(uv=[u,v],uv_size=[u1-u,v1-v])
        parts.append(dict(origin=[-hi[0],lo[1],lo[2]],size=[round(c-a,5) for a,c in zip(lo,hi)],uv=uv))
    if parts:record['cubes']=parts
    geo_bones.append(record)
write(HERE/'yata.geo.json',{'format_version':'1.12.0','minecraft:geometry':[dict(description=dict(
    identifier='geometry.archecraft.yata',texture_width=TEX_SIZE,texture_height=TEX_SIZE,
    visible_bounds_width=5,visible_bounds_height=4,visible_bounds_offset=[0,1.5,0]),bones=geo_bones)]})
write(HERE/'yata.animation.json',dict(format_version='1.8.0',animations={
    'animation.yata.'+name:dict(loop=name!='hop',animation_length=length,bones={}) for name,length in clips}))

all_points=np.vstack([vertices(e) for e in cubes]);lower=all_points.min(axis=0);upper=all_points.max(axis=0)
seat=transform(bones['rider_seat']['origin'],'body')
dimensions=dict(model_units_per_block=16,model_bounds_units=dict(min=lower.tolist(),max=upper.tolist()),
    visual_size_blocks=dict(width=float((upper[0]-lower[0])/16),height=float((upper[1]-lower[1])/16),length=float((upper[2]-lower[2])/16)),
    rider_seat_model_units=seat.tolist(),rider_seat_blocks=(seat/16).tolist(),
    suggested_entity_hitbox_blocks=dict(width=1.3964844,height=1.6),
    note='Visual ears and tail extend beyond a horse-sized gameplay hitbox. Seat is a modeling guide; runtime passenger placement is not implemented.')
write(HERE/'yata_scale.json',dimensions)

def render(angle,width=850,height=800,scale=14,baseline=725,with_rider=False,ear_joints=False):
    yaw,pitch=math.radians(angle),math.radians(16)
    camera=np.array([math.sin(yaw)*math.cos(pitch),math.sin(pitch),math.cos(yaw)*math.cos(pitch)])
    def project(v):
        x,y,z=v-[0,0,6];horizontal=x*math.cos(yaw)-z*math.sin(yaw);forward=x*math.sin(yaw)+z*math.cos(yaw)
        return [width/2+horizontal*scale,baseline-y*math.cos(pitch)*scale+forward*math.sin(pitch)*scale,
            forward*math.cos(pitch)+y*math.sin(pitch)]
    image=Image.new('RGB',(width,height),(30,36,42));ImageDraw.Draw(image).ellipse((width*0.08,baseline-55,width*.92,baseline+35),fill=(20,26,30))
    pixels=np.array(image);depth=np.full((height,width),-np.inf);texture=np.array(atlas)[:,:,:3]
    def triangle(pts,uv,shade,color=None):
        pts=np.array(pts);x0=max(0,math.floor(pts[:,0].min()));x1=min(width,math.ceil(pts[:,0].max()))
        y0=max(0,math.floor(pts[:,1].min()));y1=min(height,math.ceil(pts[:,1].max()))
        if x0>=x1 or y0>=y1:return
        a,b,c=pts;div=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(div)<1e-7:return
        xx,yy=np.meshgrid(np.arange(x0,x1)+.5,np.arange(y0,y1)+.5)
        wa=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/div
        wb=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/div;wc=1-wa-wb
        zz=wa*a[2]+wb*b[2]+wc*c[2];region=depth[y0:y1,x0:x1]
        mask=(wa>=0)&(wb>=0)&(wc>=0)&(zz>region)
        if color is None:
            uv=np.array(uv);u=np.clip((wa*uv[0,0]+wb*uv[1,0]+wc*uv[2,0]).astype(int),0,TEX_SIZE-1)
            v=np.clip((wa*uv[0,1]+wb*uv[1,1]+wc*uv[2,1]).astype(int),0,TEX_SIZE-1)
            rgb=np.clip(texture[v,u]*shade,0,255).astype('uint8');pixels[y0:y1,x0:x1][mask]=rgb[mask]
        else:pixels[y0:y1,x0:x1][mask]=np.clip(np.array(color)*shade,0,255).astype('uint8')
        region[mask]=zz[mask]
    def draw_cube(e,parent=None,color=None):
        x0,y0,z0=e['from'];x1,y1,z1=e['to']
        faces={
            'north':([(x1,y1,z0),(x0,y1,z0),(x0,y0,z0),(x1,y0,z0)],(0,0,-1)),
            'south':([(x0,y1,z1),(x1,y1,z1),(x1,y0,z1),(x0,y0,z1)],(0,0,1)),
            'east':([(x1,y1,z1),(x1,y1,z0),(x1,y0,z0),(x1,y0,z1)],(1,0,0)),
            'west':([(x0,y1,z0),(x0,y1,z1),(x0,y0,z1),(x0,y0,z0)],(-1,0,0)),
            'up':([(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)],(0,1,0)),
            'down':([(x0,y0,z1),(x1,y0,z1),(x1,y0,z0),(x0,y0,z0)],(0,-1,0))}
        for face,(verts,n) in faces.items():
            normal=transform(n,parent,True) if parent else np.array(n)
            if np.dot(normal,camera)<=0:continue
            pts=[project(transform(v,parent) if parent else np.array(v)) for v in verts]
            u,v,u1,v1=e['faces'][face]['uv'] if color is None else [0,0,1,1]
            uv=[(u,v),(u1,v),(u1,v1),(u,v1)]
            shade=.77+max(0,normal[1])*.22+max(0,-normal[2])*.13+max(0,-normal[0])*.06
            for indices in [(0,1,2),(0,2,3)]:triangle([pts[i] for i in indices],[uv[i] for i in indices],shade,color)
    for e in cubes:draw_cube(e,e['_bone'])
    if with_rider:
        # Seated Minecraft-size mannequin: 8-unit head, 12-unit torso, bent 12-unit legs.
        sx,sy,sz=seat
        guides=[([-4,sy,sz-2],[4,sy+12,sz+2],(68,133,151)),
            ([-4,sy+12,sz-4],[4,sy+20,sz+4],(190,166,133)),
            ([-8,sy+1,sz-4],[-4,sy+12,sz],(68,133,151)),([4,sy+1,sz-4],[8,sy+12,sz],(68,133,151)),
            ([-8,sy-4,sz-6],[-4,sy,sz+2],(72,83,109)),([4,sy-4,sz-6],[8,sy,sz+2],(72,83,109)),
            ([-8,sy-12,sz-6],[-4,sy-4,sz-2],(72,83,109)),([4,sy-12,sz-6],[8,sy-4,sz-2],(72,83,109))]
        for lo,hi,color in guides:draw_cube({'from':lo,'to':hi},color=color)
    result=Image.fromarray(pixels)
    if ear_joints:
        marks=ImageDraw.Draw(result)
        for side in ['left','right']:
            b=bones['ear_'+side+'_tip']
            px,py,_=project(transform(b['origin'],b['parent']))
            marks.ellipse((px-6,py-6,px+6,py+6),fill=(78,225,211),outline=(20,45,45),width=2)
    return result

preview=Image.new('RGB',(1700,920),(30,36,42))
preview.paste(render(215),(0,55));preview.paste(render(90,with_rider=True),(850,55))
d=ImageDraw.Draw(preview);font=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',27)
small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',19)
d.text((30,16),'YATA / RIGGED MOUNT BASE',font=font,fill=(238,225,201))
d.text((30,865),'FRONT / THREE-QUARTER',font=small,fill=(174,188,193))
d.text((880,865),'SIDE / SEATED PLAYER SCALE GUIDE (not included in model)',font=small,fill=(174,188,193))
d.text((30,895),f'{len(cubes)} cuboids / {len(bones)} bones / 256 x 256 pixel atlas / blank animation clips',font=small,fill=(174,188,193))
preview.save(HERE/'yata_preview.png')
render(180,width=850,height=850,scale=14,baseline=780).save(HERE/'yata_front.png')

# A posing demonstration only: exported model and animation clips remain neutral.
ear_demo=Image.new('RGB',(1700,920),(30,36,42))
ear_demo.paste(render(215,ear_joints=True),(0,55))
bones['ear_left_tip']['rotation']=[-70,0,12]
bones['ear_right_tip']['rotation']=[-50,0,-10]
ear_demo.paste(render(215,ear_joints=True),(850,55))
bones['ear_left_tip']['rotation']=[0,0,0]
bones['ear_right_tip']['rotation']=[0,0,0]
ed=ImageDraw.Draw(ear_demo)
ed.text((30,16),'YATA / MUTED PALETTE + FLOPPY EAR HINGES',font=font,fill=(225,216,203))
ed.text((30,865),'NEUTRAL / cyan dots mark the new mid-ear pivots',font=small,fill=(174,188,193))
ed.text((880,865),'POSE EXAMPLE / upper ears bend independently',font=small,fill=(174,188,193))
ed.text((30,895),'Animate ear_left_tip and ear_right_tip; keep ear_left / ear_right for whole-ear movement.',font=small,fill=(174,188,193))
ear_demo.save(HERE/'yata_ear_pivots.png')
print(f'Exported {len(cubes)} cuboids, {len(bones)} bones, embedded atlas, geometry and animation templates.')
print(json.dumps(dimensions,indent=2))

# Apply the current foot design to generated bases as well as saved projects.
from shape_feet import apply_toe_stance
apply_toe_stance(HERE)
from add_hand_claws import apply_hand_claws
apply_hand_claws(HERE)
from add_ear_flaps import apply_ear_flaps
apply_ear_flaps(HERE)
