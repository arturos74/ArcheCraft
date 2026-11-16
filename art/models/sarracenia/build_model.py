"""Editable cuboid sarracenia with two swept-back tendrils and a forked rear stalk.

Creates a Blockbench Bedrock project and UV atlas; does not register an entity.
Front is -Z, Y is up, 16 model units equal one Minecraft block.
"""
from pathlib import Path
import base64
import copy
import hashlib
import io
import json
import math
import sys
import uuid
import numpy as np
from PIL import Image,ImageDraw,ImageFont

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'yata'))
from project_tools import load,write,render,export_geometry,corners

NS=uuid.UUID('c8c91f1c-4d34-4ef8-83b5-c216af54ef9c')
def uid(name):return str(uuid.uuid5(NS,name))
groups={};children={};elements=[];materials={};parameters={}


def bone(name,origin,parent=None,rotation=(0,0,0)):
    assert name not in groups
    groups[name]=dict(name=name,uuid=uid('bone/'+name),origin=list(origin),rotation=list(rotation),
                      export=True,visibility=True,locked=False,color=0,children=[],reset=False,
                      shade=True,mirror_uv=False,isOpen=True)
    children[name]=[]
    if parent:children[parent].append(('bone',name))
    return name


def cube(name,lo,hi,parent,material,rotation=(0,0,0),origin=None,params=None,face_materials=None):
    assert all(hi[i]>lo[i] for i in range(3)),name
    e=dict(name=name,type='cube',uuid=uid('cube/'+name),from_=np.asarray(lo,dtype=float).tolist(),to=np.asarray(hi,dtype=float).tolist(),
           origin=np.asarray(origin if origin is not None else (np.array(lo)+np.array(hi))/2,dtype=float).tolist(),
           rotation=np.asarray(rotation,dtype=float).tolist(),box_uv=False,autouv=0,export=True,visibility=True,
           locked=False,color=0,faces={})
    e['from']=e.pop('from_');elements.append(e);children[parent].append(('cube',e['uuid']))
    materials[e['uuid']]={face:(face_materials or {}).get(face,material) for face in ['north','east','south','west','up','down']}
    parameters[e['uuid']]=params or {}
    return e


def segment(name,a,b,width,parent,material='stem',depth=None):
    a,b=np.array(a,dtype=float),np.array(b,dtype=float);v=b-a;length=float(np.linalg.norm(v));mid=(a+b)/2
    rotation=[math.degrees(math.asin(v[2]/length)),0,math.degrees(math.atan2(-v[0],v[1]))]
    half=np.array([width/2,length/2,(depth if depth is not None else width)/2])
    return cube(name,mid-half,mid+half,parent,material,rotation,mid)


bone('root',(0,0,0))
bone('body',(0,10,1),'root')
bone('lower_roots',(0,3,1),'root')
bone('mouth',(0,19,0),'body',(-22,0,0))
bone('hood',(0,24,6),'body',(-6,0,0))

# Stepped, pear-shaped bulb. The neck ends below the actual hollow mouth.
for name,lo,hi in [
    ('bulb_bottom',(-5,3,-3),(5,6,5)),
    ('bulb_lower',(-7,5,-5),(7,9,7)),
    ('bulb_belly',(-9,8,-6),(9,15,8)),
    ('bulb_shoulders',(-7.5,15,-4.8),(7.5,18.5,7)),
    ('narrow_pitcher_neck',(-5.8,18,-3.5),(5.8,20,5.5))]:
    cube(name,lo,hi,'body','bulb')
cube('left_bulb_facet',(-9.5,9,-3.5),(-7.6,14,5.5),'body','bulb',(0,0,-12),(-8,11,1))
cube('right_bulb_facet',(7.6,9,-3.5),(9.5,14,5.5),'body','bulb',(0,0,12),(8,11,1))

# Short root prongs support the body, while small golden thorns break its outline.
for i,(x,z,tx,tz) in enumerate([(-3,-2,-5,-4),(3,-2,5,-4),(-4,3,-6,5),(4,3,6,5),(0,4,0,7)]):
    segment(f'root_{i+1}_upper',(x,4,z),(tx,1.1,tz),1.6,'lower_roots','root',1.4)
    cube(f'root_{i+1}_toe',(tx-.8,0,tz-.8),(tx+.8,1,tz+.8),'lower_roots','root')
for i,(a,b) in enumerate([
    ((-8.5,12,-1),(-11,13,-2)),((8.5,12,-1),(11,13,-2)),
    ((-6,7,-5),(-7.3,5.3,-7)),((6,7,-5),(7.3,5.3,-7)),
    ((-6.5,14,6),(-8.8,15,7.5)),((6.5,14,6),(8.8,15,7.5)),
    ((-2.5,6,-4.7),(-3.4,3.7,-6)),((2.5,6,-4.7),(3.4,3.7,-6))]):
    mid=tuple(np.array(a)*.25+np.array(b)*.75)
    segment(f'thorn_{i+1}_base',a,mid,1.25,'body','thorn')
    segment(f'thorn_{i+1}_tip',mid,b,.55,'body','thorn')

# Four walls and a low interior floor create a genuine opening, not a black cap.
cube('mouth_cavity_floor',(-5.7,18.5,-4.6),(5.7,19,4.6),'mouth','inner')
cube('mouth_left_wall',(-7,18.5,-5.7),(-5.7,23.4,5.7),'mouth','neck',face_materials={'east':'inner'})
cube('mouth_right_wall',(5.7,18.5,-5.7),(7,23.4,5.7),'mouth','neck',face_materials={'west':'inner'})
cube('mouth_front_wall',(-5.7,18.5,-5.8),(5.7,23.4,-4.6),'mouth','neck',face_materials={'south':'inner'})
cube('mouth_back_wall',(-5.7,18.5,4.6),(5.7,23.4,5.8),'mouth','neck',face_materials={'north':'inner'})
for i in range(5):
    x0=-7.8+i*3.12;rise=[.2,.7,.4,.8,.2][i]
    cube(f'front_lip_ridge_{i+1}',(x0,23,-7),(x0+3.2,24.4+rise,-5.2),'mouth','rim')
for i in range(4):
    x0=-7.4+i*3.7
    cube(f'back_lip_ridge_{i+1}',(x0,23,5.1),(x0+3.8,24.6+(i%2)*.4,6.8),'mouth','rim')
for side in [-1,1]:
    for i in range(3):
        z0=-5.2+i*3.45;x0=-8 if side<0 else 6.1
        cube(f'{"left" if side<0 else "right"}_lip_ridge_{i+1}',(x0,23,z0),(x0+1.9,24.6+(i%2)*.5,z0+3.6),'mouth','rim')

# A 16-wide, 14-long leafy lid matches the mouth's outer rim dimensions.
# The hood pivot sits at the rear lip so it can close over the opening later.
segment('hood_petiole',(0,20,5.5),(0,27,7),1.6,'hood','stem')
for i,(lo,hi) in enumerate([
    ((-6,25,6.4),(6,28,7.4)),((-8,28,6.8),(8,34,8)),
    ((-7,34,7.1),(7,37,8.2)),((-4,37,7.4),(4,39,8.3))]):
    cube(f'hood_leaf_panel_{i+1}',lo,hi,'hood','hood',face_materials={'south':'leaf_back'})
segment('hood_center_vein',(0,25,6.2),(0,38.6,7.1),.65,'hood','gold_vein',.45)


def leaf_blade(name,a,b,parent,width_scale=1):
    tip=bone(name+'_leaf',a,parent)
    a,b=np.array(a),np.array(b);v=b-a;length=float(np.linalg.norm(v))
    rotation=[math.degrees(math.asin(v[2]/length)),0,math.degrees(math.atan2(-v[0],v[1]))]
    # Stepped blade widths taper to a blocky point. Each has its own leaf pivot.
    widths=np.array([2,4.5,6.5,5,3,.9])*width_scale
    fractions=[0,.13,.31,.55,.76,.91,1]
    for i,width in enumerate(widths):
        lo=[a[0]-width/2,a[1]+length*fractions[i],a[2]-.42]
        hi=[a[0]+width/2,a[1]+length*fractions[i+1]+.08,a[2]+.42]
        cube(name+f'_leaf_panel_{i+1}',lo,hi,tip,'leaf',rotation,a,dict(leaf_root=a.tolist(),leaf_length=length))
    for side in [-1,1]:
        lo=[a[0]+side*3.4*width_scale-width_scale,a[1]+length*.36,a[2]-.35]
        hi=[lo[0]+2*width_scale,a[1]+length*.46,a[2]+.35]
        cube(name+f'_leaf_lobe_{side}',lo,hi,tip,'leaf',rotation,a,dict(leaf_root=a.tolist(),leaf_length=length))
    cube(name+'_leaf_midrib',[a[0]-.32,a[1],a[2]-.55],[a[0]+.32,a[1]+length*.94,a[2]-.35],tip,'gold_vein',rotation,a)


def back_stem(name,points,leaf_end):
    root=bone(name,points[0],'body')
    parent=root
    for i,(a,b) in enumerate(zip(points,points[1:])):
        if i:parent=bone(name+f'_bend_{i}',a,parent)
        segment(name+f'_segment_{i+1}',a,b,1.45-i*.22,parent,'stem')
        if i<2:
            joint=np.array(b);cube(name+f'_node_{i+1}',joint-.85,joint+.85,parent,'node')
    leaf_blade(name,points[-1],leaf_end,parent)


# The front pair sweep toward +Z (the back), instead of reaching past the mouth.
back_stem('back_stem_left_outer',[(-4.5,19,6),(-10,28,10),(-17,26,17),(-20,21,21)],(-18,7,26))
back_stem('back_stem_right_outer',[(4.5,19,6),(10,29,10),(17,26,17),(20,20,21)],(18,6.5,26))

# One short central stalk grows from the back, then splits into two broad blades.
# Both forks inherit the shared stalk's motion; the blades can still flap alone.
bone('rear_stalk',(0,19,7),'body')
segment('rear_stalk_base',(0,19,7),(0,24,11),2,'rear_stalk')
bone('rear_stalk_tip',(0,24,11),'rear_stalk')
segment('rear_stalk_upper',(0,24,11),(0,27,15),1.65,'rear_stalk_tip')
cube('rear_stalk_fork_node',(-1,26,14),(1,28,16),'rear_stalk_tip','node')
for side,sign in [('left',-1),('right',1)]:
    name='rear_fork_'+side
    bone(name,(0,27,15),'rear_stalk_tip')
    start=(sign*6,25,18)
    segment(name+'_petiole',(0,27,15),start,1.45,name)
    leaf_blade(name,start,(sign*10,9,23),name,width_scale=1.65)


def face_basis(e):
    x0,y0,z0=e['from'];x1,y1,z1=e['to']
    return {
        'north':((x1,y1,z0),(x0,y1,z0),(x1,y0,z0)), 'south':((x0,y1,z1),(x1,y1,z1),(x0,y0,z1)),
        'east':((x1,y1,z1),(x1,y1,z0),(x1,y0,z1)), 'west':((x0,y1,z0),(x0,y1,z1),(x0,y0,z0)),
        'up':((x0,y1,z0),(x1,y1,z0),(x0,y1,z1)), 'down':((x0,y0,z1),(x1,y0,z1),(x0,y0,z0))}


def paint(point,material,face,e,params):
    x,y,z=point
    if material=='bulb':
        color=[63,83,39] if y>9 else [84,62,32]
        mottle=math.sin(x*.67+y*.48)+math.sin(z*.71-y*.57)+.4*math.sin(x*1.6+z)
        if mottle>1.15:color=[118,67,30]
        elif mottle<-.9:color=[41,61,32]
        angle=math.atan2(x,z-1)
        rib=abs(math.sin(angle*7+.12*y))
        if rib>.96 and mottle>-.65:color=[156,111,44]
        elif rib>.88:color=[95,109,45]
    elif material=='neck':
        color=[57,80,37]
        if abs(math.sin(x*1.8+z*.6))>.87:color=[107,116,48]
    elif material=='inner':
        color=[19,30,16]
        if face=='up':color=[29,45,20]
        if abs(math.sin(x*1.7+z*.8))>.94:color=[41,56,25]
    elif material=='rim':
        color=[179,76,24]
        if face=='up':color=[211,127,39]
        if math.sin(x*2.9+z*2.4)>.3:color=[211,137,44]
        elif math.sin(x*2.9+z*2.4)<-.65:color=[137,49,22]
    elif material in ('stem','node'):
        color=[82,94,43] if material=='stem' else [121,111,43]
        if abs(math.sin(x*2.5+z*2))>.86:color=[151,130,55]
    elif material=='thorn':color=[169,130,55] if face in ('north','up') else [106,91,44]
    elif material=='root':color=[70,76,39] if face=='up' else [59,62,33]
    elif material=='hood':
        color=[106,89,32]
        if abs(x)<1 or abs(math.sin(y*1.3-abs(x)*1.1))>.87:color=[190,111,31]
        elif abs(x)>3:color=[63,82,37]
    elif material=='leaf_back':color=[62,82,40]
    elif material=='leaf':
        root=params['leaf_root'];t=(y-root[1])/params['leaf_length'];across=abs(x-root[0])
        color=[75,96,47]
        if across<1.15 and t<.8:color=[173,105,31]
        if abs(math.sin(t*22-across*1.6))>.93 and t<.85:color=[184,131,43]
        if t>.86:color=[94,113,67]
    elif material=='gold_vein':color=[169,135,57]
    else:raise ValueError(material)
    return color


def build():
    atlas=Image.new('RGBA',(256,256),(0,0,0,0));rng=np.random.default_rng(51653)
    previous_path=HERE/'sarracenia.bbmodel'
    previous=json.loads(previous_path.read_text()) if previous_path.exists() else None
    reused=set()
    if previous:
        old_cubes={e['uuid']:e for e in previous['elements']}
        old_atlas=Image.open(io.BytesIO(base64.b64decode(previous['textures'][0]['source'].split(',',1)[1]))).convert('RGBA')
        for e in elements:
            old=old_cubes.get(e['uuid'])
            if old and all(e[k]==old[k] for k in ('name','from','to','origin','rotation')):
                e['faces']=copy.deepcopy(old['faces']);reused.add(e['uuid'])
                for face in e['faces'].values():
                    rect=tuple(face['uv']);atlas.paste(old_atlas.crop(rect),rect[:2])
    # Pack unique face islands, largest first, with one transparent padding pixel.
    requests=[]
    for e in elements:
        if e['uuid'] in reused:continue
        basis=face_basis(e)
        for face,(a,b,c) in basis.items():
            density=1.5
            w=max(1,math.ceil(np.linalg.norm(np.array(b)-a)*density))
            h=max(1,math.ceil(np.linalg.norm(np.array(c)-a)*density))
            requests.append((w,h,e,face))
    requests.sort(key=lambda item:(-item[1],-item[0]))
    px=1;py=max([f['uv'][3]+2 for e in elements if e['uuid'] in reused for f in e['faces'].values()]+[1]);row=0
    layout=[dict(cube=e['name'],face=f,material=materials[e['uuid']][f],uv=d['uv'])
            for e in elements if e['uuid'] in reused for f,d in e['faces'].items()]
    for w,h,e,face in requests:
        if px+w+1>256:px=1;py+=row+2;row=0
        assert py+h+1<=256,'UV atlas overflow'
        e['faces'][face]=dict(uv=[px,py,px+w,py+h],texture=0)
        a,b,c=map(np.array,face_basis(e)[face]);material=materials[e['uuid']][face]
        for yy in range(h):
            for xx in range(w):
                point=a+(b-a)*((xx+.5)/w)+(c-a)*((yy+.5)/h)
                color=np.array(paint(point,material,face,e,parameters[e['uuid']]))
                color=np.clip(color+int(rng.integers(-5,6)),0,255).astype(int)
                atlas.putpixel((px+xx,py+yy),tuple(color)+(255,))
        layout.append(dict(cube=e['name'],face=face,material=material,uv=[px,py,px+w,py+h]))
        px+=w+2;row=max(row,h)
    def outliner(name):
        return dict(uuid=groups[name]['uuid'],isOpen=True,children=[outliner(value) if kind=='bone' else value for kind,value in children[name]])
    template=json.loads((HERE.parent/'yata/yata.bbmodel').read_text())
    tex=copy.deepcopy(template['textures'][0]);buffer=io.BytesIO();atlas.save(buffer,format='PNG')
    tex.update(name='sarracenia.png',uuid=uid('texture'),source='data:image/png;base64,'+base64.b64encode(buffer.getvalue()).decode(),
               width=256,height=256,uv_width=256,uv_height=256,path='',saved=True)
    animations=copy.deepcopy(previous['animations']) if previous else []
    group_ids={g['uuid'] for g in groups.values()}
    for clip in animations:
        clip['animators']={key:value for key,value in clip['animators'].items() if key in group_ids}
    project=dict(meta=dict(format_version='5.0',model_format='bedrock',box_uv=False),name='Sarracenia',
                 model_identifier='archecraft.sarracenia',visible_box=[5,4,1.5],variable_placeholders='',
                 resolution=dict(width=256,height=256),elements=elements,groups=list(groups.values()),outliner=[outliner('root')],textures=[tex],animations=animations)
    path=HERE/'sarracenia.bbmodel';write(path,project);atlas.save(HERE/'sarracenia.png');write(HERE/'sarracenia_uv_layout.json',layout)
    p,b,parents,owners,cubes,t=load(path)
    geo=export_geometry(p,b,parents,owners,cubes);desc=geo['minecraft:geometry'][0]['description']
    desc.update(identifier='geometry.archecraft.sarracenia',visible_bounds_width=5,visible_bounds_height=4,visible_bounds_offset=[0,1.5,0])
    write(HERE/'sarracenia.geo.json',geo)
    front=render(cubes,t,b,parents,owners,angle=215,view_scale=14,baseline=720,center=(0,0,5))
    back=render(cubes,t,b,parents,owners,angle=35,view_scale=14,baseline=720,center=(0,0,5))
    front.save(HERE/'sarracenia_front.png');back.save(HERE/'sarracenia_back.png')
    render(cubes,t,b,parents,owners,angle=110,view_scale=14,baseline=720,center=(0,0,5)).save(HERE/'sarracenia_side.png')
    preview=Image.new('RGB',(1700,890),(30,36,42));preview.paste(front,(0,35));preview.paste(back,(850,35))
    draw=ImageDraw.Draw(preview);font=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',27);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
    draw.text((30,15),'SARRACENIA / EDITABLE MOB BASE',font=font,fill=(231,220,202))
    draw.text((30,835),'FRONT / hollow pitcher + orange peristome',font=small,fill=(183,197,190))
    draw.text((880,835),'BACK / shared rear stalk + two broad leaves',font=small,fill=(183,197,190))
    preview.save(HERE/'sarracenia_preview.png')
    points=np.vstack([corners(e,b,parents,owners) for e in cubes]);lo=points.min(axis=0);hi=points.max(axis=0)
    write(HERE/'model_manifest.json',dict(model='sarracenia.bbmodel',model_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        texture='sarracenia.png',texture_sha256=hashlib.sha256((HERE/'sarracenia.png').read_bytes()).hexdigest(),
        cuboids=len(cubes),bones=len(b),long_tendrils=2,shared_rear_stalks=1,rear_blades=2,animations=len(animations),texture_size=[256,256],units_per_block=16,
        bounds_units=dict(min=lo.tolist(),max=hi.tolist()),size_blocks=((hi-lo)/16).tolist(),front='-Z',
        references=['ScreenShot0055.jpg (back)','ScreenShot0056.jpg (front)','ScreenShot0053.jpg (front)','codex-clipboard-bd93cb9b-f563-48c5-9926-fee42249af90.jpg (corrected leaf layout)']))
    print(f'Built sarracenia: {len(cubes)} cuboids / {len(b)} bones / 2 swept-back tendrils + one forked rear stalk. Preserved {len(reused)} unchanged textured cubes. Atlas uses {py+row} of 256 rows.')


if __name__=='__main__':build()
