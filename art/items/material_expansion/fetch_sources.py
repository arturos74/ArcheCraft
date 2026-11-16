"""Resolve exact database names, preserve originals, and record icon provenance."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib, html, json, re, urllib.parse, urllib.request

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ORIGINALS=ROOT/'build/material-expansion-originals'
ORIGINALS.mkdir(parents=True,exist_ok=True)
items=json.loads((HERE/'items.json').read_text())

def get(url):
    request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(request,timeout=45) as response:return response.read()

def resolve(item):
    result=dict(item)
    try:
        for query in item['search']:
            url='https://archeagecodex.com/query.php?a=search&l=us&sq='+urllib.parse.quote(query)
            data=json.loads(get(url))
            rows=data.get('aaData',data.get('data',[])) if isinstance(data,dict) else data
            for row in rows:
                if not isinstance(row,list) or len(row)<3:continue
                name=html.unescape(re.sub('<[^>]*>','',str(row[2]))).strip()
                if name.casefold()!=query.casefold() or '/us/item/' not in str(row[2]):continue
                match=re.search(r'src=[\"\'](/items/[^\"\']+\.png)',str(row[1]))
                if not match:continue
                image_url='https://archeagecodex.com'+match.group(1)
                image=get(image_url);path=ORIGINALS/(item['id']+'.png');path.write_bytes(image)
                result.update(database_name=name,database_id=row[0],page_url='https://archeagecodex.com/us/item/'+str(row[0])+'/',
                    image_url=image_url,original_path=str(path.relative_to(ROOT)).replace('\\','/'),
                    original_sha256=hashlib.sha256(image).hexdigest(),source_type='database_icon')
                return result
        result['source_type']='original_generated_icon'
    except Exception as error:
        result.update(source_type='original_generated_icon',lookup_error=str(error))
    return result

with ThreadPoolExecutor(max_workers=6) as pool:resolved=list(pool.map(resolve,items))
(HERE/'sources.json').write_text(json.dumps(resolved,indent=2)+'\n',encoding='utf-8')
for item in resolved:print(item['id']+': '+str(item.get('database_id',item['source_type']))+' '+item.get('database_name',''))
