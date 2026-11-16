"""Author the reference idle on the saved model without rebuilding its artwork."""
from pathlib import Path
import copy
import hashlib
import json
import math
import shutil
import sys
import uuid
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'yata'))
from project_tools import load, write

DURATION = 4.8
NAME = 'animation.sarracenia.idle'
project, bones, parents, owners, cubes, texture = load(HERE / 'sarracenia.bbmodel')
before = copy.deepcopy(project)
backup = HERE / 'versions/leaf_correction_before_idle'
if not backup.exists():
    backup.mkdir(parents=True)
    for name in ['sarracenia.bbmodel', 'model_manifest.json']:
        shutil.copy2(HERE / name, backup / name)


def curve(points, t):
    """Periodic Hermite interpolation, baked to ordinary editable linear keys."""
    if t >= DURATION:
        return points[-1][1]
    for i, ((a, v), (b, w)) in enumerate(zip(points, points[1:])):
        if a <= t < b:
            prev = points[i - 1] if i else (points[-2][0] - DURATION, points[-2][1])
            nex = points[i + 2] if i + 2 < len(points) else (DURATION + points[1][0], points[1][1])
            m = (w - prev[1]) / (b - prev[0])
            n = (nex[1] - v) / (nex[0] - a)
            s = (t - a) / (b - a)
            return ((2*s**3-3*s*s+1)*v + (s**3-2*s*s+s)*(b-a)*m
                    + (-2*s**3+3*s*s)*w + (s**3-s*s)*(b-a)*n)
    raise ValueError(t)


def fidget(values):
    # Source event: wind up at 2.5s, left lift, low sweep, right lift, settle.
    return list(zip([0, 2.3, 2.55, 2.7, 2.95, 3.18, 3.4, 3.67, 3.9, 4.18, 4.45, 4.8], values))


tracks = {}


def add(name, channel, axes):
    tracks.setdefault(name, {})[channel] = axes


add('body', 'position', [None,
    fidget([0, 0, -.2, -.3, 1.15, .4, -.25, 1.05, .55, 0, 0, 0]), None])
add('body', 'rotation', [
    fidget([0, 0, 3, 6, -6, -2, 5, -5, -2, 2, 0, 0]),
    fidget([0, 0, -1, 2, -5, -2, 3, 5, 1, -1, 0, 0]),
    fidget([0, 0, 1, -2, 5, 2, -3, -5, -2, 1, 0, 0])])
add('mouth', 'rotation', [fidget([0, 0, -2, 5, -7, -3, 5, -6, -2, 2, 0, 0]), None, None])
add('hood', 'rotation', [
    fidget([0, 0, -12, -38, 14, 5, -36, 16, 9, -15, 1, 0]),
    None, fidget([0, 0, 0, -3, 5, 2, -4, -5, -2, 2, 0, 0])])

for side, sign in [('left', -1), ('right', 1)]:
    wave = (fidget([0, 0, 12, 18, -48, -36, 22, -2, 12, -25, 4, 0]) if side == 'left'
            else fidget([0, 0, 9, 16, 5, 18, 24, -49, -35, -12, 3, 0]))
    for kind in ['outer']:
        stem = f'back_stem_{side}_{kind}'
        strength = 1 if kind == 'outer' else .72
        delay = 0 if kind == 'outer' else .09

        def z_track(t, w=wave, s=sign, strength=strength, delay=delay):
            # Multiplying by -sign makes negative wave values lift either side.
            value = curve(w, (t-delay) % DURATION)
            return -s * strength * (value if value < 0 else value*.3)

        add(stem, 'rotation', [
            lambda t, s=sign, d=delay, w=wave: .9*math.sin(2*math.pi*t/DURATION) + s*.14*curve(w, (t-d) % DURATION),
            lambda t, s=sign: s*1.2*math.sin(4*math.pi*t/DURATION),
            lambda t, z=z_track: .35*z(t)])
        add(stem+'_bend_1', 'rotation', [
            lambda t, s=sign, w=wave, d=delay: .18*s*curve(w, (t-d-.07) % DURATION),
            None, lambda t, z=z_track: .85*z((t-.07) % DURATION)])
        add(stem+'_bend_2', 'rotation', [
            lambda t, w=wave, d=delay: -.16*curve(w, (t-d-.12) % DURATION),
            None, lambda t, z=z_track: .6*z((t-.13) % DURATION)])
        add(stem+'_leaf', 'rotation', [
            lambda t, w=wave, d=delay: .45*curve(w, (t-d-.18) % DURATION),
            lambda t, s=sign: 2*s*math.sin(4*math.pi*t/DURATION),
            lambda t, z=z_track: .85*z((t-.18) % DURATION)])

# The broad rear leaves now share one stalk, rather than behaving as two long
# independent tendrils. Their forks and blades add smaller delayed flaps.
add('rear_stalk', 'rotation', [
    fidget([0, 0, 3, 10, -8, -2, 9, -8, -3, 3, 0, 0]),
    fidget([0, 0, -1, -2, 5, 2, -3, -5, -1, 1, 0, 0]),
    fidget([0, 0, 0, -2, 6, 2, -2, -6, -2, 1, 0, 0])])
add('rear_stalk_tip', 'rotation', [
    fidget([0, 0, 0, 4, -5, -2, 4, -5, -2, 2, 0, 0]), None, None])
for side,sign in [('left',-1),('right',1)]:
    flap=fidget([0, 0, 0, 5, -12, -5, 8, -12, -5, 4, 0, 0])
    add('rear_fork_'+side, 'rotation', [
        lambda t, p=flap: .35*curve(p,(t-.08)%DURATION),
        lambda t, s=sign: s*1.4*math.sin(4*math.pi*t/DURATION),
        lambda t, p=flap, s=sign: s*.45*curve(p,(t-.1)%DURATION)])
    add('rear_fork_'+side+'_leaf', 'rotation', [
        lambda t, p=flap: curve(p,(t-.18)%DURATION),
        None, lambda t, p=flap, s=sign: -s*.6*curve(p,(t-.2)%DURATION)])

# Capture loop variables in every callable; plain curves are evaluated directly.
# Add a small repeating breeze beneath the source's larger fidget.
for name, channels in tracks.items():
    if name == 'body':
        original = channels['rotation'][2]
        channels['rotation'][2] = lambda t, p=original: curve(p, t)+.65*math.sin(2*math.pi*t/DURATION)
    elif name == 'hood':
        original = channels['rotation'][0]
        channels['rotation'][0] = lambda t, p=original: curve(p,t)+1.2*math.sin(4*math.pi*t/DURATION)

clip = dict(name=NAME, uuid=str(uuid.uuid5(uuid.NAMESPACE_URL, NAME)),
            loop='loop', override=False, length=DURATION, snapping=20, anim_time_update='',
            blend_weight='', start_delay='', loop_delay='', animators={})
external = dict(loop=True, animation_length=DURATION, bones={})
for name, channels in tracks.items():
    keys = []
    out = {}
    for channel, axes in channels.items():
        values_by_time = {}
        for frame in range(round(DURATION*20)+1):
            t = round(frame/20, 4)
            # Exact endpoints prevent numerical drift or a seam when looping.
            values = [round(axis(t) if callable(axis) else curve(axis,t) if axis else 0, 6) for axis in axes]
            if frame == round(DURATION*20):
                values = [float(keys0) for keys0 in start_values]
            if frame == 0:
                start_values = values[:]
            keys.append(dict(channel=channel, data_points=[dict(zip('xyz', values))],
                             uuid=str(uuid.uuid5(uuid.NAMESPACE_URL, f'{NAME}/{name}/{channel}/{t}')),
                             time=t, color=-1, interpolation='linear'))
            exported = values[:]
            if channel == 'rotation': exported = [-values[0], -values[1], values[2]]
            if channel == 'position': exported = [-values[0], values[1], values[2]]
            values_by_time[str(t)] = exported
        out[channel] = values_by_time
    clip['animators'][bones[name]['uuid']] = dict(name=name, type='bone', keyframes=keys)
    external['bones'][name] = out

project['animations'] = [a for a in project['animations'] if a['name'] != NAME] + [clip]
for key in before:
    if key != 'animations': assert before[key] == project[key], key
for old in before['animations']:
    if old['name'] != NAME: assert old in project['animations']
write(HERE/'sarracenia.bbmodel', project)
animation_path = HERE/'sarracenia.animation.json'
exported = json.loads(animation_path.read_text()) if animation_path.exists() else dict(format_version='1.8.0', animations={})
exported['animations'][NAME] = external
write(animation_path, exported)
reference = Path('G:/Temp Recording Location/2026-11-14 20-31-33.mp4')
write(HERE/'idle_motion.json', dict(duration_seconds=DURATION, samples_per_second=20,
    reference=reference.name, reference_sha256=hashlib.sha256(reference.read_bytes()).hexdigest(),
    notes='Hand-authored approximation of the reference: gentle initial sway, then asymmetric upward stem sweeps, trailing leaves, body rock and lid bobs; settle to seamless rest.',
    event_seconds=dict(wind_up=2.5, left_lift=2.95, low_sweep=3.4, right_lift=3.67, settle=4.45)))
manifest = json.loads((HERE/'model_manifest.json').read_text())
manifest.update(model_sha256=hashlib.sha256((HERE/'sarracenia.bbmodel').read_bytes()).hexdigest(), animations=len(project['animations']))
write(HERE/'model_manifest.json', manifest)
print(f'Authored {DURATION}s looping idle on {len(tracks)} bones; geometry, UVs and embedded texture preserved.')
