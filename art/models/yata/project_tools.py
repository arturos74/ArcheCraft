"""Read editable Blockbench 4/5 projects without discarding saved user changes."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import base64, io, json, math
import numpy as np

def load(path):
    project=json.loads(Path(path).read_text())
    groups={g['uuid']:g for g in project.get('groups',[])}
    bones={};parents={};owners={}
    def walk(nodes,parent=None):
        for node in nodes:
            if isinstance(node,str):owners[node]=parent;continue
            group=groups.get(node['uuid'],node)
            name=group['name'];bones[name]=group;parents[name]=parent
            walk(node.get('children',[]),name)
    walk(project['outliner'])
    cubes=project['elements']
    texture=Image.open(io.BytesIO(base64.b64decode(project['textures'][0]['source'].split(',')[1]))).convert('RGBA')
    return project,bones,parents,owners,cubes,texture

def matrix(angles):
    x,y,z=np.radians(angles)
    rx=np.array([[1,0,0],[0,np.cos(x),-np.sin(x)],[0,np.sin(x),np.cos(x)]])
    ry=np.array([[np.cos(y),0,np.sin(y)],[0,1,0],[-np.sin(y),0,np.cos(y)]])
    rz=np.array([[np.cos(z),-np.sin(z),0],[np.sin(z),np.cos(z),0],[0,0,1]])
    return rz@ry@rx

def world(point,name,bones,parents,normal=False):
    point=np.array(point,dtype=float)
    while name:
        b=bones[name];pivot=np.zeros(3) if normal else np.array(b['origin'])
        point=matrix(b.get('rotation',[0,0,0]))@(point-pivot)+pivot;name=parents[name]
    return point

def corners(cube,bones,parents,owners):
    pts=[]
    for x in (cube['from'][0],cube['to'][0]):
        for y in (cube['from'][1],cube['to'][1]):
            for z in (cube['from'][2],cube['to'][2]):
                pivot=np.array(cube.get('origin',[0,0,0]))
                p=matrix(cube.get('rotation',[0,0,0]))@(np.array([x,y,z])-pivot)+pivot
                pts.append(world(p,owners[cube['uuid']],bones,parents))
    return np.array(pts)

def write(path,data):Path(path).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')

def export_geometry(project,bones,parents,owners,cubes):
    records=[]
    for name,b in bones.items():
        x,y,z=b['origin'];record=dict(name=name,pivot=[-x,y,z])
        if parents[name]:record['parent']=parents[name]
        r=b.get('rotation',[0,0,0])
        if any(r):record['rotation']=[-r[0],-r[1],r[2]]
        entries=[]
        for e in cubes:
            if owners[e['uuid']]!=name or not e.get('export',True):continue
            lo,hi=e['from'],e['to'];uv={}
            for f,data in e['faces'].items():
                if data.get('texture') is None:continue
                u,v,u1,v1=data['uv']
                uv[f]=dict(uv=[u1,v1],uv_size=[u-u1,v-v1]) if f in ('up','down') else dict(uv=[u,v],uv_size=[u1-u,v1-v])
                if data.get('rotation'):uv[f]['uv_rotation']=data['rotation']
            entry=dict(origin=[-hi[0],lo[1],lo[2]],size=[round(b-a,6) for a,b in zip(lo,hi)],uv=uv)
            r=e.get('rotation',[0,0,0])
            if any(r):
                x,y,z=e['origin'];entry.update(pivot=[-x,y,z],rotation=[-r[0],-r[1],r[2]])
            entries.append(entry)
        if entries:record['cubes']=entries
        records.append(record)
    return {'format_version':'1.12.0','minecraft:geometry':[dict(description=dict(identifier='geometry.archecraft.yata',
        texture_width=project['resolution']['width'],texture_height=project['resolution']['height'],
        visible_bounds_width=5,visible_bounds_height=4,visible_bounds_offset=[0,1.5,0]),bones=records)]}

def render(cubes,texture,bones,parents,owners,angle=215,joints=False,ear_joints=False,
           center=(0,0,6),view_scale=14,baseline=725):
    width,height=850,800;scale=view_scale
    yaw,pitch=np.radians([angle,16]);camera=np.array([np.sin(yaw)*np.cos(pitch),np.sin(pitch),np.cos(yaw)*np.cos(pitch)])
    def project(v):
        x,y,z=v-center;h=x*np.cos(yaw)-z*np.sin(yaw);f=x*np.sin(yaw)+z*np.cos(yaw)
        return [width/2+h*scale,baseline-y*np.cos(pitch)*scale+f*np.sin(pitch)*scale,f*np.cos(pitch)+y*np.sin(pitch)]
    canvas=Image.new('RGB',(width,height),(30,36,42));ImageDraw.Draw(canvas).ellipse((68,670,782,760),fill=(20,26,30))
    pixels=np.array(canvas);depth=np.full((height,width),-np.inf);tex=np.array(texture)[:,:,:3]
    def triangle(pts,uv,shade):
        pts=np.array(pts);x0=max(0,math.floor(pts[:,0].min()));x1=min(width,math.ceil(pts[:,0].max()))
        y0=max(0,math.floor(pts[:,1].min()));y1=min(height,math.ceil(pts[:,1].max()))
        if x0>=x1 or y0>=y1:return
        a,b,c=pts;div=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(div)<1e-7:return
        xx,yy=np.meshgrid(np.arange(x0,x1)+.5,np.arange(y0,y1)+.5)
        wa=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/div
        wb=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/div;wc=1-wa-wb
        zz=wa*a[2]+wb*b[2]+wc*c[2];region=depth[y0:y1,x0:x1]
        mask=(wa>=0)&(wb>=0)&(wc>=0)&(zz>region);uv=np.array(uv)
        u=np.clip((wa*uv[0,0]+wb*uv[1,0]+wc*uv[2,0]).astype(int),0,tex.shape[1]-1)
        v=np.clip((wa*uv[0,1]+wb*uv[1,1]+wc*uv[2,1]).astype(int),0,tex.shape[0]-1)
        colors=np.clip(tex[v,u]*shade,0,255).astype('uint8');pixels[y0:y1,x0:x1][mask]=colors[mask];region[mask]=zz[mask]
    for e in cubes:
        if not e.get('visibility',True):continue
        parent=owners[e['uuid']];x0,y0,z0=e['from'];x1,y1,z1=e['to'];pivot=np.array(e.get('origin',[0,0,0]));r=matrix(e.get('rotation',[0,0,0]))
        surfaces={
            'north':([(x1,y1,z0),(x0,y1,z0),(x0,y0,z0),(x1,y0,z0)],(0,0,-1)),
            'south':([(x0,y1,z1),(x1,y1,z1),(x1,y0,z1),(x0,y0,z1)],(0,0,1)),
            'east':([(x1,y1,z1),(x1,y1,z0),(x1,y0,z0),(x1,y0,z1)],(1,0,0)),
            'west':([(x0,y1,z0),(x0,y1,z1),(x0,y0,z1),(x0,y0,z0)],(-1,0,0)),
            'up':([(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)],(0,1,0)),
            'down':([(x0,y0,z1),(x1,y0,z1),(x1,y0,z0),(x0,y0,z0)],(0,-1,0))}
        for f,(vs,n) in surfaces.items():
            normal=world(r@np.array(n),parent,bones,parents,True)
            if np.dot(normal,camera)<=0:continue
            pts=[project(world(r@(np.array(v)-pivot)+pivot,parent,bones,parents)) for v in vs]
            u,v,u1,v1=e['faces'][f]['uv'];uv=[(u,v),(u1,v),(u1,v1),(u,v1)]
            shade=.77+max(0,normal[1])*.22+max(0,-normal[2])*.13+max(0,-normal[0])*.06
            for ids in [(0,1,2),(0,2,3)]:triangle([pts[i] for i in ids],[uv[i] for i in ids],shade)
    result=Image.fromarray(pixels)
    if joints:
        d=ImageDraw.Draw(result)
        for side in ['left','right']:
            positions=[]
            for kind,color in [('thigh',(78,225,211)),('shin',(239,201,84)),('foot',(220,138,210))]:
                b=bones[side+'_'+kind];p=world(b['origin'],side+'_'+kind,bones,parents);px,py,_=project(p)
                positions.append((px,py));d.ellipse((px-5,py-5,px+5,py+5),fill=color)
            d.line(positions,fill=(221,218,205),width=2)
    if ear_joints:
        d=ImageDraw.Draw(result)
        for side in ['left','right']:
            name='ear_'+side+'_tip';px,py,_=project(world(bones[name]['origin'],name,bones,parents))
            d.ellipse((px-6,py-6,px+6,py+6),fill=(78,225,211),outline=(20,45,45),width=2)
    return result

def preview(path,cubes,texture,bones,parents,owners):
    result=Image.new('RGB',(1700,920),(30,36,42))
    result.paste(render(cubes,texture,bones,parents,owners),(0,55))
    result.paste(render(cubes,texture,bones,parents,owners,90,True),(850,55))
    d=ImageDraw.Draw(result);font=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',27)
    small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',19)
    d.text((30,16),'YATA / TOE-PLANTED HIND FEET',font=font,fill=(231,220,202))
    d.text((30,865),'FRONT / THREE-QUARTER',font=small,fill=(174,188,193))
    d.text((880,865),'SIDE / hip (cyan), knee (yellow), ankle (pink)',font=small,fill=(174,188,193))
    d.text((30,895),'Flat toe pads / raised heels / sloped feet meeting the ankle pivots.',font=small,fill=(174,188,193))
    result.save(path)

def refresh_assets(here,project,bones,parents,owners,cubes,texture):
    """Export and preview the actual saved model, including per-cube rotations."""
    write(here/'yata.geo.json',export_geometry(project,bones,parents,owners,cubes))
    layout_path=here/'yata_uv_layout.json'
    if layout_path.exists():
        names={e['name'] for e in cubes}
        write(layout_path,[f for f in json.loads(layout_path.read_text()) if f['cube'] in names])
    texture.save(here/'yata.png')
    preview(here/'yata_legs_preview.png',cubes,texture,bones,parents,owners)
    preview(here/'yata_preview.png',cubes,texture,bones,parents,owners)
    render(cubes,texture,bones,parents,owners,180).save(here/'yata_front.png')
    ear_demo=Image.new('RGB',(1700,920),(30,36,42))
    ear_demo.paste(render(cubes,texture,bones,parents,owners,ear_joints=True),(0,55))
    saved={n:list(bones[n]['rotation']) for n in ['ear_left_tip','ear_right_tip']}
    bones['ear_left_tip']['rotation']=[-70,0,12]
    bones['ear_right_tip']['rotation']=[-50,0,-10]
    ear_demo.paste(render(cubes,texture,bones,parents,owners,ear_joints=True),(850,55))
    for name,rotation in saved.items():bones[name]['rotation']=rotation
    d=ImageDraw.Draw(ear_demo);font=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',27)
    small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',19)
    d.text((30,16),'YATA / FLOPPY EAR HINGES + TOE STANCE',font=font,fill=(231,220,202))
    d.text((30,865),'NEUTRAL / cyan dots mark the ear hinges',font=small,fill=(174,188,193))
    d.text((880,865),'POSE EXAMPLE / independent ear-tip movement',font=small,fill=(174,188,193))
    ear_demo.save(here/'yata_ear_pivots.png')
    points=np.vstack([corners(e,bones,parents,owners) for e in cubes]);lo=points.min(axis=0);hi=points.max(axis=0)
    seat=world(bones['rider_seat']['origin'],'rider_seat',bones,parents)
    write(here/'yata_scale.json',dict(model_units_per_block=16,model_bounds_units=dict(min=lo.tolist(),max=hi.tolist()),
        visual_size_blocks=dict(zip(['width','height','length'],((hi-lo)/16).tolist())),
        rider_seat_model_units=seat.tolist(),rider_seat_blocks=(seat/16).tolist(),
        suggested_entity_hitbox_blocks=dict(width=1.3964844,height=1.6),
        note='Visual bounds include ears and tail. Riding guide only; no runtime mount behavior.'))
