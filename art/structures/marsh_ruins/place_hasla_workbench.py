"""Add the station to the saved pavilion without regenerating any scenery."""
from pathlib import Path
from collections import Counter
import hashlib,json,shutil
from build_site import read_template,export_template,TILE_SIZE,DATA,AIR

HERE=Path(__file__).resolve().parent
path=HERE/'marsh_ruins.nbt'
assert path.read_bytes()==(DATA/'structure/marsh_ruins.nbt').read_bytes(), 'Inspect differing artist/runtime hubs first'
backup=HERE/'versions/before_hasla_workbench'
if not backup.exists():
    backup.mkdir(parents=True)
    for name in ['marsh_ruins.nbt','hasla_swamp.nbt','manifest.json','site_manifest.json']:
        shutil.copy2(HERE/name,backup/name)
scene,extras=read_template(path)
before=scene.copy();position=(35,16,38)
assert scene[(35,15,38)][0]=='minecraft:spruce_planks'
assert scene[position] in (AIR,('archecraft:hasla_workbench',(('facing','north'),)))
scene[position]=('archecraft:hasla_workbench',(('facing','north'),))
extras[position]={'id':(8,'archecraft:workbench'),'InventoryVersion':(3,2),'Items':(9,(10,[]))}
assert {p for p in scene if scene[p]!=before[p]}<= {position}, 'Scenery changed'
sha=export_template(path,scene,TILE_SIZE,extras)
(DATA/'structure/marsh_ruins.nbt').write_bytes(path.read_bytes())
manifest=json.loads((HERE/'manifest.json').read_text())
counts=Counter(name for name,props in scene.values() if name!='minecraft:air')
manifest.update(name='archecraft:abandoned_drill_camp',sha256=sha,non_air_blocks=sum(counts.values()),
    block_counts=dict(sorted(counts.items())),palette_states=len(set(scene.values())),
    workstation=dict(id='archecraft:hasla_workbench',position=list(position),facing='north'),
    pavilion_interior='Clear wood floor with one Hasla Workbench',
    notes='Hasla Workbench added to the saved open pavilion; all terrain, tower, trees, roof and remaining floor blocks preserved.')
(HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Placed one north-facing Hasla Workbench at pavilion-local (35,16,38); scenery preserved.')
