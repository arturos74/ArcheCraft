"""One-block stump-mounted anvil based on the user's reference."""
from pathlib import Path
from PIL import Image, ImageDraw
import random, sys, uuid
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'common'))
from single_workbench_model import export

rng=random.Random(6221)
atlas=Image.new('RGBA',(128,64))
palette=[(89,69,45),(132,111,77),(40,43,44),(70,73,72),
    (105,108,101),(46,59,56),(42,143,154),(77,61,40)]
for tile,base in enumerate(palette):
    ox,oy=tile%4*32,tile//4*32
    for y in range(32):
        for x in range(32):
            n=rng.choice([-5,-2,0,0,2,5])
            if tile==0:n+=-15 if x%6 in (0,1) else (y//7+x//3)%3*3
            if tile==1:
                radius=max(abs(x-8),abs(y-8));n+=-17 if radius%4==0 else 0
            if tile in (2,3,4):n+=4 if y%9==3 else 0
            if tile==6:n+=7-y//2
            atlas.putpixel((ox+x,oy+y),tuple(max(0,min(255,c+n)) for c in base)+(255,))
    d=ImageDraw.Draw(atlas)
    if tile in (2,3,4):
        for _ in range(10):
            x,y=rng.randrange(29),rng.randrange(30)
            d.line((ox+x,oy+y,ox+min(31,x+3),oy+y),fill=tuple(min(255,c+16) for c in base)+(255,))

elements=[]
def cube(name,lo,hi,tile,group='Anvil',top=None,rotation=None):
    dx,dy,dz=[b-a for a,b in zip(lo,hi)];faces={}
    for f in ['north','east','south','west','up','down']:
        w,h=(dx,dz) if f in ('up','down') else (dz,dy) if f in ('east','west') else (dx,dy)
        t=top if f=='up' and top is not None else tile;x,y=t%4*32,t//4*32
        faces[f]=dict(uv=[x,y,x+w,y+h],texture=0)
    e=dict(name=name,type='cube',uuid=str(uuid.uuid5(uuid.NAMESPACE_URL,'archecraft:anvil/'+str(len(elements)))),
        **{'from':list(lo),'to':list(hi)},origin=[8,0,8],box_uv=False,autouv=0,faces=faces,_group=group)
    if rotation:
        e['origin']=rotation['origin'];e['rotation']=[rotation['angle'] if a==rotation['axis'] else 0 for a in 'xyz']
    elements.append(e)

# Square-cut, stepped stump; end grain is distinct from the vertical bark.
cube('Stump central trunk',(2,0,1),(14,8,15),0,'Wooden stump',top=1)
cube('Stump left bark',(1,0.3,3),(2,7.7,13),0,'Wooden stump',top=1)
cube('Stump right bark',(14,0.3,3),(15,7.7,13),0,'Wooden stump',top=1)
cube('Stump left root',(0.8,0,5),(2.3,1.2,10),7,'Wooden stump')
cube('Stump right root',(13.7,0,5),(15.2,1.2,10),7,'Wooden stump')
cube('Anvil broad foot',(4,8,4.5),(11,9,11.5),2,top=3)
cube('Anvil lower shoulder',(4.7,9,5.3),(10.3,10,10.7),3)
cube('Anvil narrow waist',(5.5,10,6.3),(9.5,12,9.7),2)
cube('Anvil upper shoulder',(4.7,12,5.7),(10.3,13,10.3),3)
cube('Anvil main body',(3.2,13,5),(11.5,14.5,11),2,top=4)
cube('Anvil working face',(2.5,14.5,4.7),(12,15.3,11.3),3,top=4)
cube('Squared heel',(1,13.4,5.1),(3.2,14.5,10.9),2)
cube('Heel face',(1,14.5,4.7),(2.5,15.3,11.3),3,top=4)
cube('Horn shoulder',(11.5,13.4,5.7),(13.4,14.8,10.3),2,top=3)
cube('Horn taper',(13.4,13.6,6.4),(14.5,14.5,9.6),2,top=3)
cube('Horn pointed end',(14.5,13.8,7.3),(15.7,14.2,8.7),2,top=3)

# These are decorative props on the bench, independent of the crafted item's art.
cube('Forged blue blade',(4.2,15.3,7.4),(13.8,15.65,8.6),6,'Display blade')
cube('Blade point',(13.8,15.3,7.75),(14.9,15.55,8.25),6,'Display blade')
cube('Sword guard',(3.8,15.3,6.5),(4.3,15.9,9.5),4,'Display blade')
cube('Sword grip',(1.5,15.35,7.5),(3.8,15.85,8.5),5,'Display blade')
cube('Sword pommel',(1,15.25,7.3),(1.5,15.95,8.7),4,'Display blade')

hammer=dict(axis='z',angle=22.5,origin=[11,1.5,15.2])
cube('Hanging hammer handle',(10.65,1.5,14.9),(11.35,6.7,15.4),7,'Hanging tools',rotation=hammer)
cube('Hammer iron head',(9.5,6.7,14.7),(12.5,7.9,15.9),3,'Hanging tools',top=4,rotation=hammer)
cube('Tool hook',(10.5,7.6,14.7),(11.5,8.1,15.5),2,'Hanging tools')
cube('Tongs left handle',(3.8,1.4,14.9),(4.2,5.5,15.3),3,'Hanging tools')
cube('Tongs right handle',(5.5,1.4,14.9),(5.9,5.5,15.3),3,'Hanging tools')
cube('Tongs pivot',(4.1,5.5,14.9),(5.6,6,15.4),4,'Hanging tools')
cube('Tongs left jaw',(4.4,6,14.9),(4.8,7,15.3),3,'Hanging tools')
cube('Tongs right jaw',(5,6,14.9),(5.4,7,15.3),3,'Hanging tools')

boxes=[[0.8,0,1,15.2,8,15.5],[4,8,4.5,11,13,11.5],[1,13,4.7,15.7,16,11.3]]
export(HERE,ROOT,'anvil','AnvilWorkbenchShapes',elements,atlas,boxes,'ANVIL')
