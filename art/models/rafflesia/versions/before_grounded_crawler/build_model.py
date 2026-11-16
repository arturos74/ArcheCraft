"""Build an editable cuboid Rafflesia from ScreenShot0057; no game registration.

Front is -Z, Y is up, and 16 model units equal one Minecraft block.
Regenerating replaces this model, so retain a copy before editing in Blockbench.
"""
from pathlib import Path
import base64
import hashlib
import io
import math
import sys
import uuid

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'yata'))
from project_tools import load, write, render, export_geometry, corners

NS = uuid.UUID('cab27883-1cad-4572-b3bb-a121e3342194')
groups, children, elements, materials = {}, {}, [], {}
FACES = ('north', 'east', 'south', 'west', 'up', 'down')


def uid(name):
    return str(uuid.uuid5(NS, name))


def bone(name, pivot, parent=None, rotation=(0, 0, 0)):
    groups[name] = dict(name=name, uuid=uid('bone/' + name), origin=list(pivot),
                        rotation=list(rotation), export=True, visibility=True,
                        locked=False, color=0, reset=False, shade=True, mirror_uv=False)
    children[name] = []
    if parent:
        children[parent].append(('bone', name))


def cube(name, lo, hi, parent, material, rotation=(0, 0, 0), origin=None):
    assert all(b > a for a, b in zip(lo, hi)), name
    e = dict(name=name, type='cube', uuid=uid('cube/' + name),
             to=list(map(float, hi)), origin=list(map(float, origin if origin is not None else (np.array(lo) + hi) / 2)),
             rotation=list(map(float, rotation)), box_uv=False, autouv=0,
             export=True, visibility=True, locked=False, color=0, faces={})
    e['from'] = list(map(float, lo))
    elements.append(e)
    children[parent].append(('cube', e['uuid']))
    materials[e['uuid']] = material


def segment(name, a, b, width, parent, material, depth=None):
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    v = b - a
    length = float(np.linalg.norm(v))
    mid = (a + b) / 2
    rotation = [math.degrees(math.asin(v[2] / length)), 0,
                math.degrees(math.atan2(-v[0], v[1]))]
    half = np.array([width / 2, length / 2, (depth or width) / 2])
    cube(name, mid - half, mid + half, parent, material, rotation, mid)


def blade(name, a, b, width, parent, material='leaf'):
    """A tapered leaf with a raised midrib and a hinge at its petiole."""
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    v = b - a
    length = float(np.linalg.norm(v))
    r = [math.degrees(math.asin(v[2] / length)), 0,
         math.degrees(math.atan2(-v[0], v[1]))]
    for i, (start, end, factor) in enumerate(((0, .22, .45), (.22, .58, 1), (.58, .84, .7), (.84, 1, .25))):
        w = width * factor
        cube(f'{name}_panel_{i + 1}', [a[0] - w/2, a[1] + length*start, a[2] - .3],
             [a[0] + w/2, a[1] + length*end + .08, a[2] + .3], parent, material, r, a)
    cube(name + '_vein', [a[0] - .19, a[1], a[2] - .48],
         [a[0] + .19, a[1] + length*.9, a[2] - .29], parent, 'vein', r, a)


bone('root', (0, 0, 0))
bone('body', (0, 15, 1), 'root')
cube('woody_heart', (-3, 12, -1), (3, 19, 4), 'body', 'bark')
cube('waist_node', (-2.7, 10.8, .2), (2.7, 14.2, 4.5), 'body', 'calyx')
for sign, side in ((-1, 'left'), (1, 'right')):
    segment(side + '_chest_vine', (sign*2.7, 12, 3), (sign*3.6, 19, -.7), 1.05, 'body', 'vein')
segment('crossing_chest_vine', (-3, 13, -1.1), (2.5, 18.7, -1.3), .85, 'body', 'stem')

# A raised orange/olive leafy collar frames the curved pale neck.
bone('collar', (0, 19, 0), 'body')
for i, angle in enumerate((0, 72, 144, 216, 288)):
    a = math.radians(angle)
    start = (math.sin(a)*1.5, 19.6, math.cos(a)*1.5)
    end = (math.sin(a)*6.5, 17, math.cos(a)*6.5)
    blade(f'collar_sepal_{i+1}', start, end, 3.7, 'collar', 'sepal')

# The neck deliberately curves in an S rather than forming a straight stalk.
bone('neck_base', (0, 19, -.7), 'body')
segment('lower_pale_stalk', (0, 18.7, -.7), (0, 23, -3.3), 2.1, 'neck_base', 'neck')
bone('neck_upper', (0, 23, -3.3), 'neck_base')
segment('neck_curve', (0, 23, -3.3), (0, 27.3, -2.2), 1.9, 'neck_upper', 'neck')
segment('neck_return', (0, 27.3, -2.2), (0, 31, -5), 2.3, 'neck_upper', 'neck')

# Calyx, pointed rear bracts, a five-lobed purple flower, and a hollow trumpet.
bone('head', (0, 31, -5), 'neck_upper', (10, 0, 0))
cube('calyx_center', (-3.2, 28, -6.7), (3.2, 34, -1.2), 'head', 'calyx')
cube('calyx_top', (-2.3, 33.3, -6), (2.3, 35, -2), 'head', 'calyx')
cube('calyx_lower', (-2.5, 26.9, -6), (2.5, 28.7, -2), 'head', 'calyx')
for side, sign in (('left', -1), ('right', 1)):
    bone('head_bract_' + side, (sign*2, 32.3, -1.8), 'head')
    segment(side + '_head_bract_base', (sign*2, 32.3, -1.8), (sign*3.2, 36.2, 1), 1.25, 'head_bract_' + side, 'thorn')
    segment(side + '_head_bract_tip', (sign*3.2, 36.2, 1), (sign*3.3, 39, 2.8), .55, 'head_bract_' + side, 'thorn')

for i in range(5):
    name = f'petal_{i+1}'
    bone(name, (0, 31, -7.1), 'head', ([-3, 4, 6, -5, 3][i], 0, i*72))
    for j, (start, end, width) in enumerate(((2.6, 4.6, 4.8), (4.5, 7.3, 7.8), (7.2, 9.4, 7), (9.3, 10.7, 4.5))):
        cube(f'{name}_lobe_{j+1}', (-width/2, 31+start, -8), (width/2, 31+end, -6.6), name, 'petal',
             (-8 if j == 2 else -16 if j == 3 else 0, 0, 0), (0, 31+start, -7.3))
    cube(name + '_central_fold', (-.35, 34, -8.3), (.35, 40.8, -7.95), name, 'petal_vein')

bone('mouth', (0, 31, -7.1), 'head')
cube('throat_shadow', (-2.7, 28.3, -7.4), (2.7, 33.7, -7), 'mouth', 'cavity')
for i in range(8):
    cube(f'trumpet_wall_{i+1}', (-1.65, 33.5, -10.4), (1.65, 35.1, -7.25),
         'mouth', 'trumpet', (0, 0, i*45), (0, 31, -7.1))
    cube(f'purple_lip_{i+1}', (-1.7, 34, -10.8), (1.7, 35.2, -10.2),
         'mouth', 'petal_vein', (0, 0, i*45), (0, 31, -7.1))
bone('tongue_base', (0, 30.8, -7.5), 'mouth')
segment('magenta_tongue_base', (0, 30.8, -7.5), (0, 29.7, -13), 1.4, 'tongue_base', 'tongue')
bone('tongue_tip', (0, 29.7, -13), 'tongue_base')
segment('magenta_tongue_bend', (0, 29.7, -13), (0, 31.6, -17), 1, 'tongue_tip', 'tongue')
for side, sign in (('left', -1), ('right', 1)):
    bone('tongue_fork_' + side, (0, 31.6, -17), 'tongue_tip')
    segment(side + '_tongue_fork', (0, 31.6, -17), (sign*2.3, 34, -20), .6, 'tongue_fork_' + side, 'purple_tip')
    segment(side + '_tongue_point', (sign*2.3, 34, -20), (sign*3.2, 34.4, -21.3), .25, 'tongue_fork_' + side, 'purple_tip')

# Heavy tapered seed-pod abdomen, broken into joints for later tail movement.
pod_points = [(0, 13.3, 3), (0, 13, 7), (0, 12.4, 11.5), (0, 10.8, 16), (0, 8.5, 20), (0, 6.2, 23), (0, 5.5, 25)]
pod_widths = [5.2, 7.3, 6.4, 4.7, 2.8, 1.1]
parent = 'body'
for i, (a, b, w) in enumerate(zip(pod_points, pod_points[1:], pod_widths)):
    name = 'abdomen_' + ('base' if i == 0 else 'middle' if i == 2 else 'tip' if i == 4 else f'joint_{i}')
    bone(name, a, parent)
    segment(f'segmented_pod_{i+1}', a, b, w, name, 'pod', w*.78)
    segment(f'pod_dark_ring_{i+1}', a, np.array(a)*.83 + np.array(b)*.17, w+.18, name, 'pod_ring', w*.78+.18)
    if i < 4:
        segment(f'pod_upper_thorn_{i+1}', np.array(a) + (0, w*.4, 0), np.array(a) + (0, w*.4+1.7, 1.1), .55, name, 'thorn')
    parent = name

# Two long leaf arms, each with an elbow and hinged pointed blade.
for side, sign in (('left', -1), ('right', 1)):
    upper, lower, hand = side + '_upper_arm', side + '_forearm', side + '_hand_leaf'
    shoulder, elbow, wrist = (sign*3.3, 17.7, -.1), (sign*7.4, 14, -.8), (sign*9, 10.8, -4.3)
    bone(upper, shoulder, 'body')
    segment(side + '_arm_stem', shoulder, elbow, 1.15, upper, 'stem')
    segment(side + '_arm_outer_vine', np.array(shoulder)+(sign*.5, -.2, .5), np.array(elbow)+(sign*.5, 0, .5), .55, upper, 'vein')
    bone(lower, elbow, upper)
    segment(side + '_forearm_stem', elbow, wrist, .85, lower, 'bark')
    for j in range(2):
        a = np.array(elbow)*(.8-j*.3)+np.array(wrist)*(.2+j*.3)
        segment(f'{side}_arm_thorn_{j+1}', a, a+(sign*1.4, 1.5, -.2), .65, lower, 'thorn')
    bone(hand, wrist, lower)
    blade(side + '_sickle_leaf', wrist, (sign*12, 7, -6.7), 3.9, hand, 'sepal')

# Bipedal branching roots; the short toes touch the same flat ground plane.
for side, sign in (('left', -1), ('right', 1)):
    thigh, shin, foot = side + '_root_leg', side + '_root_ankle', side + '_root_foot'
    hip, knee, ankle = (sign*2.5, 12.6, 2), (sign*4.6, 7.7, 3.8), (sign*5.4, 2, -.1)
    bone(thigh, hip, 'body')
    segment(side + '_root_thigh', hip, knee, 1.5, thigh, 'stem')
    bone(shin, knee, thigh)
    segment(side + '_root_shin', knee, ankle, 1.05, shin, 'bark')
    blade(side + '_knee_leaf', knee, (sign*7, 9.2, 5.4), 2.8, shin, 'sepal')
    bone(foot, ankle, shin)
    for j, (dx, z) in enumerate(((-1.5, -3.8), (0, -5), (1.7, -3.4))):
        end = (sign*5.4+dx, .45, z)
        segment(f'{side}_toe_root_{j+1}', ankle, end, .8, foot, 'root')
        cube(f'{side}_toe_pad_{j+1}', (end[0]-.5, 0, end[2]-.7), (end[0]+.5, .8, end[2]+.7), foot, 'root')


def face_basis(e):
    x0, y0, z0 = e['from']; x1, y1, z1 = e['to']
    return dict(north=((x1,y1,z0),(x0,y1,z0),(x1,y0,z0)), south=((x0,y1,z1),(x1,y1,z1),(x0,y0,z1)),
                east=((x1,y1,z1),(x1,y1,z0),(x1,y0,z1)), west=((x0,y1,z0),(x0,y1,z1),(x0,y0,z0)),
                up=((x0,y1,z0),(x1,y1,z0),(x0,y1,z1)), down=((x0,y0,z1),(x1,y0,z1),(x0,y0,z0)))


def paint(point, material, face, e):
    x, y, z = point
    if material == 'petal':
        color = [92, 34, 119]
        mottle = math.sin(x*.9+y*.6) + math.sin(x*1.9-y*.4)
        if mottle > 1.1: color = [117, 45, 140]
        elif mottle < -1: color = [72, 26, 98]
        if abs(math.sin((y-31)*.85-abs(x)*1.5)) > .98: color = [54, 22, 76]
        if min(abs(x-e['from'][0]), abs(x-e['to'][0])) < .28: color = [66, 25, 88]
        if face == 'south': color = np.array(color)*.72
    elif material == 'petal_vein': color = [75, 27, 105] if face != 'up' else [146, 58, 151]
    elif material == 'trumpet':
        color = [55, 25, 82]
        if abs(math.sin(x*2.1+y)) > .8: color = [99, 39, 123]
    elif material == 'cavity': color = [20, 14, 28]
    elif material in ('tongue', 'purple_tip'):
        color = [155, 37, 94] if material == 'tongue' else [99, 32, 138]
        if abs(math.sin(z*1.8+y)) > .85: color = [192, 58, 119] if material == 'tongue' else [146, 51, 163]
    elif material == 'neck':
        color = [192, 191, 124]
        if math.sin(y*1.1+x*1.3) > .7: color = [151, 160, 87]
        if abs(math.sin(x*3.6+z*2.5)) > .93: color = [218, 211, 145]
    elif material == 'calyx':
        color = [125, 137, 54]
        if math.sin(x*1.6+y*.7+z) > .6: color = [181, 163, 69]
        if math.cos(x*1.8+z*1.5) > .65: color = [76, 96, 39]
    elif material in ('pod', 'pod_ring'):
        color = [167, 111, 64] if material == 'pod' else [74, 58, 34]
        if material == 'pod':
            if math.sin(x*.9+z*.5+y*.6) > .6: color = [197, 144, 82]
            if abs(x) > 2.1 and math.sin(z+x) > 0: color = [93, 112, 49]
            if abs(math.sin(x*1.3+y*.7)) < .11: color = [113, 66, 37]
    elif material in ('leaf', 'sepal'):
        color = [84, 103, 42]
        if abs(math.sin(x*1.6+y*.9+z*.8)) > .76: color = [144, 111, 36]
        if material == 'sepal' and math.sin(y*.7+z*.8) > -.1: color = [174, 100, 33]
        if abs(math.sin(y*1.8+x)) < .14: color = [59, 77, 34]
    elif material == 'vein': color = [160, 145, 64]
    elif material == 'thorn': color = [179, 145, 65] if face in ('up', 'north') else [111, 97, 39]
    elif material in ('stem', 'bark', 'root'):
        color = [74, 90, 38] if material == 'stem' else [89, 75, 38]
        if abs(math.sin(x*2.6+z*1.9)) > .82: color = [123, 117, 52]
    else: raise ValueError(material)
    return color


def build():
    HERE.mkdir(parents=True, exist_ok=True)
    size = 256
    atlas = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    rng = np.random.default_rng(5717)
    requests = []
    for e in elements:
        for face, (a, b, c) in face_basis(e).items():
            w = max(1, math.ceil(np.linalg.norm(np.array(b)-a)*1.3))
            h = max(1, math.ceil(np.linalg.norm(np.array(c)-a)*1.3))
            requests.append((w, h, e, face))
    requests.sort(key=lambda r: (-r[1], -r[0]))
    px, py, row, layout = 1, 1, 0, []
    for w, h, e, face in requests:
        if px+w+1 > size: px, py, row = 1, py+row+2, 0
        assert py+h+1 <= size, 'UV atlas overflow'
        e['faces'][face] = dict(uv=[px, py, px+w, py+h], texture=0)
        a, b, c = map(np.array, face_basis(e)[face])
        material = materials[e['uuid']]
        for yy in range(h):
            for xx in range(w):
                point = a+(b-a)*(xx+.5)/w+(c-a)*(yy+.5)/h
                color = np.clip(np.array(paint(point, material, face, e))+int(rng.integers(-5, 6)), 0, 255).astype(int)
                atlas.putpixel((px+xx, py+yy), tuple(color)+(255,))
        layout.append(dict(cube=e['name'], face=face, material=material, uv=[px, py, px+w, py+h]))
        px += w+2
        row = max(row, h)
    def outliner(name):
        return dict(uuid=groups[name]['uuid'], isOpen=True, children=[outliner(value) if kind == 'bone' else value for kind, value in children[name]])
    buffer = io.BytesIO(); atlas.save(buffer, format='PNG')
    texture = dict(name='rafflesia.png', uuid=uid('texture'), source='data:image/png;base64,'+base64.b64encode(buffer.getvalue()).decode(),
                   width=size, height=size, uv_width=size, uv_height=size, path='', saved=True, mode='bitmap',
                   render_mode='default', render_sides='auto', frame_time=1, frame_order_type='loop', visible=True, internal=True)
    clips = [dict(uuid=uid('animation/'+name), name='animation.rafflesia.'+name, loop='loop' if name in ('idle','walk') else 'once',
                  length=2 if name == 'idle' else 1, snapping=20, selected=False, saved=True, override=False,
                  anim_time_update='', blend_weight='', start_delay='', loop_delay='', animators={}) for name in ('idle', 'walk', 'attack', 'death')]
    project = dict(meta=dict(format_version='5.0', model_format='bedrock', box_uv=False), name='Rafflesia',
                   model_identifier='archecraft.rafflesia', visible_box=[5, 4, 1.5], variable_placeholders='',
                   resolution=dict(width=size, height=size), elements=elements, groups=list(groups.values()),
                   outliner=[outliner('root')], textures=[texture], animations=clips)
    path = HERE/'rafflesia.bbmodel'
    write(path, project); atlas.save(HERE/'rafflesia.png'); write(HERE/'rafflesia_uv_layout.json', layout)
    p, b, pa, o, c, t = load(path)
    geo = export_geometry(p, b, pa, o, c)
    geo['minecraft:geometry'][0]['description'].update(identifier='geometry.archecraft.rafflesia', visible_bounds_width=5, visible_bounds_height=4)
    write(HERE/'rafflesia.geo.json', geo)
    write(HERE/'rafflesia.animation.json', dict(format_version='1.8.0', animations={clip['name']: dict(loop=clip['loop']=='loop', animation_length=clip['length'], bones={}) for clip in clips}))
    views = {}
    for name, angle in (('front', 215), ('back', 35), ('side', 110), ('face', 180)):
        views[name] = render(c, t, b, pa, o, angle=angle, view_scale=14, baseline=730, center=(0, 0, 2))
        views[name].save(HERE/f'rafflesia_{name}.png')
    preview = Image.new('RGB', (1700, 900), (30, 36, 42))
    preview.paste(views['front'], (0, 45)); preview.paste(views['back'], (850, 45))
    draw = ImageDraw.Draw(preview)
    font = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 28)
    small = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 20)
    draw.text((30, 12), 'RAFFLESIA / EDITABLE BLOCKBENCH BASE', font=font, fill=(232, 222, 209))
    draw.text((30, 854), 'FRONT / purple bloom, hollow trumpet, forked tongue', font=small, fill=(186, 198, 189))
    draw.text((880, 854), 'BACK / pale curved neck, ribbed pod, branching roots', font=small, fill=(186, 198, 189))
    preview.save(HERE/'rafflesia_preview.png')
    points = np.vstack([corners(e, b, pa, o) for e in c])
    lo, hi = points.min(axis=0), points.max(axis=0)
    write(HERE/'model_manifest.json', dict(model=path.name, model_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
          texture='rafflesia.png', texture_sha256=hashlib.sha256((HERE/'rafflesia.png').read_bytes()).hexdigest(),
          cuboids=len(c), bones=len(b), texture_size=[size, size], units_per_block=16, front='-Z',
          bounds_units=dict(min=lo.tolist(), max=hi.tolist()), size_blocks=((hi-lo)/16).tolist(),
          reference='ScreenShot0057.jpg', reference_notes='Single screenshot: front/side and rear individuals; obscured details interpreted as a blocky base.',
          animation_status='Four empty named templates; no animation or in-game entity registration.'))
    print(f'Built Rafflesia: {len(c)} cubes / {len(b)} bones / {size}x{size} atlas ({py+row} rows).')


if __name__ == '__main__':
    build()
