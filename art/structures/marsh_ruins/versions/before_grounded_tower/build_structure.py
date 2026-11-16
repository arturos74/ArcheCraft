"""Reproducible vanilla-block marsh ruin, authored for Java 1.21.1.

Coordinates are local to the template. The front entrance faces north (-Z).
No entities, training targets, palisades or modded blocks are included.
"""
from pathlib import Path
from collections import Counter
import gzip
import hashlib
import json
import math
import random
import struct
from swamp_ecology import decorate,patch_water

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SIZE = (48, 36, 48)
SEED = 731204
rng = random.Random(SEED)
blocks = {}
ground = {}


def put(x, y, z, name, **properties):
    assert 0 <= x < SIZE[0] and 0 <= y < SIZE[1] and 0 <= z < SIZE[2], (x, y, z)
    blocks[x, y, z] = ('minecraft:' + name, tuple(sorted((k, str(v).lower()) for k, v in properties.items())))


def name_at(x, y, z):
    return blocks.get((x, y, z), ('minecraft:air', ()))[0].split(':')[1]


def water_at(x, y, z):
    name, properties = blocks.get((x, y, z), ('minecraft:air', ()))
    return name == 'minecraft:water' or dict(properties).get('waterlogged') == 'true'


def box(x0, y0, z0, x1, y1, z1, name, **properties):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                put(x, y, z, name, **properties)


def stone():
    return rng.choices(['stone_bricks', 'mossy_stone_bricks', 'cracked_stone_bricks', 'mossy_cobblestone', 'andesite'], [3, 5, 3, 3, 1])[0]


def stair(x, y, z, facing='south', material='mossy_stone_brick_stairs', half='bottom'):
    put(x, y, z, material, facing=facing, half=half, shape='straight', waterlogged=False)


def slab(x, y, z, material='mossy_stone_brick_slab', type='bottom'):
    put(x, y, z, material, type=type, waterlogged=False)


def surface(x, z):
    return ground[x, z]


def set_surface(x, z, y, material):
    for yy in range(y):
        if name_at(x, yy, z) in ('air', 'water', 'short_grass', 'tall_grass', 'fern'):
            put(x, yy, z, 'dirt' if yy > 2 else 'stone')
    put(x, y, z, material)
    ground[x, z] = y


# Broad, mostly dry clearings surround the terraced northeast hillside.
for x in range(48):
    for z in range(48):
        wave = math.sin(x * .27) + .7 * math.cos(z * .31) + .5 * math.sin((x + z) * .22)
        height = 5 + (1 if wave > .70 else 0)
        hill = max(0., 1 - ((x - 37.5) / 16) ** 2 - ((z - 36) / 18) ** 2)
        edge = min(1., (47 - x) / 4, (47 - z) / 4)
        height = max(height, 5 + int(11 * hill * max(0, edge)))
        if 29 <= x <= 43 and 30 <= z <= 43:
            height = max(height, 14)
        ground[x, z] = height
        for y in range(height + 1):
            material = 'stone' if y < height - 3 else 'dirt'
            if y == height:
                material = 'grass_block'
            put(x, y, z, material)

# Two smaller puddles leave dry corridors for future mobs. Waterlogged bottom
# slabs provide a solid half-block-deep bed instead of a full water-block drop.
for x in range(3, 43):
    for z in range(2, 31):
        pond = ((x - 32) / 8) ** 2 + ((z - 10) / 9) ** 2 < 1
        pool = ((x - 9) / 4.5) ** 2 + ((z - 8) / 5.5) ** 2 < 1
        island = ((x - 22) / 5) ** 2 + ((z - 17) / 4) ** 2 < 1
        if (pond or pool) and not island and surface(x, z) <= 6 and patch_water(x,z,True):
            put(x, 4, z, 'mud')
            put(x, 5, z, 'mud_brick_slab', type='bottom', waterlogged=True)
            for y in range(6, surface(x, z) + 1):
                put(x, y, z, 'air')
            ground[x, z] = 5


def path(points, width=1.7):
    for (ax, az), (bx, bz) in zip(points, points[1:]):
        count = max(abs(bx - ax), abs(bz - az)) * 3
        for i in range(count + 1):
            px, pz = ax + (bx - ax) * i / count, az + (bz - az) * i / count
            for x in range(max(1, int(px - width)), min(47, int(px + width) + 2)):
                for z in range(max(1, int(pz - width)), min(47, int(pz + width) + 2)):
                    if (x - px) ** 2 + (z - pz) ** 2 > width ** 2:
                        continue
                    y = max(5, surface(x, z))
                    material = rng.choices(['coarse_dirt', 'gravel', 'mossy_cobblestone', 'stone_bricks', 'mossy_stone_bricks', 'grass_block'], [4, 3, 3, 2, 3, 1])[0]
                    set_surface(x, z, y, material)


path([(26, 1), (25, 8), (28, 15), (31, 20), (35, 23)])
path([(26, 9), (17, 10), (13, 16), (14, 23), (18, 29)], 1.8)
path([(14, 23), (23, 25), (32, 23)], 1.25)

# Worn masonry steps ascend to the house, with a broken retaining wall.
for z in range(20, 30):
    y = 6 + z - 20
    for x in range(34, 38):
        for yy in range(y):
            put(x, yy, z, stone() if yy >= y - 2 else 'dirt')
        stair(x, y, z, 'south', rng.choice(['stone_brick_stairs', 'mossy_stone_brick_stairs']))
        ground[x, z] = y
        for yy in range(y + 1, 20):
            put(x, yy, z, 'air')
    for x in (33, 38):
        for yy in range(max(5, surface(x, z)), y + 1):
            put(x, yy, z, stone())
        if z % 3 != 0:
            slab(x, y + 1, z)
for x in range(29, 44):
    for z in (29, 30):
        if 34 <= x <= 37:
            continue
        for y in range(surface(x, z), 15):
            put(x, y, z, stone())
        if z == 29 and x % 4 != 0:
            put(x, 15, z, stone())
            slab(x, 16, z)

# Six broken columns mark the remains of a smaller courtyard.
columns = [(9, 19, 5), (17, 19, 7), (10, 26, 8), (19, 27, 5), (14, 31, 6), (22, 24, 4)]
for cx, cz, height in columns:
    base = max(6, surface(cx, cz))
    for x in range(cx - 1, cx + 2):
        for z in range(cz - 1, cz + 2):
            set_surface(x, z, base, stone())
    for y in range(base + 1, base + height + 1):
        put(cx, y, cz, stone() if y % 3 else 'chiseled_stone_bricks')
    for dx, dz, facing in [(-1, 0, 'east'), (1, 0, 'west'), (0, -1, 'south'), (0, 1, 'north')]:
        stair(cx + dx, base + 1, cz + dz, facing)
    slab(cx, base + height + 1, cz, 'stone_brick_slab')
    for i in range(3):
        x, z = cx + rng.choice([-2, 2]), cz + rng.choice([-2, -1, 1, 2])
        slab(x, max(6, surface(x, z)) + 1, z, rng.choice(['stone_brick_slab', 'mossy_cobblestone_slab']))
for x in range(10, 19):
    if x % 4 != 0:
        put(x, max(6, surface(x, 28)) + 1, 28, stone())

# Open pavilion: stone plinth, corner/side posts, beams and a deep tiled roof.
box(29, 14, 31, 42, 14, 43, 'mossy_stone_bricks')
box(30, 15, 32, 41, 15, 42, 'spruce_planks')
box(30, 16, 32, 41, 26, 42, 'air')
for x in (30, 41):
    for z in (32, 37, 42):
        box(x, 16, z, x, 20, z, 'dark_oak_log', axis='y')
for z in (32, 37, 42):
    box(30, 20, z, 41, 20, z, 'dark_oak_log', axis='x')
for x in (30, 41):
    box(x, 20, 32, x, 20, 42, 'dark_oak_log', axis='z')
box(31, 15, 30, 40, 15, 31, 'spruce_planks')
for x in (31, 40):
    box(x, 16, 30, x, 20, 30, 'dark_oak_log', axis='y')
    stair(x, 19, 31, 'south', 'dark_oak_stairs', 'top')
for x in (32, 39):
    put(x, 19, 31, 'lantern', hanging=True, waterlogged=False)
    put(x, 20, 31, 'dark_oak_log', axis='x')

# Dark tiled roof; the gable ends stay open and eaves curl at the corners.
for x in range(28, 44):
    distance = min(x - 28, 43 - x)
    y = 21 + distance // 2
    for z in range(29, 45):
        facing = 'east' if x <= 35 else 'west'
        stair(x, y, z, facing, 'deepslate_tile_stairs')
        if x in (28, 43) and z in (29, 44):
            slab(x, y + 1, z, 'deepslate_tile_slab')
for z in range(29, 45):
    slab(35, 25, z, 'deepslate_tile_slab')
    slab(36, 25, z, 'deepslate_tile_slab')

# Furniture under the pavilion roof; containers start empty for editing.
put(32, 16, 40, 'crafting_table')
put(33, 16, 40, 'furnace', facing='north', lit=False)
put(39, 16, 40, 'barrel', facing='up', open=False)
put(38, 16, 40, 'chest', facing='north', type='single', waterlogged=False)
put(31, 16, 38, 'brown_bed', facing='south', part='foot', occupied=False)
put(31, 16, 39, 'brown_bed', facing='south', part='head', occupied=False)
box(38, 16, 34, 39, 16, 34, 'bookshelf')
box(34, 19, 37, 37, 19, 37, 'dark_oak_log', axis='x')
put(35, 18, 37, 'lantern', hanging=True, waterlogged=False)
box(34, 16, 37, 36, 16, 38, 'brown_carpet')

# A jagged, mossy lookout ruin rises behind the east end of the roof.
for x in range(42, 47):
    for z in range(40, 46):
        base = max(14, surface(x, z))
        for y in range(base, 21):
            put(x, y, z, stone())
        if x in (42, 46) or z in (40, 45):
            top = 28 + (1 if (x + 2 * z) % 3 == 0 else 0)
            for y in range(21, top):
                if (x, z) == (42, 40) or (x, z) == (46, 45) or y < 25 or rng.random() > .35:
                    put(x, y, z, stone())
            if (x + z) % 2 == 0:
                put(x, top, z, stone())
                slab(x, top + 1, z)
        else:
            put(x, 21, z, 'stone_bricks')
# Narrow lookout slits and rubble soften the tower silhouette.
box(44, 24, 40, 44, 25, 40, 'air')
box(46, 24, 42, 46, 25, 42, 'air')
for x, z in [(29, 28), (40, 25), (44, 26), (26, 33), (27, 38), (41, 19), (7, 33)]:
    base = surface(x, z)
    box(x, base + 1, z, x + 1, base + 2, z + 1, 'mossy_cobblestone')
    slab(x, base + 3, z, 'mossy_cobblestone_slab')


# Natural scenery uses the same swamp palette and tree family as the habitat tiles.
decorate(blocks,ground,731208,[(5,29,'willow'),(23,33,'umbrella'),(8,42,'squat'),(43,13,'forked')])


# Minimal, explicit NBT writer: no third-party dependency or game installation needed.
def payload(tag, value):
    if tag == 3:
        return struct.pack('>i', value)
    if tag == 8:
        raw = value.encode('utf8')
        return struct.pack('>H', len(raw)) + raw
    if tag == 9:
        child, values = value
        return bytes([child]) + struct.pack('>i', len(values)) + b''.join(payload(child, v) for v in values)
    if tag == 10:
        return b''.join(bytes([t]) + payload(8, key) + payload(t, v) for key, (t, v) in value.items()) + b'\0'
    raise ValueError(tag)


def export():
    # Store explicit air so the house and courtyard clear existing vegetation.
    air = ('minecraft:air', ())
    palette = sorted(set(blocks.values()) | {air})
    indices = {state: i for i, state in enumerate(palette)}
    states = []
    for name, properties in palette:
        state = {'Name': (8, name)}
        if properties:
            state['Properties'] = (10, {k: (8, v) for k, v in properties})
        states.append(state)
    records = []
    for y in range(SIZE[1]):
        for z in range(SIZE[2]):
            for x in range(SIZE[0]):
                record = {'pos': (9, (3, [x, y, z])), 'state': (3, indices[blocks.get((x,y,z), air)])}
                records.append(record)
    data = {'DataVersion': (3, 3955), 'size': (9, (3, list(SIZE))), 'palette': (9, (10, states)),
            'blocks': (9, (10, records)), 'entities': (9, (10, [])), 'author': (8, 'ArcheCraft')}
    raw = bytes([10, 0, 0]) + payload(10, data)
    compressed = gzip.compress(raw, mtime=0)
    resource = ROOT / 'src/main/resources/data/archecraft/structure/marsh_ruins.nbt'
    resource.parent.mkdir(parents=True, exist_ok=True)
    resource.write_bytes(compressed)
    (HERE / 'marsh_ruins.nbt').write_bytes(compressed)
    counts = Counter(state[0] for state in blocks.values() if state[0] != 'minecraft:air')
    manifest = dict(name='archecraft:marsh_ruins', size=list(SIZE), seed=SEED,
                    source='art/structures/marsh_ruins/build_structure.py', template=str(resource.relative_to(ROOT)).replace('\\','/'),
                    sha256=hashlib.sha256(compressed).hexdigest(), palette_states=len(palette),
                    non_air_blocks=sum(counts.values()), block_counts=dict(sorted(counts.items())),
                    water_level=5, house_floor=15, entrance=[35,16,32],
                    water_columns=sum(water_at(x,5,z) for x in range(48) for z in range(48)), pond_depth_blocks=.5,
                    notes='Open-sided pavilion with roof/posts and no walls, glass or doors. Smaller half-block-deep puddles and broad dry clearings. Vanilla blocks only; no entities, training dummies, spikes or custom models. Empty editable containers. Front faces north.')
    (HERE / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Exported {SIZE}: {manifest["non_air_blocks"]} non-air blocks, {len(palette)} states, {len(compressed)} compressed bytes.')


if __name__ == '__main__':
    export()
