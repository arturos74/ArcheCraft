"""Install generated cutouts at inventory resolution and build a review sheet."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib, json, shutil

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ASSETS=ROOT/'src/main/resources/assets/archecraft'
sources=json.loads((HERE/'sources.json').read_text())
results=json.loads((ROOT/'build/material-expansion-generated.json').read_text())
generated={item['id']:item for item in results}
assert len(generated)==len(sources)==22
masters=ROOT/'build/material-expansion-masters'
masters.mkdir(parents=True,exist_ok=True)
manifest=[]
preview=Image.new('RGBA',(1440,800),(29,34,40,255))
draw=ImageDraw.Draw(preview)
font=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',22)
small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',17)
draw.text((25,16),'ARCHECRAFT  /  MATERIAL EXPANSION  /  22 ITEMS',font=font,fill=(231,226,208))
for index,item in enumerate(sources):
    result=generated[item['id']]
    assert result.get('path') and not result.get('error'),result
    source=Path(result['path'])
    master=masters/(item['id']+'.png')
    shutil.copy2(source,master)
    texture=Image.open(master).convert('RGBA').resize((48,48),Image.Resampling.NEAREST)
    alpha=texture.getchannel('A')
    assert alpha.getextrema()[0]==0 and alpha.getextrema()[1]>0,item['id']
    assert all(alpha.getpixel(p)==0 for p in [(0,0),(47,0),(0,47),(47,47)]),item['id']
    texture_path=ASSETS/f'textures/item/{item["id"]}.png'
    texture.save(texture_path)
    record={k:v for k,v in item.items() if k not in ('search','description')}
    record.update(texture_path=str(texture_path.relative_to(ROOT)).replace('\\','/'),
        model_path=f'src/main/resources/assets/archecraft/models/item/{item["id"]}.json',
        dimensions=[48,48],alpha_extrema=list(alpha.getextrema()),
        sha256=hashlib.sha256(texture_path.read_bytes()).hexdigest(),
        image_processing=dict(tool=result['tool'],prompt=result['prompt'],transparent_background=True,
            master_backup_path=str(master.relative_to(ROOT)).replace('\\','/'),
            postprocess='Nearest-neighbor downscale to 48x48, preserving generated alpha.'))
    manifest.append(record)
    x=index%6*240;y=65+index//6*175
    draw.rounded_rectangle((x+10,y,x+230,y+164),radius=8,fill=(37,43,49),outline=(63,72,77))
    preview.alpha_composite(texture.resize((96,96),Image.Resampling.NEAREST),(x+72,y+8))
    label=item['name']
    if draw.textlength(label,font=small)>210:
        words=label.split();lines=[];line=''
        for word in words:
            candidate=(line+' '+word).strip()
            if draw.textlength(candidate,font=small)>210:lines.append(line);line=word
            else:line=candidate
        lines.append(line)
    else:lines=[label]
    for n,line in enumerate(lines):draw.text((x+120,y+112+n*20),line,font=small,anchor='mt',fill=(233,230,218))
    draw.text((x+120,y+153),'DATABASE' if item['source_type']=='database_icon' else 'ORIGINAL',font=small,
        anchor='mm',fill=(137,164,166))
draw.text((25,775),'Transparent 48 x 48 inventory sprites / Recipes and crop growth can be added next.',font=small,fill=(172,182,186))
preview.convert('RGB').save(HERE/'preview.png')
doc=dict(retrieved_on='2026-11-13',notes='22 material items. Sturdy Ingot excluded. 16 database cutouts and 6 original generated icons. '
    'Items and seeds are inventory materials only; recipes, planting and growth are deferred. '
    'Thunderstruck Log uses the global database icon named Thunderstruck Tree.',items=manifest)
(ROOT/'docs/material-expansion-icon-sources.json').write_text(json.dumps(doc,indent=2)+'\n',encoding='utf-8')
print('Installed 22 transparent 48x48 textures; saved preview and complete source/prompt manifest.')
