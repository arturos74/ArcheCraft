"""Check the editable asset's hierarchy, embedded texture, and face UVs."""
from pathlib import Path
import base64
import io
import json
import math
from collections import Counter
from PIL import Image

HERE = Path(__file__).resolve().parent
project = json.loads((HERE / 'sarracenia.bbmodel').read_text())
groups = {g['uuid']: g for g in project['groups']}
cubes = {e['uuid']: e for e in project['elements']}
assert len(groups) == len(project['groups']), 'Duplicate group UUID'
assert len(cubes) == len(project['elements']), 'Duplicate cube UUID'
assert not groups.keys() & cubes.keys(), 'Cube/group UUID collision'
seen_groups, seen_cubes, parents = Counter(), Counter(), {}


def visit(nodes, parent=None):
    for node in nodes:
        if isinstance(node, str):
            assert node in cubes, 'Missing cube reference'
            seen_cubes[node] += 1
        else:
            key = node['uuid']
            assert key in groups, 'Missing group reference'
            assert not seen_groups[key], 'Repeated or cyclic group reference'
            seen_groups[key] += 1
            parents[groups[key]['name']] = parent
            visit(node['children'], groups[key]['name'])


visit(project['outliner'])
assert set(seen_groups) == set(groups), 'Orphan group'
assert set(seen_cubes) == set(cubes), 'Orphan cube'
assert all(n == 1 for n in seen_cubes.values()), 'Repeated cube reference'
stems = ['back_stem_left_outer', 'back_stem_right_outer']
for stem in stems:
    assert parents[stem] == 'body'
    assert parents[stem + '_bend_1'] == stem
    assert parents[stem + '_bend_2'] == stem + '_bend_1'
    assert parents[stem + '_leaf'] == stem + '_bend_2'
assert 'back_stem_left_inner' not in parents and 'back_stem_right_inner' not in parents
assert parents['rear_stalk'] == 'body'
assert parents['rear_stalk_tip'] == 'rear_stalk'
for side in ['left','right']:
    assert parents['rear_fork_'+side] == 'rear_stalk_tip'
    assert parents['rear_fork_'+side+'_leaf'] == 'rear_fork_'+side

# The correction must preserve the artist data outside the leaf/stem assembly.
old_path=HERE/'versions/before_leaf_correction/sarracenia.bbmodel'
if old_path.exists():
    old=json.loads(old_path.read_text())
    old_texture=Image.open(io.BytesIO(base64.b64decode(old['textures'][0]['source'].split(',',1)[1])))
    for old_cube in old['elements']:
        if old_cube['name'].startswith('back_stem_'):continue
        assert cubes[old_cube['uuid']]==old_cube, 'Unrelated cube changed: '+old_cube['name']
        for face in old_cube['faces'].values():
            rect=tuple(face['uv'])
            new_texture=Image.open(HERE/'sarracenia.png')
            assert old_texture.crop(rect).tobytes()==new_texture.crop(rect).tobytes(), 'Unrelated texture changed'

png = base64.b64decode(project['textures'][0]['source'].split(',', 1)[1])
texture = Image.open(io.BytesIO(png)).convert('RGBA')
assert png == (HERE / 'sarracenia.png').read_bytes(), 'External texture differs'
width, height = texture.size
assert project['resolution'] == {'width': width, 'height': height}
occupied = set()
for cube in cubes.values():
    assert all(b > a for a, b in zip(cube['from'], cube['to']))
    for field in ('from', 'to', 'origin', 'rotation'):
        assert all(math.isfinite(n) for n in cube[field]), 'Invalid coordinate'
    assert len(cube['faces']) == 6
    for face in cube['faces'].values():
        assert face['texture'] == 0
        x0, y0, x1, y1 = face['uv']
        assert 0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height
        for y in range(y0, y1):
            for x in range(x0, x1):
                assert (x, y) not in occupied, 'Overlapping UV islands'
                assert texture.getpixel((x, y))[3] == 255, 'Unpainted face'
                occupied.add((x, y))

geometry = json.loads((HERE / 'sarracenia.geo.json').read_text())['minecraft:geometry'][0]
assert geometry['description']['identifier'] == 'geometry.archecraft.sarracenia'
assert len(geometry['bones']) == len(groups)
assert sum(len(b.get('cubes', [])) for b in geometry['bones']) == len(cubes)
print(f'Validated {len(cubes)} cuboids, {len(groups)} bones, two swept-back tendrils and a shared forked rear stalk, '
      f'{len(cubes) * 6} painted faces, matching embedded PNG, and geometry export.')
