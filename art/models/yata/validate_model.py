"""Check the animation base and round-trip its Bedrock coordinate conversion."""
from pathlib import Path
from collections import Counter
import base64, io, json, math, sys
from PIL import Image
import numpy as np
from project_tools import load,world as pose_world,corners

HERE=Path(__file__).resolve().parent
project,bones,parents,owners,cubes,embedded=load(HERE/'yata.bbmodel')
geometry=json.loads((HERE/'yata.geo.json').read_text())['minecraft:geometry'][0]
assert project['meta']['model_format']=='bedrock'
assert project['resolution']=={'width':256,'height':256}
assert len(project['elements'])>=60
texture=Image.open(HERE/'yata.png').convert('RGBA')
embedded=Image.open(io.BytesIO(base64.b64decode(project['textures'][0]['source'].split(',')[1]))).convert('RGBA')
assert texture.size==(256,256) and texture.tobytes()==embedded.tobytes()

uuids=[b['uuid'] for b in bones.values()]
for group in bones.values():
    assert len(group['origin'])==len(group['rotation'])==3
    assert all(math.isfinite(n) for n in group['origin']+group['rotation'])
assert len(bones)==29 and set(owners)=={e['uuid'] for e in project['elements']}
assert parents['left_foot']=='left_shin' and parents['ear_left']=='head'
assert parents['right_hand']=='right_forearm' and parents['tail_tip']=='tail_mid'
assert parents['ear_left_tip']=='ear_left' and parents['ear_right_tip']=='ear_right'
assert parents['ear_left_flap']=='ear_left' and parents['ear_right_flap']=='ear_right'

exported={b['name']:b for b in geometry['bones']}
assert exported.keys()==bones.keys()
for name,b in bones.items():
    g=exported[name]
    assert g.get('parent')==parents[name]
    assert np.allclose([-g['pivot'][0],g['pivot'][1],g['pivot'][2]],b['origin'])
    r=g.get('rotation',[0,0,0])
    assert np.allclose([-r[0],-r[1],r[2]],b['rotation'])
    local=[e for e in project['elements'] if owners[e['uuid']]==name]
    assert len(local)==len(g.get('cubes',[]))
    for e,c in zip(local,g.get('cubes',[])):
        uuids.append(e['uuid']);lo=e['from'];hi=e['to']
        assert all(math.isfinite(n) for n in lo+hi)
        assert all(b>a for a,b in zip(lo,hi))
        origin=c['origin'];size=c['size']
        assert np.allclose([-origin[0]-size[0],origin[1],origin[2]],lo)
        assert np.allclose(np.array(hi)-lo,size)
        assert set(e['faces'])=={'north','south','east','west','up','down'}
        for face,f in e['faces'].items():
            u,v,u1,v1=f['uv']
            assert 0<=u<u1<=256 and 0<=v<v1<=256
            assert texture.crop((u,v,u1,v1)).getchannel('A').getextrema()==(255,255)
            a,b=c['uv'][face]['uv'];w,h=c['uv'][face]['uv_size']
            roundtrip=[a+w,b+h,a,b] if face in ('up','down') else [a,b,a+w,b+h]
            assert roundtrip==f['uv']
assert len(uuids)==len(set(uuids))

layout=json.loads((HERE/'yata_uv_layout.json').read_text())
assert len(layout)==len(cubes)*6
occupied=set()
elements={e['name']:e for e in project['elements']}
for island in layout:
    u,v,u1,v1=island['uv']
    coords={(x,y) for x in range(u,u1) for y in range(v,v1)}
    if coords.intersection(occupied):
        source=elements.get(island.get('shared_with',''))
        assert island['material'] in ('claw','fur','inner') and source is not None,'Unexpected overlapping UV islands'
        assert source['faces'][island['face']]['uv']==island['uv'],'Shared claw UV must match its existing source'
    occupied.update(coords)
clips=project['animations'];animations=json.loads((HERE/'yata.animation.json').read_text())['animations']
assert len(clips)==6 and len({c['uuid'] for c in clips})==6
for clip in clips:
    assert clip['length']>0
    if clip['name'] in ('animation.yata.idle','animation.yata.ridden_idle'):
        assert clip['loop']=='loop' and clip['length']==4.2
        assert len(clip['animators'])==19 and len(animations[clip['name']]['bones'])==19
        for bone_id,animator in clip['animators'].items():
            assert bone_id in {b['uuid'] for b in bones.values()}
            assert not any(part in animator['name'] for part in ('thigh','shin','foot'))
            for channel in {k['channel'] for k in animator['keyframes']}:
                keys=sorted([k for k in animator['keyframes'] if k['channel']==channel],key=lambda k:k['time'])
                assert keys[0]['time']==0 and keys[-1]['time']==clip['length']
                assert keys[0]['data_points']==keys[-1]['data_points']
                assert all(k['interpolation']=='linear' for k in keys)
                assert all(math.isfinite(float(p[a])) for k in keys for p in k['data_points'] for a in 'xyz')
    elif clip['name'] in ('animation.yata.run','animation.yata.walk','animation.yata.ridden_walk'):
        durations={'animation.yata.run':.66,'animation.yata.walk':.96,'animation.yata.ridden_walk':.64}
        assert clip['loop']=='loop' and clip['length']==durations[clip['name']]
        assert len(clip['animators'])==26 and len(animations[clip['name']]['bones'])==26
        for bone_id,animator in clip['animators'].items():
            assert bone_id in {b['uuid'] for b in bones.values()}
            for channel in {k['channel'] for k in animator['keyframes']}:
                keys=sorted([k for k in animator['keyframes'] if k['channel']==channel],key=lambda k:k['time'])
                assert keys[0]['time']==0 and keys[-1]['time']==clip['length']
                assert keys[0]['data_points']==keys[-1]['data_points']
                assert all(math.isfinite(float(p[a])) for k in keys for p in k['data_points'] for a in 'xyz')
    else:
        assert clip.get('animators',{})=={} and animations[clip['name']]['bones']=={}
    assert animations[clip['name']]['animation_length']==clip['length']
scale=json.loads((HERE/'yata_scale.json').read_text())
actual_points=np.vstack([corners(e,bones,parents,owners) for e in cubes])
assert np.allclose(scale['model_bounds_units']['min'],actual_points.min(axis=0))
assert np.allclose(scale['model_bounds_units']['max'],actual_points.max(axis=0))
assert 1.35<scale['rider_seat_blocks'][1]<1.5
assert 2.4<scale['visual_size_blocks']['height']<3

# Exercise the new joint: rotating one tip moves its geometry around the hinge,
# while the lower ear and the opposite ear retain their exact neutral positions.
def world(point,name,overrides=None):
    point=np.array(point,dtype=float)
    while name:
        b=bones[name];x,y,z=np.radians((overrides or {}).get(name,b['rotation']))
        rx=np.array([[1,0,0],[0,np.cos(x),-np.sin(x)],[0,np.sin(x),np.cos(x)]])
        ry=np.array([[np.cos(y),0,np.sin(y)],[0,1,0],[-np.sin(y),0,np.cos(y)]])
        rz=np.array([[np.cos(z),-np.sin(z),0],[np.sin(z),np.cos(z),0],[0,0,1]])
        pivot=np.array(b['origin']);point=rz@ry@rx@(point-pivot)+pivot;name=parents[name]
    return point
elements={e['name']:e for e in project['elements']}
for side in ['left','right']:
    hand=side+'_hand';base=elements[side+' little claws']
    for i in range(1,4):
        claw=elements[side+f' hand claw {i}'];tip=elements[side+f' hand claw {i} tip']
        assert owners[claw['uuid']]==owners[tip['uuid']]==hand
        assert tip['to'][0]-tip['from'][0]<claw['to'][0]-claw['from'][0]<0.6,'Each claw must taper'
        assert tip['from'][1]<claw['from'][1]<base['from'][1],'Claws must project beyond the paw'
        for a,b in [(base,claw),(claw,tip)]:
            assert all(min(a['to'][axis],b['to'][axis])>max(a['from'][axis],b['from'][axis])
                for axis in range(3)),'Claw segments must connect without gaps'
# The artist may change the stance in Blockbench. Exact generated leg proportions
# are opt-in; structural/export checks and new claw connections remain mandatory.
for side in (['left','right'] if '--check-generated-pose' in sys.argv else []):
    thigh=side+'_thigh';shin=side+'_shin';foot=side+'_foot'
    hip=pose_world(bones[thigh]['origin'],thigh,bones,parents)
    knee=pose_world(bones[shin]['origin'],shin,bones,parents)
    ankle=pose_world(bones[foot]['origin'],foot,bones,parents)
    assert hip[1]>knee[1]>ankle[1]
    assert knee[2]<hip[2]-3,'Knee must sit forward of hip'
    assert ankle[2]>knee[2]+2.5,'Lower leg must bend backward after knee'
    assert ankle[1]>5.5,'Heel joint must be raised above the toe contact patch'
    foot_cubes=[e for e in cubes if owners[e['uuid']]==foot]
    points=np.vstack([corners(e,bones,parents,owners) for e in foot_cubes])
    assert abs(points[:,1].min())<0.00001,'Foot must remain planted'
    assert points[:,2].min()<ankle[2]-6,'Toes must point forward'
    ankle_cube=elements[side+' ankle']
    assert corners(ankle_cube,bones,parents,owners)[:,1].min()>4,'Heel must not touch the ground'
    shaft=elements[side+' broad hind foot']
    assert 25<shaft.get('rotation',[0,0,0])[0]<50,'Foot must slope up to the ankle'
    assert np.allclose(shaft['origin'],bones[foot]['origin']),'Rising foot must pivot at ankle joint'
    top=np.array([(shaft['from'][0]+shaft['to'][0])/2,shaft['to'][1],
        (shaft['from'][2]+shaft['to'][2])/2])
    from project_tools import matrix
    tip=matrix(shaft['rotation'])@(top-np.array(shaft['origin']))+shaft['origin']
    assert np.allclose(pose_world(tip,foot,bones,parents),ankle),'Upper foot must meet the joint exactly'
    assert corners(shaft,bones,parents,owners)[:,1].min()>0.25,'Only toe pads should support the stance'
    for i in range(1,4):
        toe=elements[side+f' toe {i}'];pts=corners(toe,bones,parents,owners)
        assert abs(pts[:,1].min())<0.00001 and pts[:,1].max()<1.3,'Toe pads must be short and planted'
        assert not any(toe.get('rotation',[0,0,0])),'Toe pads must have a flat sole'
for side,other in [('left','right'),('right','left')]:
    root='ear_'+side;tip=root+'_tip'
    # Exercise the hinge relative to its saved rest pose, including a natural flop.
    bent=list(bones[tip]['rotation']);bent[0]-=70;override={tip:bent}
    stem=elements[side+' ear stem'];upper=elements[side+' ear tip']
    assert owners[stem['uuid']]==root and owners[upper['uuid']]==tip
    a=np.mean([stem['from'],stem['to']],axis=0);b=np.mean([upper['from'],upper['to']],axis=0)
    assert np.allclose(world(a,root),world(a,root,override))
    assert np.linalg.norm(world(b,tip)-world(b,tip,override))>5
    assert np.allclose(world(bones[tip]['origin'],tip),world(bones[tip]['origin'],tip,override))
    opposite=elements[other+' ear tip'];p=np.mean([opposite['from'],opposite['to']],axis=0)
    assert np.allclose(world(p,'ear_'+other+'_tip'),world(p,'ear_'+other+'_tip',override))
    lower=elements[side+' broad ear'];upper=elements[side+' ear upper panel']
    assert lower['to'][1]==upper['from'][1]==bones[tip]['origin'][1]
    flap=root+'_flap';flap_tip=elements[side+' lower ear flap tip']
    assert owners[flap_tip['uuid']]==flap
    assert len([e for e in cubes if owners[e['uuid']]==flap])==6
    bend={flap:[30,0,bones[flap]['rotation'][2]]}
    p=np.mean([flap_tip['from'],flap_tip['to']],axis=0)
    assert np.linalg.norm(world(p,flap)-world(p,flap,bend))>1,'Lower flap must be independently movable'
    assert np.allclose(world(bones[flap]['origin'],flap),world(bones[flap]['origin'],flap,bend))
    p=np.mean([upper['from'],upper['to']],axis=0)
    assert np.allclose(world(p,tip),world(p,tip,bend)),'Flap motion must not move the main ear'
print(f'Validated {len(cubes)} cuboids, {len(bones)} bones, {len(layout)} textured faces, geometry export, independent ear flaps, tip hinges and hand claws.')
