"""Rebuild the editable model, Java model, original pixel atlas, and preview."""
from pathlib import Path
import base64
import io
import json
import math
import random
import uuid
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ASSETS = ROOT / 'src/main/resources/assets/archecraft'
rng = random.Random(417)

# Four stone and four mineral tiles. Original pixel art, no extracted game assets.
atlas = Image.new('RGBA', (64, 32))
for tile in range(8):
    ox, oy = (tile % 4) * 16, (tile // 4) * 16
    ore = tile >= 4
    for y in range(16):
        for x in range(16):
            n = rng.choice([-6, -3, 0, 0, 2, 4, 7])
            band = [3, 3, 0, -3, -5, 1, 2, 0][(y + tile) % 8]
            c = (38+n+band, 40+n+band, 39+n+band)
            atlas.putpixel((ox+x, oy+y), (*c, 255))
    d = ImageDraw.Draw(atlas)
    # Short horizontal fractures reinforce the sedimentary/blocky layering.
    for _ in range(10):
        x, y = rng.randrange(14), rng.randrange(16)
        d.line((ox+x, oy+y, ox+min(15,x+rng.randrange(2,5)), oy+y), fill=(23,25,25))
    if ore:
        # Branching red ore ribbons; bright edges and sparse silver inclusions.
        x = rng.randrange(4,11)
        for y in range(16):
            x = max(2, min(13, x+rng.choice([-1,0,0,1])))
            d.rectangle((ox+x-1,oy+y,ox+x+1,oy+y), fill=(87,30,32))
            d.point((ox+x,oy+y), fill=rng.choice([(151,48,43),(183,66,52),(126,39,37)]))
            if y % 4 == 0:
                d.line((ox+x,oy+y,ox+min(15,x+4),oy+y), fill=(115,39,37))
        for _ in range(5):
            x,y = rng.randrange(16),rng.randrange(16)
            d.point((ox+x,oy+y), fill=(159,153,137))
    else:
        for _ in range(5):
            x,y = rng.randrange(16),rng.randrange(16)
            d.line((ox+x,oy+y,ox+min(15,x+1),oy+y), fill=(57,59,55))

# All unrotated cuboids: a broad broken foot, staggered ledges and an offset crown.
# Small overlaps are inside the rock; exposed coplanar faces are avoided.
pieces = [
 ('Foot - main slab', (2,0,2), (14,2,14), 0),
 ('Foot - left broken edge', (0,0,5), (3,2,11), 1),
 ('Foot - right broken edge', (13,0,4), (16,1.5,10), 2),
 ('Foot - front chip', (5,0,0), (11,1.5,3), 3),
 ('Lower ledge - core', (3,2,3), (13,5,13), 1),
 ('Lower ledge - front step', (4,1.5,1), (10,4,4), 0),
 ('Lower ledge - left shoulder', (1,2,6), (4,4,11), 2),
 ('Lower ledge - right shoulder', (12,1.5,5), (15,4,11), 3),
 ('Middle - mineral band', (4,5,4), (12,6,12), 4),
 ('Middle - broad shelf', (3,6,5), (12,8.5,12), 2),
 ('Middle - front broken face', (5,4,2), (11,7,5), 5),
 ('Middle - right buttress', (11,4,7), (14,7,11), 0),
 ('Upper - mineral band', (5,8.5,6), (11,9.5,11), 6),
 ('Upper - offset shelf', (5,9.5,5), (11,12,11), 1),
 ('Upper - left fractured lip', (4,8.5,7), (6,10.5,10), 3),
 ('Crown - mineral edge', (6,12,6), (10,12.75,10), 7),
 ('Crown - tall block', (6,12.75,7), (10,15,10), 2),
 ('Crown - broken tip', (7,15,7), (9,16,9), 0),
 ('Loose fragment - front right', (12,0,1), (15,2,3), 1),
 ('Loose fragment - back left', (0,0,13), (2,1,15), 3),
]
directions = ['north','east','south','west','up','down']
texture_uuid = str(uuid.uuid5(uuid.NAMESPACE_URL,'archecraft:starshard_vein/texture'))
elements, exported = [], []
for i,(name,lo,hi,tile) in enumerate(pieces):
    faces, java_faces = {}, {}
    for j,face in enumerate(directions):
        t = tile if tile >= 4 else (tile+j) % 4
        x,y = (t%4)*16,(t//4)*16
        uv = [x,y,x+16,y+16]
        faces[face] = {'uv':uv,'texture':0}
        java_faces[face] = {'uv':[uv[0]/4,uv[1]/2,uv[2]/4,uv[3]/2],'texture':'#0'}
    ident = str(uuid.uuid5(uuid.NAMESPACE_URL,'archecraft:starshard_vein/'+name))
    elements.append({'name':name,'type':'cube','uuid':ident,'from':lo,'to':hi,
                     'origin':[8,0,8],'rotation':[0,0,0],'box_uv':False,
                     'autouv':0,'color':i%8,'faces':faces})
    exported.append({'name':name,'from':lo,'to':hi,'faces':java_faces})

display = {
 'gui':{'rotation':[30,225,0],'translation':[0,0,0],'scale':[0.625]*3},
 'ground':{'rotation':[0,0,0],'translation':[0,3,0],'scale':[0.25]*3},
 'fixed':{'rotation':[0,0,0],'translation':[0,0,0],'scale':[0.5]*3},
 'thirdperson_righthand':{'rotation':[75,45,0],'translation':[0,2.5,0],'scale':[0.375]*3},
 'firstperson_righthand':{'rotation':[0,45,0],'translation':[0,0,0],'scale':[0.4]*3}
}
buf = io.BytesIO()
atlas.save(buf,format='PNG')
model = {'meta':{'format_version':'4.10','model_format':'java_block','box_uv':False},
 'name':'starshard_vein','model_identifier':'archecraft:starshard_vein',
 'resolution':{'width':64,'height':32},'elements':elements,
 'outliner':[e['uuid'] for e in elements],
 'textures':[{'name':'starshard_vein.png','uuid':texture_uuid,'id':'0',
              'namespace':'archecraft','folder':'block','particle':True,
              'width':64,'height':32,'uv_width':64,'uv_height':32,
              'mode':'bitmap','saved':True,
              'source':'data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode()}],
 'display':display}
java_model = {'credit':'Original layered Starshard Vein model for ArcheCraft',
 'texture_size':[64,32], 'ambientocclusion':True,
 'textures':{'0':'archecraft:block/starshard_vein','particle':'archecraft:block/starshard_vein'},
 'elements':exported,'display':display}
def write_json(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
write_json(HERE/'starshard_vein.bbmodel',model)
write_json(ASSETS/'models/block/starshard_vein.json',java_model)
texture_path = ASSETS/'textures/block/starshard_vein.png'
texture_path.parent.mkdir(parents=True,exist_ok=True)
atlas.save(texture_path)
atlas.save(HERE/'starshard_vein.png')

# Orthographic textured preview of these exact cuboids, with per-pixel depth sorting.
def render(angle):
    yaw, pitch = math.radians(angle),math.radians(23)
    def project(p):
        x,y,z=p[0]-8,p[1],p[2]-8
        horizontal = x*math.cos(yaw)-z*math.sin(yaw)
        forward = x*math.sin(yaw)+z*math.cos(yaw)
        return (260+horizontal*23,480-y*math.cos(pitch)*23+forward*math.sin(pitch)*23,
                forward*math.cos(pitch)+y*math.sin(pitch))
    quads=[]
    for elem in elements:
        x0,y0,z0=elem['from'];x1,y1,z1=elem['to']
        surfaces={
         'north':([(x1,y1,z0),(x0,y1,z0),(x0,y0,z0),(x1,y0,z0)],(0,0,-1),0.75),
         'south':([(x0,y1,z1),(x1,y1,z1),(x1,y0,z1),(x0,y0,z1)],(0,0,1),0.88),
         'east': ([(x1,y1,z1),(x1,y1,z0),(x1,y0,z0),(x1,y0,z1)],(1,0,0),0.76),
         'west': ([(x0,y1,z0),(x0,y1,z1),(x0,y0,z1),(x0,y0,z0)],(-1,0,0),0.86),
         'up':   ([(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)],(0,1,0),1.15),
        }
        camera=(math.sin(yaw)*math.cos(pitch),math.sin(pitch),math.cos(yaw)*math.cos(pitch))
        for face,(v,normal,shade) in surfaces.items():
            if sum(a*b for a,b in zip(normal,camera))<=0: continue
            uv=elem['faces'][face]['uv']
            for py in range(16):
                for px in range(16):
                    pts=[]
                    for u,w in [(px/16,py/16),((px+1)/16,py/16),((px+1)/16,(py+1)/16),(px/16,(py+1)/16)]:
                        p=[v[0][k]+u*(v[1][k]-v[0][k])+w*(v[3][k]-v[0][k]) for k in range(3)]
                        pts.append(project(p))
                    color=atlas.getpixel((uv[0]+px,uv[1]+py))
                    quads.append((sum(p[2] for p in pts)/4,[(p[0],p[1]) for p in pts],tuple(min(255,int(c*shade)) for c in color[:3])))
    canvas=Image.new('RGB',(520,560),(24,29,34))
    d=ImageDraw.Draw(canvas)
    d.ellipse((105,429,415,525),fill=(17,21,25))
    for _,points,color in sorted(quads,key=lambda q:q[0]): d.polygon(points,fill=color)
    return canvas
preview=Image.new('RGB',(1040,620),(24,29,34))
preview.paste(render(35),(0,45));preview.paste(render(215),(520,45))
d=ImageDraw.Draw(preview)
try:
    title=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',24)
    small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',15)
except OSError:
    title=small=ImageFont.load_default()
d.text((28,15),'STARSHARD VEIN / layered block model',font=title,fill=(223,224,214))
d.text((28,585),'FRONT / 3-QUARTER',font=small,fill=(160,170,176))
d.text((548,585),'REVERSE / 3-QUARTER',font=small,fill=(160,170,176))
preview.save(HERE/'starshard_vein_preview.png')

# Structural checks: editable model and export contain the same 20 bounded cuboids.
assert len(model['elements'])==len(java_model['elements'])==20
assert len(set(model['outliner']))==20
for e,j in zip(elements,exported):
    assert e['from']==j['from'] and e['to']==j['to']
    assert all(0<=a<b<=16 for a,b in zip(e['from'],e['to']))
    for f in directions:
        assert e['faces'][f]['texture']==0
        assert all(0<=v<=16 for v in j['faces'][f]['uv'])
print('Created and validated 20-cube Blockbench model, Java export, 64x32 atlas, and preview.')
