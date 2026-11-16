"""Add three small hooked claws per hand to the current saved Yata project."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import copy,json,shutil,uuid
import numpy as np
from project_tools import load,world,write,refresh_assets,render

HERE=Path(__file__).resolve().parent
CLAW_LENGTH_SCALE=1.0
CLAW_THICKNESS_SCALE=1.0

def apply_hand_claws(here):
    path=here/'yata.bbmodel'
    project,bones,parents,owners,cubes,texture=load(path)
    before=copy.deepcopy(project)
    backup=here/'versions/before_hand_claws'
    backup.mkdir(parents=True,exist_ok=True)
    for name in ['yata.bbmodel','yata.png']:
        if not (backup/name).exists():shutil.copy2(here/name,backup/name)
    # Retain all original paw geometry. The new dark claws reuse the paw's
    # existing nail texture so no painted pixels or texture metadata change.
    additions=[];by_hand={}
    for side in ['left','right']:
        hand=side+'_hand'
        template=next(e for e in cubes if e['name']==side+' little claws')
        lo,hi=template['from'],template['to'];span=hi[0]-lo[0]
        z=(lo[2]+hi[2])/2
        by_hand[bones[hand]['uuid']]=[]
        for i in range(3):
            x=lo[0]+span*(i+.5)/3
            half=span/3*.35
            specs=[('',[x-half,lo[1]-.85,z-.25],[x+half,lo[1]+.12,z+.25]),
                (' tip',[x-half*.6,lo[1]-1.42,z+.06],[x+half*.6,lo[1]-.72,z+.38])]
            for suffix,a,b in specs:
                anchor=np.array([x,lo[1]+.12,z])
                size_scale=np.array([CLAW_THICKNESS_SCALE,CLAW_LENGTH_SCALE,CLAW_THICKNESS_SCALE])
                a=(anchor+(np.array(a)-anchor)*size_scale).tolist()
                b=(anchor+(np.array(b)-anchor)*size_scale).tolist()
                name=side+f' hand claw {i+1}'+suffix
                ident=str(uuid.uuid5(uuid.NAMESPACE_URL,'archecraft/yata/'+name))
                if any(e['uuid']==ident for e in cubes):continue
                e=copy.deepcopy(template)
                e.update(name=name,uuid=ident,**{'from':a,'to':b},origin=list(bones[hand]['origin']))
                e.pop('rotation',None);e['selected']=False
                additions.append(e);by_hand[bones[hand]['uuid']].append(ident)
                owners[ident]=hand
    def attach(nodes):
        for node in nodes:
            if not isinstance(node,dict):continue
            if node['uuid'] in by_hand:node['children'].extend(by_hand[node['uuid']])
            attach(node.get('children',[]))
    attach(project['outliner'])
    cubes.extend(additions)
    assert project['textures']==before['textures'] and project['animations']==before['animations']
    old={e['uuid']:e for e in before['elements']}
    assert all(e==old[e['uuid']] for e in cubes if e['uuid'] in old)
    assert project.get('groups')==before.get('groups')
    write(path,project)
    layout_path=here/'yata_uv_layout.json'
    layout=json.loads(layout_path.read_text())
    for e in additions:
        for face,data in e['faces'].items():
            side='left' if e['name'].startswith('left') else 'right'
            layout.append(dict(cube=e['name'],face=face,material='claw',uv=data['uv'],
                shared_with=side+' little claws'))
    write(layout_path,layout)
    refresh_assets(here,project,bones,parents,owners,cubes,texture)
    preview=Image.new('RGB',(1700,920),(30,36,42))
    preview.paste(render(cubes,texture,bones,parents,owners),(0,55))
    hands=[e for e in cubes if owners[e['uuid']] in ['left_hand','right_hand','left_forearm','right_forearm']]
    paws=[e for e in cubes if e['name'] in ['left paw','right paw']]
    focus=np.mean([world(np.mean([e['from'],e['to']],axis=0),owners[e['uuid']],bones,parents) for e in paws],axis=0)
    preview.paste(render(hands,texture,bones,parents,owners,205,center=focus,view_scale=55,baseline=360),(850,55))
    d=ImageDraw.Draw(preview);font=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',27)
    small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',19)
    d.text((30,16),'YATA / THREE CLAWS PER HAND',font=font,fill=(231,220,202))
    d.text((30,865),'CURRENT SAVED MODEL',font=small,fill=(174,188,193))
    d.text((880,865),'HAND DETAIL / separate dark tapered claws',font=small,fill=(174,188,193))
    d.text((30,895),'Claws follow the existing hand bones. Saved geometry, texture and animation clips preserved.',font=small,fill=(174,188,193))
    preview.save(here/'yata_hand_claws_preview.png')
    print(f'Added {len(additions)} claw segments; {len(cubes)} total cuboids, {len(bones)} bones. All original elements and texture retained.')

if __name__=='__main__':apply_hand_claws(HERE)
