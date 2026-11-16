"""One-block carved jade Hasla weapon altar, based on the user's reference."""
from pathlib import Path
from PIL import Image,ImageDraw
import math,random,sys,uuid

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'common'))
from single_workbench_model import export

rng=random.Random(731215)
atlas=Image.new('RGBA',(128,64))
palette=[(25,78,63),(36,113,88),(12,40,35),(22,33,34),
         (31,99,77),(74,145,111),(86,210,222),(19,60,63)]
for tile,base in enumerate(palette):
    ox,oy=tile%4*32,tile//4*32
    for y in range(32):
        for x in range(32):
            noise=rng.choice([-5,-2,0,0,2,5])
            if tile in (0,1,4):
                noise+=5 if math.sin(x*.7+y*.36)+math.cos(y*.9-x*.2)>1 else -4
            if tile==3:noise+=3 if y%9==0 else 0
            if tile==6:noise+=10-y//2
            atlas.putpixel((ox+x,oy+y),tuple(max(0,min(255,c+noise)) for c in base)+(255,))
    if tile==4:
        d=ImageDraw.Draw(atlas)
        # Repeating, stepped carved curls with dark recesses and green edges.
        for yy in range(0,32,12):
            for xx in range(0,32,12):
                pts=[(xx+1,yy+9),(xx+1,yy+2),(xx+9,yy+2),(xx+9,yy+8),(xx+5,yy+8),(xx+5,yy+5)]
                pts=[(ox+min(31,x),oy+min(31,y)) for x,y in pts]
                d.line(pts,fill=(12,54,44,255),width=2)
                d.line([(x+1 if x<ox+31 else x,y) for x,y in pts],fill=(63,143,107,255),width=1)

elements=[]
def cube(name,lo,hi,tile,group='Carved stone',top=None,rotation=None):
    dx,dy,dz=[b-a for a,b in zip(lo,hi)];faces={}
    for f in ['north','east','south','west','up','down']:
        w,h=(dx,dz) if f in ('up','down') else (dz,dy) if f in ('east','west') else (dx,dy)
        t=top if f=='up' and top is not None else tile;x,y=t%4*32,t//4*32
        faces[f]=dict(uv=[x,y,x+w,y+h],texture=0)
    e=dict(name=name,type='cube',uuid=str(uuid.uuid5(uuid.NAMESPACE_URL,'archecraft:hasla_workbench/'+name)),
           **{'from':list(lo),'to':list(hi)},origin=[8,0,8],box_uv=False,autouv=0,faces=faces,_group=group)
    if rotation:
        e['origin']=rotation['origin'];e['rotation']=[rotation['angle'] if a==rotation['axis'] else 0 for a in 'xyz']
    elements.append(e)

for x in [1.2,11.2]:
    for z in [1.5,11.5]:
        cube('Carved paw '+str((x,z)),(x,0,z),(x+3.6,2.5,z+3.1),0,'Pedestal feet',top=1)
        for i in range(2):
            cube('Paw groove '+str((x,z,i)),(x+.7+i*1.2,.4,z+2.9),(x+.9+i*1.2,1.5,z+3.2),2,'Pedestal feet')
cube('Pedestal foot',(3,1.5,2.5),(13,4,13.5),0,top=1)
cube('Broad altar body',(2,3,3),(14,12,13),4,top=1)
cube('Left stepped flank',(1,4,4),(2,10.5,12),4)
cube('Right stepped flank',(14,4,4),(15,10.5,12),4)
cube('Front shoulder',(2.5,4,13),(13.5,11,14),4)
cube('Rear shoulder',(2.5,4,2),(13.5,11,3),4)
cube('Narrow upper collar',(2.5,12,3),(13.5,13,13),0,top=1)
cube('Raised working rim',(1.5,13,2.5),(14.5,14.2,13.5),4,top=1)
cube('Dark forging surface',(2,14.2,3),(14,14.65,13),3,'Working surface')
for name,lo,hi in [
    ('Front rim',(1.5,14.2,13),(14.5,14.9,13.6)),
    ('Rear rim',(1.5,14.2,2.4),(14.5,14.9,3)),
    ('Left rim',(1.4,14.2,3),(2,14.9,13)),
    ('Right rim',(14,14.2,3),(14.6,14.9,13))]:cube(name,lo,hi,1,'Working surface')

# A broad feline mask and geometric cheek curls echo the reference's relief.
cube('Forehead crest',(7,10.4,13.8),(9,12.2,14.7),5,'Guardian face')
cube('Left brow',(3.3,9.6,13.8),(7.1,10.7,14.8),1,'Guardian face',rotation=dict(axis='z',angle=-22.5,origin=[7.1,9.6,14]))
cube('Right brow',(8.9,9.6,13.8),(12.7,10.7,14.8),1,'Guardian face',rotation=dict(axis='z',angle=22.5,origin=[8.9,9.6,14]))
for x in [4,10]:cube('Recessed eye '+str(x),(x,8.8,14.3),(x+2,9.35,15),2,'Guardian face')
cube('Nose bridge',(7,7.1,14),(9,10.2,15),0,'Guardian face',top=1)
cube('Left muzzle',(4,5.7,13.9),(7.5,7.8,15.5),1,'Guardian face')
cube('Right muzzle',(8.5,5.7,13.9),(12,7.8,15.5),1,'Guardian face')
cube('Nose',(7.2,6.5,15),(8.8,7.5,15.9),2,'Guardian face',top=5)
cube('Mouth recess',(6,5.25,14.9),(10,5.7,15.35),2,'Guardian face')
cube('Carved jaw',(5,4.5,13.6),(11,5.3,15.1),4,'Guardian face')
for x in [4.6,10.7]:cube('Stone fang '+str(x),(x,4.7,14.4),(x+.7,6.4,15.2),5,'Guardian face')
for side,x in [('Left',2.1),('Right',12.7)]:
    cube(side+' cheek crest',(x,7.3,13.5),(x+1.2,10.6,14.5),1,'Guardian face')
for side,x in [('Left',.7),('Right',14.8)]:
    cube(side+' carved curl upper',(x,9.5,5.3),(x+.5,10.4,10.5),1,'Side reliefs')
    cube(side+' carved curl rear',(x,6.5,5.3),(x+.5,9.5,6.2),1,'Side reliefs')
    cube(side+' carved curl lower',(x,6.5,6.2),(x+.5,7.4,9.4),1,'Side reliefs')
    cube(side+' carved curl inner',(x,7.4,8.5),(x+.5,9,9.4),1,'Side reliefs')

cube('Cyan display blade',(4.3,14.65,7.4),(12.4,15.05,8.5),6,'Display sword')
cube('Blade taper',(12.4,14.7,7.65),(13.5,15.0,8.25),6,'Display sword')
cube('Blade tip',(13.5,14.75,7.85),(14.4,14.95,8.05),6,'Display sword')
cube('Sword guard',(3.8,14.65,6.6),(4.3,15.5,9.3),5,'Display sword')
cube('Sword grip',(2.2,14.7,7.55),(3.8,15.2,8.35),7,'Display sword')
cube('Sword pommel',(1.7,14.65,7.4),(2.2,15.35,8.5),5,'Display sword')

boxes=[[1.2,0,1.5,14.8,3,14.7],[.7,3,2,15.3,13,15.9],[1.4,13,2.4,14.6,15.5,13.6]]
export(HERE,ROOT,'hasla_workbench','HaslaWorkbenchShapes',elements,atlas,boxes,'HASLA WEAPON WORKBENCH')
