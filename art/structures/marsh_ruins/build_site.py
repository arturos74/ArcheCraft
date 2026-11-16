"""Assemble the unchanged crafting hub and three editable 48-block swamp tiles."""
from pathlib import Path
import copy
import gzip
import hashlib
import io
import json
import math
import random
import struct
from build_structure import payload
from swamp_ecology import decorate,patch_water

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
DATA=ROOT/'src/main/resources/data/archecraft'
SIZE=(96,36,96)
TILE_SIZE=(48,36,48)
AIR=('minecraft:air',())
blocks={}
ground={}


def read_template(path):
    stream=io.BytesIO(gzip.decompress(path.read_bytes()))
    def read(tag):
        if tag==3:return struct.unpack('>i',stream.read(4))[0]
        if tag==8:return stream.read(struct.unpack('>H',stream.read(2))[0]).decode()
        if tag==9:
            child=stream.read(1)[0];count=read(3)
            return child,[read(child) for _ in range(count)]
        if tag==10:
            result={}
            while (child:=stream.read(1)[0])!=0:
                key=read(8);result[key]=(child,read(child))
            return result
        raise ValueError(f'Unexpected NBT type {tag}; preserve and inspect the artist template before rebuilding.')
    assert stream.read(1)==b'\x0a';read(8)
    root=read(10);palette=[]
    for state in root['palette'][1][1]:
        palette.append((state['Name'][1],tuple(sorted((k,v[1]) for k,v in state.get('Properties',(10,{}))[1].items()))))
    result={};extras={}
    for record in root['blocks'][1][1]:
        pos=tuple(record['pos'][1][1]);result[pos]=palette[record['state'][1]]
        if 'nbt' in record:extras[pos]=record['nbt'][1]
    assert not root['entities'][1][1], 'Inspect embedded entities before assembling the site'
    return result,extras


def export_template(path,scene,size,extras=None):
    extras=extras or {};palette=sorted(set(scene.values())|{AIR});index={state:i for i,state in enumerate(palette)}
    states=[]
    for name,properties in palette:
        state={'Name':(8,name)}
        if properties:state['Properties']=(10,{key:(8,value) for key,value in properties})
        states.append(state)
    records=[]
    for y in range(size[1]):
        for z in range(size[2]):
            for x in range(size[0]):
                pos=(x,y,z);record={'pos':(9,(3,list(pos))),'state':(3,index[scene.get(pos,AIR)])}
                if pos in extras:record['nbt']=(10,extras[pos])
                records.append(record)
    root={'DataVersion':(3,3955),'size':(9,(3,list(size))),'palette':(9,(10,states)),
          'blocks':(9,(10,records)),'entities':(9,(10,[])),'author':(8,'ArcheCraft')}
    raw=gzip.compress(b'\x0a\0\0'+payload(10,root),mtime=0)
    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


def swamp_tile(seed,offset,ponds,ruins):
    rng=random.Random(seed);scene={};heights={}
    def put(x,y,z,name,**props):
        assert 0<=x<48 and 0<=y<36 and 0<=z<48,(x,y,z)
        scene[x,y,z]=('minecraft:'+name,tuple(sorted((k,str(v).lower()) for k,v in props.items())))
    def at(x,y,z):return scene.get((x,y,z),AIR)[0].split(':')[1]
    def wet(x,z):return dict(scene.get((x,5,z),AIR)[1]).get('waterlogged')=='true'
    def masonry():return rng.choice(['stone_bricks','mossy_stone_bricks','cobblestone','mossy_cobblestone'])
    for x in range(48):
        for z in range(48):
            # Match the hub's lowlands at the tile seams using global coordinates.
            gx,gz=x+offset[0]-48,z+offset[1]-48
            wave=math.sin(gx*.27)+.7*math.cos(gz*.31)+.5*math.sin((gx+gz)*.22)
            y=5+(wave>.7)
            heights[x,z]=y
            for yy in range(y+1):put(x,yy,z,'grass_block' if yy==y else 'dirt' if yy>=y-3 else 'stone')
            corridor=abs(x-24)<=3 or abs(z-24)<=3
            main_pond=any(((x-cx)/rx)**2+((z-cz)/rz)**2<1 for cx,cz,rx,rz in ponds)
            if not corridor and main_pond and patch_water(gx,gz,True):
                put(x,4,z,'mud');put(x,5,z,'mud_brick_slab',type='bottom',waterlogged=True)
                if y==6:put(x,6,z,'air')
                heights[x,z]=5
    # Broken courtyards: patchy floors, open entries, low walls, jagged pillars.
    for ri,(cx,cz) in enumerate(ruins):
        hx,hz=(4,3) if ri==0 else (3,4)
        for x in range(cx-hx,cx+hx+1):
            for z in range(cz-hz,cz+hz+1):
                if abs(x-24)<=3 or abs(z-24)<=3:continue
                y=heights[x,z]
                if rng.random()<.43:put(x,y,z,masonry())
                edge=x in (cx-hx,cx+hx) or z in (cz-hz,cz+hz)
                entry=abs(x-cx)<=1 and z in (cz-hz,cz+hz)
                if edge and not entry:
                    height=rng.choices([0,1,2,3,4],[2,3,5,2,1])[0]
                    if x in (cx-hx,cx+hx) and z in (cz-hz,cz+hz):height=rng.randint(3,6)
                    for yy in range(y+1,y+height+1):put(x,yy,z,masonry())
                    if height and rng.random()<.6:
                        put(x,y+height+1,z,rng.choice(['stone_brick_slab','mossy_stone_brick_slab','cobblestone_slab','mossy_cobblestone_slab']),type='bottom',waterlogged=False)
        # One incomplete arch and a few fallen blocks rather than an enclosed room.
        y=heights[cx-hx,cz-hz]
        put(cx-hx+1,y+4,cz-hz,'mossy_stone_brick_stairs',facing='west',half='top',shape='straight',waterlogged=False)
        for _ in range(5):
            x=cx+rng.randint(-hx-1,hx+1);z=cz+rng.randint(-hz-1,hz+1)
            if abs(x-24)>3 and abs(z-24)>3 and at(x,heights[x,z]+1,z)=='air':
                put(x,heights[x,z]+1,z,rng.choice(['cobblestone_slab','mossy_cobblestone_slab']),type='bottom',waterlogged=False)
    shapes=['willow','umbrella','squat','forked']
    shift=seed%4;shapes=shapes[shift:]+shapes[:shift]
    decorate(scene,heights,seed+100,[(6,40,shapes[0]),(40,6,shapes[1]),(7,16,shapes[2]),(40,40,shapes[3])],
             offset=(offset[0]-48,offset[1]-48),corridors=True)
    return scene


def connector(scene,extras,pos,facing,name,target='minecraft:empty',pool='minecraft:empty'):
    scene[pos]=('minecraft:jigsaw',(('orientation',facing+'_up'),))
    extras[pos]={key:(8,value) for key,value in dict(name=name,target=target,pool=pool,joint='aligned',final_state='minecraft:stone').items()}
    extras[pos].update(selection_priority=(3,0),placement_priority=(3,0))


def build():
    base=HERE/'marsh_ruins.nbt';before=base.read_bytes()
    assert before==(DATA/'structure/marsh_ruins.nbt').read_bytes(),'Art/runtime hub differ; inspect edits before rebuilding'
    hub,hub_extras=read_template(base)
    plans=[('sunken_court',(0,48),731205,[(11,10,7,6),(36,34,7,8),(11,36,5,5)],[(34,10),(10,29)]),
           ('broken_arch',(48,0),731206,[(10,10,6,7),(36,13,6,6),(35,36,8,7)],[(9,33),(35,28)]),
           ('fallen_walls',(0,0),731207,[(12,12,8,7),(35,36,7,9),(10,36,5,6)],[(34,10),(10,29)])]
    sections={'hub':hub};offsets={'hub':(48,48)};manifest=[]
    for name,offset,seed,ponds,ruins in plans:
        scene=swamp_tile(seed,offset,ponds,ruins);sections[name]=scene;offsets[name]=offset
        dest=DATA/f'structure/marsh_ruins/{name}.nbt';sha=export_template(dest,scene,TILE_SIZE)
        art=HERE/'sections'/f'{name}.nbt';art.parent.mkdir(parents=True,exist_ok=True);art.write_bytes(dest.read_bytes())
        water=sum(dict(state[1]).get('waterlogged')=='true' for state in scene.values())
        manifest.append(dict(name=name,offset=list(offset),seed=seed,sha256=sha,water_columns=water,ruins=2,pond_depth_blocks=.5))
    # Natural generation uses hidden underground connectors; editable tiles stay clean.
    assembly={name:(copy.copy(scene),copy.deepcopy(hub_extras) if name=='hub' else {}) for name,scene in sections.items()}
    root,extra=assembly['hub']
    connector(root,extra,(0,2,24),'west','archecraft:hasla/root_west','archecraft:hasla/west_entry','archecraft:marsh_ruins/west')
    connector(root,extra,(24,2,0),'north','archecraft:hasla/root_north','archecraft:hasla/north_entry','archecraft:marsh_ruins/north')
    west,extra=assembly['sunken_court']
    connector(west,extra,(47,2,24),'east','archecraft:hasla/west_entry')
    connector(west,extra,(24,2,0),'north','archecraft:hasla/west_north','archecraft:hasla/northwest_entry','archecraft:marsh_ruins/northwest')
    north,extra=assembly['broken_arch'];connector(north,extra,(24,2,47),'south','archecraft:hasla/north_entry')
    northwest,extra=assembly['fallen_walls'];connector(northwest,extra,(24,2,47),'south','archecraft:hasla/northwest_entry')
    for name,(scene,extras) in assembly.items():export_template(DATA/f'structure/marsh_ruins/pieces/{name}.nbt',scene,TILE_SIZE,extras)
    combined={};combined_extra={}
    for name,scene in sections.items():
        ox,oz=offsets[name]
        combined.update({(x+ox,y,z+oz):state for (x,y,z),state in scene.items()})
        if name=='hub':combined_extra.update({(x+ox,y,z+oz):value for (x,y,z),value in hub_extras.items()})
    full=DATA/'structure/hasla_swamp.nbt';full_sha=export_template(full,combined,SIZE,combined_extra)
    (HERE/'hasla_swamp.nbt').write_bytes(full.read_bytes())
    (DATA/'structure/abandoned_drill_camp.nbt').write_bytes(full.read_bytes())
    (HERE/'abandoned_drill_camp.nbt').write_bytes(full.read_bytes())
    assert base.read_bytes()==before and (DATA/'structure/marsh_ruins.nbt').read_bytes()==before
    info=dict(size=list(SIZE),section_size=list(TILE_SIZE),hub_offset=[48,48],hub_sha256=hashlib.sha256(before).hexdigest(),
              sections=manifest,assembled_template='archecraft:abandoned_drill_camp',sha256=full_sha,
              workstation=dict(id='archecraft:hasla_workbench',hub_position=[35,16,38],site_position=[83,16,86],facing='north'),
              notes='Abandoned Drill Camp: saved crafting pavilion with Hasla Workbench, plus three swamp habitat sections. Sarracenia natural spawns come from the registered structure override; no entities are embedded in the templates.')
    (HERE/'site_manifest.json').write_text(json.dumps(info,indent=2)+'\n')
    print('Built 96 x 96 Abandoned Drill Camp from four 48-block tiles; saved hub and Hasla Workbench preserved.')
    return combined


if __name__=='__main__':build()
