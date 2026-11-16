"""Validate and preview saved clips. Pass --walk for the walking animation."""
from pathlib import Path
import copy
import json
import subprocess
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent/'yata'))
import project_tools as pt

project, bones, parents, owners, cubes, texture = pt.load(HERE/'sarracenia.bbmodel')
SHORT = 'walk' if '--walk' in sys.argv else 'idle'
backup = 'before_walk_animation' if SHORT=='walk' else 'leaf_correction_before_idle'
old = json.loads((HERE/f'versions/{backup}/sarracenia.bbmodel').read_text())
for key in old:
    if key != 'animations': assert old[key] == project[key], f'Artist data changed: {key}'
clip = next(c for c in project['animations'] if c['name'] == 'animation.sarracenia.'+SHORT)
if SHORT=='walk':
    for previous in old['animations']:
        if previous['name']!=clip['name']:assert previous in project['animations'], 'Other animation changed'
external = json.loads((HERE/'sarracenia.animation.json').read_text())['animations'][clip['name']]
tracks = {}
for animator in clip['animators'].values():
    assert animator['name'] in bones
    channels = tracks.setdefault(animator['name'], {})
    for key in animator['keyframes']:
        v = np.array([float(key['data_points'][0][axis]) for axis in 'xyz'])
        assert np.all(np.isfinite(v))
        channels.setdefault(key['channel'], []).append((key['time'], v))
        converted = v*np.array([-1,-1,1]) if key['channel']=='rotation' else v*np.array([-1,1,1])
        assert np.allclose(external['bones'][animator['name']][key['channel']][str(key['time'])], converted)
    for channel, keys in channels.items():
        keys.sort(key=lambda k:k[0])
        assert len({k[0] for k in keys}) == len(keys)
        assert keys[0][0] == 0 and keys[-1][0] == clip['length']
        assert np.array_equal(keys[0][1], keys[-1][1]), 'Loop seam'
if SHORT=='idle':assert 'lower_roots' not in tracks and 'root' not in tracks
assert clip['loop'] == 'loop' and external['loop']
print(f'PASS {SHORT}: geometry/UVs/texture preserved; finite tracks; matching animation export; seamless endpoints; other clips preserved.')

pose = {}


def sample(t):
    return {name:{channel:np.array([np.interp(t,[k[0] for k in keys],[k[1][axis] for k in keys])
                                   for axis in range(3)]) for channel,keys in channels.items()}
            for name,channels in tracks.items()}


def animated_world(point, name, bones, parents, normal=False):
    point = np.array(point,dtype=float)
    while name:
        b = bones[name]
        pivot = np.zeros(3) if normal else np.array(b['origin'])
        ch = pose.get(name,{})
        point = pt.matrix(np.array(b.get('rotation',[0,0,0]))+ch.get('rotation',0))@(point-pivot)+pivot
        if not normal: point += ch.get('position',0)
        name = parents[name]
    return point


pt.world = animated_world
if SHORT=='walk':
    # Check interpolated poses too, since rotation and vertical correction are
    # interpolated separately during playback. Toes may lift, never sink.
    lowest=1e9;highest_support=-1e9
    for t in np.linspace(0,clip['length'],93):
        pose=sample(t)
        points=np.vstack([pt.corners(c,bones,parents,owners) for c in cubes])
        assert np.all(np.isfinite(points))
        lowest=min(lowest,points[:,1].min())
        supports=np.vstack([pt.corners(c,bones,parents,owners) for c in cubes if owners[c['uuid']]=='lower_roots'])
        highest_support=max(highest_support,supports[:,1].min())
    assert lowest>=-.025, f'Ground clipping: {lowest}'
    assert highest_support<=.925, f'Excessive bounce: {highest_support}'
    print(f'PASS walk floor: minimum {lowest:.4f} units; maximum toe clearance {highest_support:.3f} units across 93 interpolated poses.')

if '--render' in sys.argv:
    sys.path.insert(0,str(ROOT/'build/video-tools'))
    import imageio_ffmpeg
    frames = ROOT/f'build/sarracenia-{SHORT}-preview'
    frames.mkdir(parents=True,exist_ok=True)
    fps = 50 if SHORT=='walk' else 20
    count = round(clip['length']*fps)
    font = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
    for frame in range(count):
        pose = sample(frame/fps)
        views=[]
        for angle in ([215,110] if SHORT=='walk' else [215]):
            im = pt.render(cubes,texture,bones,parents,owners,angle=angle,view_scale=10,baseline=710,center=(0,0,6))
            draw = ImageDraw.Draw(im)
            draw.text((28,22),'SARRACENIA / '+SHORT.upper(),font=font,fill=(231,220,202))
            text='Body rock / bobbing shuffle / curling tendrils' if SHORT=='walk' else 'Sway / stem sweeps / leaf follow-through / lid bobs'
            draw.text((28,53),text,font=font,fill=(174,188,193))
            views.append(im.resize((680,640)))
        frame_image=Image.new('RGB',(680*len(views),640))
        for i,view in enumerate(views):frame_image.paste(view,(680*i,0))
        frame_image.save(frames/f'{frame:03d}.png')
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    cycle = frames/'cycle.mp4'
    subprocess.run([exe,'-y','-v','error','-framerate',str(fps),'-i',str(frames/'%03d.png'),
                    '-frames:v',str(count),'-c:v','libx264','-pix_fmt','yuv420p','-crf','20',str(cycle)],check=True)
    subprocess.run([exe,'-y','-v','error','-stream_loop','5' if SHORT=='walk' else '1','-i',str(cycle),'-c','copy',
                    '-movflags','+faststart',str(HERE/f'sarracenia_{SHORT}_preview.mp4')],check=True)
    sheet = Image.new('RGB',(2040,1440 if SHORT=='walk' else 1280))
    times=[0,.16,.3,.46,.62,.78] if SHORT=='walk' else [0,2.6,3.15,3.4,3.85,4.4]
    for i, t in enumerate(times):
        im = Image.open(frames/f'{round(t*fps):03d}.png').copy()
        ImageDraw.Draw(im).text((25,600),f'{t:.2f} seconds',font=font,fill=(231,220,202))
        if SHORT=='walk':sheet.paste(im.resize((1020,480)),((i%2)*1020,(i//2)*480))
        else:sheet.paste(im,((i%3)*680,(i//3)*640))
    sheet.save(HERE/f'sarracenia_{SHORT}_poses.png')
    print(f'Rendered saved {SHORT} preview and six key poses.')
