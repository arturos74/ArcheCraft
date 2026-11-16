"""Export the saved Blockbench rig, textured faces and idle/walk/run to the renderer.

This reads the saved file without modifying it, including artist edits, bone
rest rotations and per-face UVs. No modeling/animation dependency is required.
"""
from pathlib import Path
import hashlib,json
import numpy as np
from project_tools import load,matrix

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ASSETS=ROOT/'src/main/resources/assets/archecraft'
path=HERE/'yata.bbmodel'
project,bones,parents,owners,cubes,texture=load(path)
tw,th=texture.size
quads=[]
names=list(bones)
def native(p):return np.array([-p[0]/16,(24-p[1])/16,p[2]/16])
rig=[]
for name,b in bones.items():
    parent=parents[name]
    pivot=native(b['origin'])-(native(bones[parent]['origin']) if parent else 0)
    r=b.get('rotation',[0,0,0])
    rig.append(dict(name=name,parent=names.index(parent) if parent else -1,
        pivot=pivot.tolist(),rotation=[-r[0],-r[1],r[2]]))
for e in cubes:
    if not e.get('export',True) or not e.get('visibility',True):continue
    x0,y0,z0=e['from'];x1,y1,z1=e['to']
    pivot=np.array(e.get('origin',[0,0,0]));rotation=matrix(e.get('rotation',[0,0,0]));parent=owners[e['uuid']]
    faces={
        'north':([(x1,y1,z0),(x0,y1,z0),(x0,y0,z0),(x1,y0,z0)],(0,0,-1)),
        'south':([(x0,y1,z1),(x1,y1,z1),(x1,y0,z1),(x0,y0,z1)],(0,0,1)),
        'east':([(x1,y1,z1),(x1,y1,z0),(x1,y0,z0),(x1,y0,z1)],(1,0,0)),
        'west':([(x0,y1,z0),(x0,y1,z1),(x0,y0,z1),(x0,y0,z0)],(-1,0,0)),
        'up':([(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)],(0,1,0)),
        'down':([(x0,y0,z1),(x1,y0,z1),(x1,y0,z0),(x0,y0,z0)],(0,-1,0))}
    for face,(vertices,normal) in faces.items():
        data=e['faces'][face]
        if data.get('texture') is None:continue
        u,v,u1,v1=data['uv'];uv=[(u/tw,v/th),(u1/tw,v/th),(u1/tw,v1/th),(u/tw,v1/th)]
        turns=int(data.get('rotation',0))//90
        uv=uv[-turns:]+uv[:-turns] if turns else uv
        points=[]
        for vertex in vertices:
            p=rotation@(np.array(vertex)-pivot)+pivot
            # Vanilla living renderers flip X/Y and put feet at model Y=24.
            # Reflect both here so the saved pose retains its handedness.
            points.append(native(p)-native(bones[parent]['origin']))
        normal=rotation@np.array(normal)
        normal=np.array([-normal[0],-normal[1],normal[2]])
        normal/=np.linalg.norm(normal)
        indices=[0,1,2,3]
        cross=np.cross(points[1]-points[0],points[2]-points[0])
        if np.dot(cross,normal)<0:indices=[0,3,2,1]
        packed=[[round(float(n),8) for n in [*points[i],*uv[i]]] for i in indices]
        assert all(0<=n<=1 for p in packed for n in p[3:])
        quads.append(dict(bone=names.index(parent),normal=[round(float(n),8) for n in normal],vertices=packed))
mesh_path=ASSETS/'entity/yata_mesh.json'
texture_path=ASSETS/'textures/entity/yata.png'
mesh_path.parent.mkdir(parents=True,exist_ok=True);texture_path.parent.mkdir(parents=True,exist_ok=True)
mesh_path.write_text(json.dumps(dict(format_version=2,bones=rig,quads=quads),separators=(',',':'))+'\n')
texture.save(texture_path)
def export_clip(short_name):
    clip=next(c for c in project['animations'] if c['name']=='animation.yata.'+short_name)
    assert clip['loop']=='loop' and clip['length']>0
    tracks={}
    for bone_id,animator in clip.get('animators',{}).items():
        if animator.get('type')!='bone':continue
        name=next(n for n,b in bones.items() if b['uuid']==bone_id)
        if animator.get('rotation_global'):raise ValueError('Global rotation is not supported: '+name)
        channels={}
        for k in animator['keyframes']:
            channel=k['channel']
            if channel not in ('rotation','position','scale'):raise ValueError(channel)
            interpolation=k.get('interpolation','linear')
            if interpolation not in ('linear','step'):raise ValueError('Use linear or step keys: '+name)
            if len(k['data_points'])!=1:raise ValueError('Pre/post key values are not supported: '+name)
            v=[float(k['data_points'][0][a]) for a in 'xyz']
            if not all(np.isfinite(v)):raise ValueError('Non-finite key: '+name)
            if channel=='rotation':v=[-v[0],-v[1],v[2]]
            if channel=='position':v=[-v[0]/16,-v[1]/16,v[2]/16]
            channels.setdefault(channel,[]).append(dict(time=k['time'],value=v,step=interpolation=='step'))
        for keys in channels.values():
            keys.sort(key=lambda k:k['time'])
            assert len({k['time'] for k in keys})==len(keys)
        tracks[name]=channels
    animation_path=ASSETS/f'entity/yata_{short_name}.json'
    animation_path.write_text(json.dumps(dict(duration=clip['length'],tracks=tracks),separators=(',',':'))+'\n')
    return animation_path,clip['length']
animation_path,idle_seconds=export_clip('idle')
run_path,run_seconds=export_clip('run')
walk_path,walk_seconds=export_clip('walk')
ridden_walk_path,ridden_walk_seconds=export_clip('ridden_walk')
manifest=dict(source='art/models/yata/yata.bbmodel',source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    cuboids=len(cubes),bones=len(bones),quads=len(quads),texture_dimensions=list(texture.size),
    mesh=str(mesh_path.relative_to(ROOT)).replace('\\','/'),texture=str(texture_path.relative_to(ROOT)).replace('\\','/'),
    texture_sha256=hashlib.sha256(texture_path.read_bytes()).hexdigest(),
    animation=str(animation_path.relative_to(ROOT)).replace('\\','/'),idle_seconds=idle_seconds,
    run_animation=str(run_path.relative_to(ROOT)).replace('\\','/'),run_seconds=run_seconds,
    walk_animation=str(walk_path.relative_to(ROOT)).replace('\\','/'),walk_seconds=walk_seconds,
    ridden_walk_animation=str(ridden_walk_path.relative_to(ROOT)).replace('\\','/'),ridden_walk_seconds=ridden_walk_seconds,
    saddle_mesh='src/main/resources/assets/archecraft/entity/yata_saddle.json',
    saddle_texture='src/main/resources/assets/archecraft/textures/entity/yata_saddle.png',
    male_texture='src/main/resources/assets/archecraft/textures/entity/yata_male.png',
    male_authoring_source='art/models/yata/male/yata_male.bbmodel',male_size_multiplier=1.1,
    black_texture='src/main/resources/assets/archecraft/textures/entity/yata_black.png',
    black_authoring_source='art/models/yata/variants/black/yata_black.bbmodel',black_size_multiplier=1.3,
    palomino_texture='src/main/resources/assets/archecraft/textures/entity/yata_palomino.png',
    palomino_authoring_source='art/models/yata/variants/palomino/yata_palomino.bbmodel',palomino_size_multiplier=1.3,
    albino_texture='src/main/resources/assets/archecraft/textures/entity/yata_albino.png',
    albino_authoring_source='art/models/yata/variants/albino/yata_albino.bbmodel',albino_size_multiplier=1.3,
    notes='Bone-local native mesh and additive idle/walk/ridden_walk/run tracks. Model, animation and texture load on resource reload. '
        'Run this exporter after changing the saved Blockbench project. Source project is never modified by export.')
(ROOT/'docs/yata-runtime-model.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(f'Exported current saved Yata: {len(cubes)} cuboids, {len(quads)} textured quads, {tw}x{th} texture. Source project untouched.')
