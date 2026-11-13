"""Original stepped limestone smelter, based on the user's ArcheAge reference."""
from pathlib import Path
from PIL import Image, ImageDraw
import sys, random, uuid
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'common'))
from smelter_model import export

rng=random.Random(10491)
atlas=Image.new('RGBA',(128,128))
palette=[(112,110,91),(88,87,71),(151,144,119),(22,27,25),
    (104,75,43),(38,116,123),(53,65,63),(74,182,179),
    (137,58,24),(43,37,30),(131,127,105),(75,79,68),
    (117,114,94),(100,98,79),(125,122,101),(102,103,88)]
for tile,base in enumerate(palette):
    ox,oy=tile%4*32,tile//4*32
    for y in range(32):
        for x in range(32):
            n=rng.choice([-7,-4,-2,0,0,2,4,7])
            if tile in (0,1,2,10,12,13,14,15):
                n+=-17 if (y%8==0 or (x+(y//8%2)*8)%16==0) else 0
            elif tile in (5,7):n+=3-y//4+(x//4)%3*2
            atlas.putpixel((ox+x,oy+y),tuple(max(0,min(255,c+n)) for c in base)+(255,))
    d=ImageDraw.Draw(atlas)
    if tile in (0,1,2,10,12,13,14,15):
        for _ in range(9):
            x,y=rng.randrange(29),rng.randrange(30)
            d.line((ox+x,oy+y,ox+min(31,x+3),oy+min(31,y+2)),fill=tuple(max(0,c-17) for c in base)+(255,))
    if tile in (5,7):
        d.line((ox+1,oy+1,ox+29,oy+1),fill=tuple(min(255,c+30) for c in base)+(255,))

elements=[]
def cube(name,lo,hi,tile,group='Stone oven',top=None,rotation=None):
    dx,dy,dz=[b-a for a,b in zip(lo,hi)];faces={}
    for f in ['north','east','south','west','up','down']:
        w,h=(dx,dz) if f in ('up','down') else (dz,dy) if f in ('east','west') else (dx,dy)
        t=top if f=='up' and top is not None else tile;x,y=t%4*32,t//4*32
        assert 0<w<=32 and 0<h<=32,name
        faces[f]=dict(uv=[x,y,x+w,y+h],texture=0)
    e=dict(name=name,type='cube',uuid=str(uuid.uuid5(uuid.NAMESPACE_URL,'archecraft:smelter/'+str(len(elements)))),
        **{'from':list(lo),'to':list(hi)},origin=[16,0,16],box_uv=False,autouv=0,faces=faces,_group=group)
    if rotation:
        e['origin']=rotation['origin'];e['rotation']=[rotation['angle'] if a==rotation['axis'] else 0 for a in 'xyz']
    elements.append(e)

cube('Low foundation step',(1,0,1),(31,1.5,25),1,'Foundation')
cube('Stone plinth',(1.5,1.5,1.5),(30.5,4,24.5),0,'Foundation',top=12)
def layer(name,x0,x1,z0,z1,y0,y1,corner,tile):
    cube(name+' center',(x0+corner,y0,z0),(x1-corner,y1,z1),tile)
    cube(name+' left shoulder',(x0,y0,z0+corner),(x0+corner,y1,z1-corner),tile)
    cube(name+' right shoulder',(x1-corner,y0,z0+corner),(x1,y1,z1-corner),tile)
layer('Lower masonry course',3,29,2,21,4,11,3,0)
layer('Middle masonry course',4,28,3,20,11,16,3,12)
layer('Upper masonry course',6,26,4,19,16,20,3,14)
layer('Dome crown',9,23,6,17,20,23,2,0)
cube('Flat crown cap',(12,23,8),(20,24.5,15),14,top=12)

cube('Soot-dark lower throat',(13,4.1,21.02),(19,11.5,21.2),3,'Furnace opening')
cube('Soot-dark upper throat',(14,11.5,20.02),(18,13.1,20.2),3,'Furnace opening')
cube('Firebox floor',(13,4.05,21),(19,4.35,24),9,'Furnace opening')
cube('Banked coals',(14,4.35,21.3),(18,4.6,22.4),8,'Furnace opening')
cube('Left arch upright',(11,4,19),(13,11.5,25),10,'Furnace opening',top=2)
cube('Right arch upright',(19,4,19),(21,11.5,25),10,'Furnace opening',top=2)
cube('Left arch haunch',(12,11.5,19),(14,13,25),2,'Furnace opening')
cube('Right arch haunch',(18,11.5,19),(20,13,25),2,'Furnace opening')
cube('Arch keystone',(14,13,19),(18,14.5,25),2,'Furnace opening')
cube('Arch top cap',(13,14.5,19),(19,15.3,24.8),10,'Furnace opening')

chute=dict(axis='x',angle=22.5,origin=[16,2,31])
cube('Sloped pouring channel',(13.5,2,22),(18.5,2.6,31),2,'Pouring channel',rotation=chute)
cube('Channel left wall',(12.5,2,22),(13.5,4,31),10,'Pouring channel',top=2,rotation=chute)
cube('Channel right wall',(18.5,2,22),(19.5,4,31),10,'Pouring channel',top=2,rotation=chute)
cube('Iron stirring rod',(15.7,4.2,19.5),(16.3,4.5,29),6,'Stirring tool',rotation=chute)
cube('Wooden rod grip',(15.4,4,29),(16.6,4.8,30.5),4,'Stirring tool',rotation=chute)

for x,label in [(3,'Left'),(22,'Right')]:
    z=26
    cube(label+' mold bottom',(x,0.15,z),(x+6,0.5,z+5),5,'Ingot molds')
    cube(label+' mold front rim',(x,0.5,z+4.5),(x+6,1.1,z+5),5,'Ingot molds')
    cube(label+' mold back rim',(x,0.5,z),(x+6,1.1,z+0.5),5,'Ingot molds')
    cube(label+' mold left rim',(x,0.5,z+0.5),(x+0.5,1.1,z+4.5),5,'Ingot molds')
    cube(label+' mold right rim',(x+5.5,0.5,z+0.5),(x+6,1.1,z+4.5),5,'Ingot molds')
    cube(label+' cooling archeum ingot',(x+1.2,0.5,z+1.1),(x+4.8,1,z+3.9),7,'Ingot molds')

cube('Side air pipe',(28,11.5,10.5),(31,14,13),11,'Air pipe and flue')
cube('Pipe end collar',(30.4,11.2,10.2),(31.5,14.3,13.3),2,'Air pipe and flue')
cube('Dark pipe bore',(31.51,11.8,10.8),(31.56,13.7,12.7),3,'Air pipe and flue')
cube('Rear flue base',(22.5,16,3.5),(26.5,19,7.5),1,'Air pipe and flue')
cube('Rear iron flue',(23,19,4),(26,28.5,7),11,'Air pipe and flue')
for label,lo,hi in [
    ('front',(22.5,28.5,7),(26.5,29.5,7.5)),('back',(22.5,28.5,3.5),(26.5,29.5,4)),
    ('left',(22.5,28.5,4),(23,29.5,7)),('right',(26,28.5,4),(26.5,29.5,7))]:
    cube('Flue rim '+label,lo,hi,6,'Air pipe and flue')
cube('Flue dark interior',(23,28.3,4),(26,28.4,7),3,'Air pipe and flue')

# Coarse mass envelopes, never the decorative cube list: cheap crosshair outlines.
boxes=[
    [[1,0,0,16,4,16],[3,4,0,16,24,6],[11,4,3,16,15.3,10]],
    [[0,0,0,15,4,16],[0,4,0,13,24,6],[0,4,3,5,15.3,10]],
    [[1,0,1,16,4,16],[3,4,2,16,23,16],[9,23,8,16,24.5,15]],
    [[0,0,1,15,4,16],[0,4,2,13,24.5,16],[6.5,20,3.5,10.5,29.5,7.5]],
]
export(HERE,ROOT,elements,atlas,boxes)
