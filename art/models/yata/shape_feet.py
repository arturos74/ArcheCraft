"""Give the saved Yata flat toe pads and a rising foot meeting a raised ankle."""
from pathlib import Path
import copy, math, shutil
import numpy as np
from project_tools import load,world,corners,write,refresh_assets

def apply_toe_stance(here):
    path=here/'yata.bbmodel'
    project,bones,parents,owners,cubes,texture=load(path)
    before=copy.deepcopy(project)
    backup=here/'versions/before_toe_stance'
    backup.mkdir(parents=True,exist_ok=True)
    for name in ['yata.bbmodel','yata.png']:
        if not (backup/name).exists():shutil.copy2(here/name,backup/name)
    elements={e['name']:e for e in cubes}
    for side in ['left','right']:
        foot=side+'_foot';shin=side+'_shin';b=bones[foot]
        ankle=world(b['origin'],foot,bones,parents)
        # Move the existing ankle joint up its lower-leg chain; keep hips, knees,
        # the torso and the rider point in their saved locations.
        delta=(6.0-ankle[1])/math.cos(math.radians(40))
        b['origin'][1]=round(b['origin'][1]+delta,6)
        lower=elements[side+' lower leg']
        lower['from'][1]=round(b['origin'][1]+0.17,6)
        ankle=world(b['origin'],foot,bones,parents)
        pivot=np.array(b['origin']);offset=pivot-ankle
        x=ankle[0]
        def set_box(e,lo,hi,rotation=(0,0,0)):
            # Foot's neutral orientation is level, so authored coordinates differ
            # from the desired neutral world geometry only by this translation.
            e['from']=np.round(np.array(lo)+offset,6).tolist()
            e['to']=np.round(np.array(hi)+offset,6).tolist()
            e['origin']=list(b['origin'])
            if any(rotation):e['rotation']=list(rotation)
            else:e.pop('rotation',None)
        # Rounded joint mass around the raised ankle; it no longer sits at ground.
        set_box(elements[side+' ankle'],[x-1.7,5.1,ankle[2]-1.1],[x+1.7,6.8,ankle[2]+1.1])
        # One continuous sloping metatarsus. Its upper end is exactly at the ankle
        # pivot and its lower end overlaps the backs of the three flat toe pads.
        contact_y=1.0;contact_z=1.45
        dy=ankle[1]-contact_y;dz=ankle[2]-contact_z
        length=math.hypot(dy,dz);angle=math.degrees(math.atan2(dz,dy))
        set_box(elements[side+' broad hind foot'],[x-1.8,ankle[1]-length,ankle[2]-0.9],
            [x+1.8,ankle[1],ankle[2]+0.9],(angle,0,0))
        for i,dx in enumerate([-1.7,0,1.7]):
            front=-0.25 if i==1 else 0.2
            set_box(elements[side+f' toe {i+1}'],[x+dx-0.7225,0,front],[x+dx+0.7225,1.15,2.3])
            set_box(elements[side+f' claw {i+1}'],[x+dx-0.51,0.05,front-0.7],
                [x+dx+0.51,0.7,front+0.6])
        print(side,'ankle height',round(ankle[1],3),'foot slope',round(angle,1),'degrees')
    assert project['textures']==before['textures']
    assert project['animations']==before['animations']
    assert len(project['elements'])==len(before['elements'])
    write(path,project)
    refresh_assets(here,project,bones,parents,owners,cubes,texture)
    print('Saved toe-planted feet, raised ankle pivots, matching exports and previews.')

if __name__=='__main__':apply_toe_stance(Path(__file__).resolve().parent)
