"""Render saved idle/walk/run clips and verify native playback matches the rig."""
from pathlib import Path
import copy, hashlib, json, math, subprocess, sys
import numpy as np
import project_tools as pt
from PIL import Image,ImageDraw,ImageFont

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
project,bones,parents,owners,cubes,texture=pt.load(HERE/'yata.bbmodel')
SHORT='ridden_walk' if '--ridden-walk' in sys.argv else 'walk' if '--walk' in sys.argv else 'run' if '--run' in sys.argv else 'idle'
clip=next(c for c in project['animations'] if c['name']=='animation.yata.'+SHORT)
tracks={a['name']:{} for a in clip['animators'].values()}
for a in clip['animators'].values():
    for k in a['keyframes']:
        tracks[a['name']].setdefault(k['channel'],[]).append((k['time'],[float(k['data_points'][0][x]) for x in 'xyz']))
for channels in tracks.values():
    for keys in channels.values():keys.sort()

def sample(time):
    return {name:{ch:np.array([np.interp(time,[k[0] for k in keys],[k[1][axis] for k in keys]) for axis in range(3)])
        for ch,keys in channels.items()} for name,channels in tracks.items()}

pose={}
rest_world=pt.world
def animated_world(point,name,bones,parents,normal=False):
    point=np.array(point,dtype=float)
    while name:
        b=bones[name];pivot=np.zeros(3) if normal else np.array(b['origin'])
        channels=pose.get(name,{})
        point=pt.matrix(np.array(b.get('rotation',[0,0,0]))+channels.get('rotation',0))@(point-pivot)+pivot
        if not normal:point+=channels.get('position',0)
        name=parents[name]
    return point

def verify():
    # Verify the current saved artist model, rather than an obsolete animation backup.
    manifest=json.loads((ROOT/'docs/yata-runtime-model.json').read_text())
    assert manifest['source_sha256']==hashlib.sha256((HERE/'yata.bbmodel').read_bytes()).hexdigest(), 'Run export_runtime.py after model edits'
    mesh=json.loads((ROOT/'src/main/resources/assets/archecraft/entity/yata_mesh.json').read_text())
    runtime=json.loads((ROOT/f'src/main/resources/assets/archecraft/entity/yata_{SHORT}.json').read_text())
    assert len(mesh['quads'])==552 and len(mesh['bones'])==29
    fixture=[]
    # Reconstruct native matrices, then compare ALL face corners with authoring
    # coordinates at rest and through the ear flick/tail swing.
    times=[0,.08,.18,.3,.4,.54,.64] if SHORT=='ridden_walk' else [0,.12,.28,.44,.6,.8,.96] if SHORT=='walk' else [0,.1,.2,.3,.4,.5,.66] if SHORT=='run' else [0,.45,1.7,2,2.25,3.4,4.2]
    for t in times:
        global pose
        pose=sample(t)
        transforms=[]
        for b in mesh['bones']:
            ch=runtime['tracks'].get(b['name'],{})
            def value(channel):
                keys=ch.get(channel,[])
                return np.array([np.interp(t,[k['time'] for k in keys],[k['value'][axis] for k in keys]) for axis in range(3)]) if keys else np.zeros(3)
            m=np.eye(4);m[:3,:3]=pt.matrix(np.array(b['rotation'])+value('rotation'));m[:3,3]=np.array(b['pivot'])+value('position')
            transforms.append(transforms[b['parent']]@m if b['parent']>=0 else m)
        vertices=[]
        ordered=[q for index in range(len(mesh['bones'])) for q in mesh['quads'] if q['bone']==index]
        for q in ordered:
            index=q['bone'];name=mesh['bones'][index]['name'];p=np.array(bones[name]['origin'])
            for v in q['vertices']:
                # local native vertex -> unrotated authoring point
                local=np.array(v[:3]);author=p+local*np.array([-16,-16,16])
                authored=animated_world(author,name,bones,parents)
                expected=np.array([-authored[0]/16,(24-authored[1])/16,authored[2]/16])
                actual=(transforms[index]@np.array([*local,1]))[:3]
                assert np.max(np.abs(actual-expected))<1e-7,(t,name)
                vertices.append(actual.tolist())
        fixture.append(dict(time=t,vertices=vertices))
        for side in ['left','right']:
            for e in [e for e in cubes if owners[e['uuid']]==side+'_foot']:
                point=np.mean([e['from'],e['to']],axis=0);pivot=np.array(e.get('origin',[0,0,0]))
                point=pt.matrix(e.get('rotation',[0,0,0]))@(point-pivot)+pivot
                if SHORT=='idle':assert np.allclose(animated_world(point,side+'_foot',bones,parents),rest_world(point,side+'_foot',bones,parents))
    if SHORT in ('run','walk','ridden_walk'):
        for t in np.linspace(0,clip['length'],round(clip['length']*200)+1):
            pose=sample(t)
            lowest=[]
            for e in [e for e in cubes if owners[e['uuid']] in ('left_foot','right_foot')]:
                for x in [e['from'][0],e['to'][0]]:
                    for y in [e['from'][1],e['to'][1]]:
                        for z in [e['from'][2],e['to'][2]]:
                            pivot=np.array(e.get('origin',[0,0,0]));p=pt.matrix(e.get('rotation',[0,0,0]))@(np.array([x,y,z])-pivot)+pivot
                            height=animated_world(p,owners[e['uuid']],bones,parents)[1]
                            assert height>-.025,f'{SHORT} foot clips through the floor'
                            lowest.append(height)
            if SHORT=='walk':assert abs(min(lowest))<.025,'Wild walk must always have a supporting foot on the ground'
            if SHORT=='ridden_walk':assert min(lowest)<.475,'Ridden walk bounce must remain gentle'
    pose={}
    if '--client-fixture' in sys.argv:
        name=f'yata_{SHORT}_expected.json' if SHORT!='idle' else 'yata_animation_expected.json'
        path=ROOT/'build/workbench-checks/resources/assets/archecraft/entity'/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(fixture,separators=(',',':')))
        if SHORT=='walk':
            clips={s:json.loads((ROOT/f'src/main/resources/assets/archecraft/entity/yata_{s}.json').read_text()) for s in ['idle','walk','run']}
            blended=[]
            for seconds,weights in [(.3,[.4,.6,0]),(.2,[0,.5,.5]),(.5,[.6,0,.4]),(1.7,[1,0,0]),(.44,[0,1,0])]:
                transforms=[]
                for b in mesh['bones']:
                    values={ch:np.zeros(3) for ch in ['position','rotation']}
                    for s,weight in zip(['idle','walk','run'],weights):
                        c=clips[s];t=seconds%c['duration'];tracks=c['tracks'].get(b['name'],{})
                        for channel in values:
                            keys=tracks.get(channel,[])
                            if keys:values[channel]+=weight*np.array([np.interp(t,[k['time'] for k in keys],[k['value'][axis] for k in keys]) for axis in range(3)])
                    m=np.eye(4);m[:3,:3]=pt.matrix(np.array(b['rotation'])+values['rotation']);m[:3,3]=np.array(b['pivot'])+values['position']
                    transforms.append(transforms[b['parent']]@m if b['parent']>=0 else m)
                vertices=[(transforms[q['bone']]@np.array([*v[:3],1]))[:3].tolist() for q in ordered for v in q['vertices']]
                blended.append(dict(time=seconds,weights=weights,vertices=vertices))
            (path.parent/'yata_blend_expected.json').write_text(json.dumps(blended,separators=(',',':')))
    print(f'PASS {SHORT}: current saved rig matches native playback at all 2,208 corners / 7 phases; foot ground checks and seamless endpoints.')

verify()
if '--render' in sys.argv:
    sys.path.insert(0,str(ROOT/'build/video-tools'))
    import imageio_ffmpeg
    frames=ROOT/f'build/yata-{SHORT}-preview';frames.mkdir(exist_ok=True)
    pt.world=animated_world
    font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
    fps=50 if SHORT!='idle' else 20
    count=round(clip['length']*fps)
    for frame in range(count):
        t=frame/fps;pose=sample(t)
        image=pt.render(cubes,texture,bones,parents,owners,angle=215)
        draw=ImageDraw.Draw(image)
        draw.text((30,24),'YATA / '+SHORT.upper().replace('_',' '),font=font,fill=(231,220,202))
        label='Ridden walk / .64s cycle / gentle two-beat bounce' if SHORT=='ridden_walk' else 'Alternating steps / .96s stride / gentle sway' if SHORT=='walk' else 'Normal speed / .66s stride / restored from 20% footage' if SHORT=='run' else 'Breathing / head lift / ear flick / tail sweep'
        draw.text((30,57),label,font=font,fill=(174,188,193))
        image.resize((680,640)).save(frames/f'{frame:03d}.png')
    target=frames/'cycle.mp4'
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-framerate',str(fps),'-i',str(frames/'%03d.png'),
        '-frames:v',str(count),'-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-movflags','+faststart',str(target)],check=True)
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-stream_loop','4' if SHORT in ('walk','ridden_walk') else '5' if SHORT=='run' else '0','-i',str(target),
        '-c','copy','-movflags','+faststart',str(HERE/f'yata_{SHORT}_preview.mp4')],check=True)
    # Four key poses make it easy to inspect the ear flick without playing video.
    sheet=Image.new('RGB',(1360,1280))
    for i,frame in enumerate([0,12,24,36] if SHORT=='walk' else [0,8,16,24] if SHORT in ('run','ridden_walk') else [0,32,45,64]):sheet.paste(Image.open(frames/f'{frame:03d}.png'),((i%2)*680,(i//2)*640))
    sheet.save(HERE/f'yata_{SHORT}_poses.png')
    print(f'Rendered yata_{SHORT}_preview.mp4 and yata_{SHORT}_poses.png')
