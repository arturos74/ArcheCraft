"""Refresh only the saved hub's natural scenery, preserving its built structures."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import argparse
from build_site import read_template,export_template,TILE_SIZE,DATA,AIR
from swamp_ecology import decorate,patch_water,FLORA,NATURAL_GROUND

HERE=Path(__file__).resolve().parent
path=HERE/'marsh_ruins.nbt'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source',type=Path,default=path,help='Saved hub to decorate; defaults to the current art copy')
scene,extras=read_template(parser.parse_args().source)
built={pos:state for pos,state in scene.items() if state[0].split(':')[1] not in
       FLORA|NATURAL_GROUND|{'air','dirt','oak_log','oak_leaves','mangrove_log','mangrove_leaves','azalea_leaves','flowering_azalea_leaves','mud_brick_slab'}}
for pos,(name,props) in list(scene.items()):
    if name.split(':')[1] in FLORA|{'oak_log','oak_leaves','mangrove_log','mangrove_leaves','azalea_leaves','flowering_azalea_leaves'}:
        scene[pos]=AIR
heights={}
for x in range(48):
    for z in range(48):
        candidates=[y for y in range(20) if scene.get((x,y,z),AIR)[0].split(':')[1] in NATURAL_GROUND|{'dirt','mud_brick_slab'}]
        heights[x,z]=max(candidates,default=5)
        if dict(scene.get((x,5,z),AIR)[1]).get('waterlogged')=='true' and not patch_water(x,z,True):
            scene[x,5,z]=('minecraft:grass_block',());heights[x,z]=5
stats=decorate(scene,heights,731208,[(5,29,'willow'),(23,33,'umbrella'),(8,42,'squat'),(43,13,'forked')])
assert all(scene[pos]==state for pos,state in built.items()),'Built architecture changed during scenery pass'
sha=export_template(path,scene,TILE_SIZE,extras)
(DATA/'structure/marsh_ruins.nbt').write_bytes(path.read_bytes())
manifest=json.loads((HERE/'manifest.json').read_text())
counts=Counter(name for name,props in scene.values() if name!='minecraft:air')
manifest.update(sha256=sha,non_air_blocks=sum(counts.values()),block_counts=dict(sorted(counts.items())),
                palette_states=len(set(scene.values())),water_columns=sum(dict(props).get('waterlogged')=='true' for name,props in scene.values()),
                trees=stats,ecology='Irregular half-block puddles, muddy/mossy grass, four tree shapes, supported vines and two-block grasses.')
(HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Refreshed hub scenery; pavilion, masonry, furnishings and paths preserved.')
