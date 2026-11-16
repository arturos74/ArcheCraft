"""Write item names and flat inventory models from the expansion catalog."""
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ASSETS=ROOT/'src/main/resources/assets/archecraft'
items=json.loads((HERE/'items.json').read_text())
lang_path=ASSETS/'lang/en_us.json'
lang=json.loads(lang_path.read_text())
for item in items:
    ident=item['id']
    lang['item.archecraft.'+ident]=item['name']
    path=ASSETS/f'models/item/{ident}.json'
    path.write_text(json.dumps({'parent':'minecraft:item/generated','textures':{'layer0':'archecraft:item/'+ident}},indent=2)+'\n')
lang_path.write_text(json.dumps(lang,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Wrote {len(items)} translations and inventory models.')
