"""Alchemy table authored for a two-block footprint from the supplied reference."""
from pathlib import Path
from PIL import Image, ImageDraw
import sys, random, uuid

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'common'))
from workbench_model import export_two_block

rng=random.Random(5724)
atlas=Image.new('RGBA',(128,64))
palette=[(61,57,34),(84,65,38),(231,222,188),(224,215,178),
         (54,200,217),(57,72,66),(129,96,41),(170,224,211)]
for tile,base in enumerate(palette):
    ox,oy=tile%4*32,tile//4*32
    for y in range(32):
        for x in range(32):
            n=rng.choice([-3,-1,0,0,1,3])
            if tile in (0,1):n+=-9 if y%6==0 else 0
            if tile in (4,7):n+=5-y//5+(x//6)%2*3
            atlas.putpixel((ox+x,oy+y),tuple(max(0,min(255,c+n)) for c in base)+(255,))
    d=ImageDraw.Draw(atlas)
    if tile in (0,1):
        for _ in range(15):
            x,y=rng.randrange(28),rng.randrange(32)
            d.line((ox+x,oy+y,ox+min(31,x+rng.randrange(3,9)),oy+y),fill=(base[0]-15,base[1]-13,base[2]-8,255))
    if tile==2:
        for y in range(3,24,3):
            d.line((ox+2,oy+y,ox+12-rng.randrange(3),oy+y),fill=(116,103,74,255))
            d.point((ox+5,oy+y+1),fill=(145,128,88,255))
    if tile==3:
        ink=(118,113,79,255)
        d.ellipse((ox+3,oy+3,ox+12,oy+12),outline=ink)
        d.line((ox+7,oy+2,ox+7,oy+14),fill=ink)
        d.line((ox+1,oy+8,ox+14,oy+8),fill=ink)
        d.line((ox+3,oy+4,ox+11,oy+12),fill=ink)
        for y in [17,20,23]:d.line((ox+2,oy+y,ox+12,oy+y),fill=ink)

elements=[]
def cube(name,lo,hi,tile,group='Table frame',top=None,density=1,rotation=None):
    dx,dy,dz=[b-a for a,b in zip(lo,hi)];faces={}
    for f in ['north','east','south','west','up','down']:
        w,h=(dx,dz) if f in ('up','down') else (dz,dy) if f in ('east','west') else (dx,dy)
        t=top if f=='up' and top is not None else tile;x,y=t%4*32,t//4*32
        assert w*density<=32 and h*density<=32,name
        faces[f]=dict(uv=[x,y,x+w*density,y+h*density],texture=0)
    e=dict(name=name,type='cube',uuid=str(uuid.uuid5(uuid.NAMESPACE_URL,'archecraft:alchemy/'+str(len(elements)))),
           **{'from':list(lo),'to':list(hi)},origin=[16,0,8],box_uv=False,autouv=0,faces=faces,_group=group)
    if rotation:
        e['origin']=rotation['origin'];e['rotation']=[rotation['angle'] if a==rotation['axis'] else 0 for a in 'xyz']
    elements.append(e)

for x,label in [(1.5,'Left'),(28,'Right')]:
    for z,side in [(2,'back'),(11.5,'front')]:
        cube(f'{label} {side} leg',(x,0,z),(x+2.5,11.5,z+2.5),1)
cube('Front apron',(1,9,12),(31,11,14),1)
cube('Back apron',(1,9,2),(31,11,4),1)
cube('Left lower stretcher',(2,3,3),(3.5,4.5,13),0)
cube('Right lower stretcher',(28.5,3,3),(30,4.5,13),0)
cube('Long lower brace',(3.5,3,7),(28.5,4.5,8.5),0)
for i in range(5):
    z=0.5+3*i
    cube(f'Dark tabletop plank {i+1}',(0.5,11.5,z),(31.5,13,z+2.9),0,'Tabletop')
cube('Left tabletop end',(0,11,0.5),(1,13,15.4),1,'Tabletop')
cube('Right tabletop end',(31,11,0.5),(32,13,15.4),1,'Tabletop')

def flask(name,x,z,width,height,body_height,tile):
    y=13;neck=width*0.25
    cube(name+' liquid chamber',(x,y,z),(x+width,y+body_height,z+width),tile,'Flasks',top=7)
    inset=width*0.18
    cube(name+' shoulders',(x+inset,y+body_height,z+inset),(x+width-inset,y+body_height+1,z+width-inset),7,'Flasks')
    center=x+width/2;cz=z+width/2
    cube(name+' long neck',(center-neck/2,y+body_height+1,cz-neck/2),(center+neck/2,y+height,cz+neck/2),tile,'Flasks')
    cube(name+' glass rim',(center-neck/2-0.2,y+height-0.5,cz-neck/2-0.2),(center+neck/2+0.2,y+height,cz+neck/2+0.2),7,'Flasks')
    cube(name+' cork',(center-neck/2,y+height,cz-neck/2),(center+neck/2,y+height+0.6,cz+neck/2),6,'Flasks')

flask('Tall blue flask',4,3.5,4.5,13,4,4)
flask('Small blue flask',9.5,4,3.2,10,3,4)
flask('Pale reagent flask',7.2,8.1,3.2,9,2.7,7)

cube('Ring stand upright',(2.2,13,3.1),(2.8,21.5,3.7),5,'Distillation stand')
cube('Stand front foot',(1,13,2.5),(4.5,13.5,3.5),5,'Distillation stand')
cube('Stand side foot',(2,13,2),(2.8,13.5,6),5,'Distillation stand')
for name,lo,hi in [
 ('top',(1.5,26,3.1),(3.5,26.5,3.7)),('bottom',(1.5,21.5,3.1),(3.5,22,3.7)),
 ('left',(0.5,23,3.1),(1,25,3.7)),('right',(4,23,3.1),(4.5,25,3.7)),
 ('upper left',(1,25,3.1),(1.5,26,3.7)),('upper right',(3.5,25,3.1),(4,26,3.7)),
 ('lower left',(1,22,3.1),(1.5,23,3.7)),('lower right',(3.5,22,3.1),(4,23,3.7))]:
    cube('Iron hoop '+name,lo,hi,5,'Distillation stand')
cube('Suspended measuring drop',(2.25,19.8,3.1),(2.75,20.8,3.7),5,'Distillation stand')

def bowl(name,x,y,z,width):
    cube(name+' bottom',(x,y,z),(x+width,y+0.4,z+width),5,'Scales and vessels')
    for edge,lo,hi in [
     ('front',(x,y+0.4,z+width-0.35),(x+width,y+0.9,z+width)),
     ('back',(x,y+0.4,z),(x+width,y+0.9,z+0.35)),
     ('left',(x,y+0.4,z+0.35),(x+0.35,y+0.9,z+width-0.35)),
     ('right',(x+width-0.35,y+0.4,z+0.35),(x+width,y+0.9,z+width-0.35))]:
        cube(name+' '+edge,lo,hi,5,'Scales and vessels')
bowl('Mixing bowl',2,13,10,3.5)

book=dict(axis='x',angle=45,origin=[22.5,14,13])
cube('Open book leather cover',(17.5,14,5),(27.5,14.2,13),1,'Open grimoire',rotation=book)
cube('Left parchment leaves',(17.8,14.2,5.25),(22.35,14.45,12.8),2,'Open grimoire',top=3,density=3,rotation=book)
cube('Right parchment leaves',(22.65,14.2,5.25),(27.2,14.45,12.8),2,'Open grimoire',top=2,density=3,rotation=book)
cube('Book central binding',(22.35,14.2,5.15),(22.65,14.5,12.9),6,'Open grimoire',rotation=book)
for x in [18,26.5]:
    cube('Bookstand upright',(x,13,7),(x+1,20.5,8),1,'Bookstand')
    cube('Bookstand cap',(x-0.2,20.5,6.8),(x+1.2,21.2,8.2),6,'Bookstand')
cube('Bookstand top rail',(18,18.6,7),(27.5,19.4,8),1,'Bookstand')
cube('Bookstand front ledge',(17.3,13,12.5),(27.7,14.1,13.8),1,'Bookstand')

cube('Balance base',(27.5,13,12),(31,13.5,15),5,'Scales and vessels')
cube('Balance upright',(29,13.5,13),(29.6,20,13.6),5,'Scales and vessels')
cube('Balance arm',(26,19.5,13),(31.5,20,13.5),5,'Scales and vessels')
cube('Left pan suspension',(26.5,17.5,13.1),(26.8,19.5,13.4),5,'Scales and vessels')
cube('Right pan suspension',(30.6,16,13.1),(30.9,19.5,13.4),5,'Scales and vessels')
bowl('Left weighing pan',25.7,17,12.4,1.8)
bowl('Right weighing pan',29.9,15.5,12.4,1.8)

cube('Ingredient tray bottom',(12,13,11),(16,13.3,14),1,'Loose ingredients')
cube('Tray back',(12,13.3,11),(16,14,11.4),1,'Loose ingredients')
cube('Tray left',(12,13.3,11.4),(12.4,14,14),1,'Loose ingredients')
cube('Tray right',(15.6,13.3,11.4),(16,14,14),1,'Loose ingredients')
for i,(x,z) in enumerate([(13,12),(14.4,12.8),(15.5,14.2),(17,13.8),(16.7,11)]):
    cube(f'Turquoise reagent piece {i+1}',(x,13.3 if x<16 and z<14 else 13,z),
         (x+0.65,14 if x<16 and z<14 else 13.65,z+0.65),4,'Loose ingredients')

# A handful of mass envelopes keeps outline traversal cheap in both halves.
gameplay_boxes=[
 [[1,0,1,16,13,15],[0.5,13,3,13,27,11.5]],
 [[0,0,1,15,13,15],[1.5,13,5.5,12,21.5,13.5],[12,13,11.5,16,20.5,15]],
]
export_two_block(HERE,ROOT,'alchemy_workbench','AlchemyWorkbenchShapes',elements,atlas,gameplay_boxes,'ALCHEMY WORKBENCH')
