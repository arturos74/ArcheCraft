"""Ground the saved tower and empty the pavilion without rebuilding its scenery."""
from pathlib import Path
from collections import Counter
import json
import random
from build_site import read_template,export_template,TILE_SIZE,DATA,AIR
from swamp_ecology import FLORA

HERE=Path(__file__).resolve().parent
path=HERE/'marsh_ruins.nbt'
scene,extras=read_template(path)
rng=random.Random(731209)
def at(x,y,z):return scene.get((x,y,z),AIR)[0].split(':')[1]
def masonry():return ('minecraft:'+rng.choice(['stone_bricks','mossy_stone_bricks','mossy_cobblestone']),())

filled=0
for x in range(42,47):
    for z in range(40,46):
        # The old tower started at Y=14 even where the hillside fell away.
        # Continue each column until it meets the existing solid ground.
        y=13
        while y>=0 and at(x,y,z) in FLORA|{'air','water'}:
            scene[x,y,z]=masonry();extras.pop((x,y,z),None);filled+=1;y-=1
        # Connect jagged battlements to the wall below, retaining the two slits.
        if x in (42,46) or z in (40,45):
            occupied=[y for y in range(21,32) if at(x,y,z) not in FLORA|{'air'}]
            if occupied:
                for y in range(21,max(occupied)):
                    if (x,z,y) in [(44,40,24),(44,40,25),(46,42,24),(46,42,25)]:continue
                    if at(x,y,z)=='air':scene[x,y,z]=masonry();filled+=1

removed=0
furniture={'bookshelf','brown_bed','chest','barrel','crafting_table','furnace','brown_carpet'}
for (x,y,z),state in list(scene.items()):
    interior=31<=x<=40 and 33<=z<=41 and 16<=y<=19
    item=30<=x<=41 and 32<=z<=42 and state[0].split(':')[1] in furniture
    if (interior or item) and state!=AIR and state[0]!='archecraft:hasla_workbench':
        scene[x,y,z]=AIR;extras.pop((x,y,z),None);removed+=1
for x in range(31,41):
    for z in range(33,42):
        assert at(x,15,z)=='spruce_planks'
        assert all(at(x,y,z)=='air' or (x,y,z)==(35,16,38) and at(x,y,z)=='hasla_workbench' for y in range(16,20))
for x in range(42,47):
    for z in range(40,46):assert all(at(x,y,z) not in FLORA|{'air','water'} for y in range(21))

sha=export_template(path,scene,TILE_SIZE,extras)
(DATA/'structure/marsh_ruins.nbt').write_bytes(path.read_bytes())
manifest=json.loads((HERE/'manifest.json').read_text())
counts=Counter(name for name,props in scene.values() if name!='minecraft:air')
manifest.update(sha256=sha,non_air_blocks=sum(counts.values()),block_counts=dict(sorted(counts.items())),
                palette_states=len(set(scene.values())),tower_grounded=True,pavilion_interior='Clear wood floor with reserved Hasla Workbench position',
                notes='Open pavilion with wood floor, Hasla Workbench if present, structural frame and roof. Tower columns extend to the hillside; natural swamp scenery retained.')
(HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(f'Grounded/connected {filled} tower blocks; removed {removed} interior furnishing/decor blocks. Scenery retained.')
