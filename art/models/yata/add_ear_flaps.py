"""Add the Yata's smaller lower ear flaps to the current saved project."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import copy,json,shutil,uuid
from project_tools import load,write,refresh_assets,render

def apply_ear_flaps(here):
    path=here/'yata.bbmodel'
    project,bones,parents,owners,cubes,texture=load(path)
    before=copy.deepcopy(project)
    backup=here/'versions/before_ear_flaps'
    backup.mkdir(parents=True,exist_ok=True)
    for name in ['yata.bbmodel','yata.png']:
        if not (backup/name).exists():shutil.copy2(here/name,backup/name)
    additions=[];nodes={};new_groups=[];layout=json.loads((here/'yata_uv_layout.json').read_text())
    elements={e['name']:e for e in cubes}
    for side,sign in [('left',1),('right',-1)]:
        parent='ear_'+side;name=parent+'_flap'
        if name in bones:continue
        origin=list(bones[parent]['origin']);origin[1]+=.5;origin[2]+=.65
        x,y,z=origin
        ident=str(uuid.uuid5(uuid.NAMESPACE_URL,'archecraft/yata/bone/'+name))
        group=copy.deepcopy(bones[parent])
        group.update(name=name,uuid=ident,origin=origin,rotation=[0,0,sign*60],children=[],selected=False,primary_selected=False)
        shell=elements[side+' ear stem'];inner=elements[side+' inner ear']
        specs=[
            ('base',[-.6,0,-.45],[.6,1.3,.45],shell,'fur'),
            ('lobe',[-1.45,1,-.45],[1.45,4.4,.45],shell,'fur'),
            ('taper',[-1,4.4,-.35],[1,5.8,.35],shell,'fur'),
            ('tip',[-.5,5.8,-.25],[.5,6.5,.25],shell,'fur'),
            ('inner',[-1,1.5,-.56],[1,4.2,-.45],inner,'inner'),
            ('inner tip',[-.6,4.2,-.45],[.6,5.3,-.35],inner,'inner')]
        child_ids=[]
        for label,lo,hi,source,material in specs:
            cube_name=side+' lower ear flap '+label
            cube_id=str(uuid.uuid5(uuid.NAMESPACE_URL,'archecraft/yata/cube/'+cube_name))
            e=copy.deepcopy(source)
            e.update(name=cube_name,uuid=cube_id,**{'from':[a+b for a,b in zip(origin,lo)],
                'to':[a+b for a,b in zip(origin,hi)]},origin=origin.copy(),selected=False)
            e.pop('rotation',None);additions.append(e);child_ids.append(cube_id)
            for face,data in e['faces'].items():
                layout.append(dict(cube=cube_name,face=face,material=material,uv=data['uv'],shared_with=source['name']))
        if 'groups' in project:
            project['groups'].append(group)
            node=dict(uuid=ident,isOpen=True,children=child_ids)
        else:
            node=copy.deepcopy(group);node.update(isOpen=True,children=child_ids)
        nodes[bones[parent]['uuid']]=node
        new_groups.append(name)
    def attach(entries):
        for entry in entries:
            if not isinstance(entry,dict):continue
            attach(entry.get('children',[]))
            if entry['uuid'] in nodes:entry['children'].append(nodes[entry['uuid']])
    attach(project['outliner'])
    cubes.extend(additions)
    assert project['textures']==before['textures'] and project['animations']==before['animations']
    old={e['uuid']:e for e in before['elements']}
    assert all(e==old[e['uuid']] for e in cubes if e['uuid'] in old)
    write(path,project);write(here/'yata_uv_layout.json',layout)
    # Reload to resolve the newly attached groups in either Blockbench format.
    project,bones,parents,owners,cubes,texture=load(path)
    refresh_assets(here,project,bones,parents,owners,cubes,texture)
    preview=Image.new('RGB',(1700,920),(30,36,42))
    preview.paste(render(cubes,texture,bones,parents,owners),(0,55))
    head=[e for e in cubes if (owners[e['uuid']] or '').startswith('ear_') or owners[e['uuid']] in ['head','jaw','neck']]
    preview.paste(render(head,texture,bones,parents,owners,215,center=(0,35.5,-8),view_scale=31,baseline=400),(850,55))
    d=ImageDraw.Draw(preview);font=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',27)
    small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',19)
    d.text((30,16),'YATA / SMALLER LOWER EAR FLAPS',font=font,fill=(231,220,202))
    d.text((30,865),'CURRENT SAVED MODEL',font=small,fill=(174,188,193))
    d.text((880,865),'HEAD DETAIL / additional flaps beneath the main ears',font=small,fill=(174,188,193))
    d.text((30,895),'New controls: ear_left_flap and ear_right_flap. Original ear-tip hinges and saved edits retained.',font=small,fill=(174,188,193))
    preview.save(here/'yata_ear_flaps_preview.png')
    print(f'Added {len(additions)} cuboids and {len(new_groups)} flap bones. Total: {len(cubes)} cubes, {len(bones)} bones.')

if __name__=='__main__':apply_ear_flaps(Path(__file__).resolve().parent)
