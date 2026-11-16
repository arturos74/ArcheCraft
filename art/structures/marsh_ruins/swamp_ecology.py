"""Shared vanilla swamp vegetation, irregular puddles, and varied tree silhouettes."""
import math
import random

AIR=('minecraft:air',())
FLORA={'short_grass','tall_grass','fern','large_fern','allium','blue_orchid','cornflower','poppy','sugar_cane','lily_pad','vine'}
NATURAL_GROUND={'grass_block','coarse_dirt','rooted_dirt','mud','moss_block'}


def patch_water(x,z,main_pond):
    noise=.65*math.sin(x*.56+math.sin(z*.37))+.55*math.cos(z*.61)+.25*math.sin(x*.93+z*.77)
    return noise>(-.15 if main_pond else 1.04)


def decorate(scene,heights,seed,trees,offset=(0,0),corridors=False,scatter_water=True):
    rng=random.Random(seed)
    def at(x,y,z):return scene.get((x,y,z),AIR)[0].split(':')[1]
    def put(x,y,z,name,**props):
        if 0<=x<48 and 0<=z<48 and 0<=y<36:
            scene[x,y,z]=('minecraft:'+name,tuple(sorted((k,str(v).lower()) for k,v in props.items())))
    def clear_route(x,z):return corridors and (abs(x-24)<=3 or abs(z-24)<=3)
    def wet(x,z):return dict(scene.get((x,5,z),AIR)[1]).get('waterlogged')=='true'
    def air(x,y,z):return at(x,y,z)=='air'
    def plant_space(x,y,z):return at(x,y,z) in FLORA or air(x,y,z)
    # Sparse satellite puddles sit between grass islands, with solid half-block beds.
    if scatter_water:
        for x in range(2,46):
            for z in range(2,46):
                y=heights[x,z]
                if y not in (5,6) or clear_route(x,z) or at(x,y,z)!='grass_block':continue
                if not all(plant_space(x,yy,z) for yy in range(y+1,9)):continue
                if patch_water(x+offset[0],z+offset[1],False):
                    put(x,4,z,'mud');put(x,5,z,'mud_brick_slab',type='bottom',waterlogged=True)
                    if y==6:put(x,6,z,'air')
                    heights[x,z]=5
    # Coherent muddy/mossy patches rather than a uniformly green lawn.
    for x in range(1,47):
        for z in range(1,47):
            y=heights[x,z]
            if at(x,y,z)!='grass_block' or not plant_space(x,y+1,z):continue
            near_water=any(wet(x+dx,z+dz) for dx,dz in [(1,0),(-1,0),(0,1),(0,-1)])
            patch=math.sin((x+offset[0])*.67)+math.cos((z+offset[1])*.73)
            roll=rng.random()
            if near_water and roll<.35:material='mud'
            elif patch>1.1 and roll<.65:material='moss_block'
            elif patch<-.9 and roll<.32:material='mud'
            elif roll<.035:material='coarse_dirt'
            else:continue
            put(x,y,z,material)

    stats=[]
    for cx,cz,kind in trees:
        base=heights[cx,cz]
        if at(cx,base,cz) not in NATURAL_GROUND|{'mud_brick_slab'}:continue
        put(cx,base,cz,'rooted_dirt')
        log='mangrove_log' if kind=='forked' else 'oak_log'
        leaves='mangrove_leaves' if kind=='forked' else 'oak_leaves'
        tree_leaves=set()
        def wood_line(start,end):
            steps=max(abs(end[i]-start[i]) for i in range(3))
            for i in range(steps+1):
                pos=tuple(round(start[j]+(end[j]-start[j])*i/max(1,steps)) for j in range(3))
                if not all(0<=pos[j]<(48 if j!=1 else 36) for j in range(3)):continue
                x,y,z=pos
                if air(x,y,z) or at(x,y,z) in FLORA or at(x,y,z).endswith('_leaves'):
                    axis='y' if end[1]!=start[1] else 'x' if end[0]!=start[0] else 'z'
                    put(x,y,z,log,axis=axis)
        def crown(xc,yc,zc,rx,rz,ry):
            for x in range(max(0,math.floor(xc-rx-1)),min(48,math.ceil(xc+rx+2))):
                for z in range(max(0,math.floor(zc-rz-1)),min(48,math.ceil(zc+rz+2))):
                    for y in range(max(base+3,math.floor(yc-ry)),math.ceil(yc+ry)+1):
                        d=((x-xc)/rx)**2+((z-zc)/rz)**2+((y-yc)/ry)**2
                        edge=.10*math.sin(x*2.17+z*.71+y)
                        if d<=1.07+edge and (air(x,y,z) or at(x,y,z).endswith('_leaves')):
                            put(x,y,z,leaves,persistent=True,distance=1,waterlogged=False);tree_leaves.add((x,y,z))
        sign=rng.choice([-1,1])
        if kind=='willow':
            top=base+rng.randint(9,11)
            wood_line((cx,base+1,cz),(cx,top-4,cz))
            wood_line((cx,top-4,cz),(cx+sign*2,top,cz+1))
            crown(cx+sign,top,cz,4.5,4,2.2)
            for dx,dz in [(-3,1),(2,3),(2,-3)]:
                wood_line((cx+sign,top-2,cz),(cx+dx,top-1,cz+dz))
            crown(cx-sign*2,top-2,cz+2,3,3,1.5)
        elif kind=='umbrella':
            top=base+rng.randint(7,9)
            wood_line((cx,base+1,cz),(cx,top,cz))
            for dx,dz in [(3,0),(-3,1),(0,3),(1,-3)]:wood_line((cx,top-2,cz),(cx+dx,top,cz+dz))
            crown(cx,top+1,cz,5,4,1.8)
            crown(cx+sign*2,top,cz+2,3.5,3,1.5)
        elif kind=='squat':
            top=base+rng.randint(4,6)
            wood_line((cx,base+1,cz),(cx+sign,top,cz))
            wood_line((cx,top-2,cz),(cx-sign*2,top,cz+1))
            crown(cx,top+1,cz,4.1,3.7,2.1)
        else:
            fork=base+rng.randint(7,9)
            wood_line((cx,base+1,cz),(cx,fork,cz))
            for dx,dz,up in [(-2,1,3),(3,-1,5)]:
                wood_line((cx,fork-2,cz),(cx+dx,fork+up,cz+dz))
                crown(cx+dx,fork+up,cz+dz,3.2,3.5,2)
        # Root flares vary with the trunk instead of repeating identical crosses.
        for dx,dz in rng.sample([(1,0),(-1,0),(0,1),(0,-1)],2):
            y=heights.get((cx+dx,cz+dz),base)+1
            if air(cx+dx,y,cz+dz):put(cx+dx,y,cz+dz,log,axis='y')
        # Each hanging column starts beside a supporting leaf. Lower vines retain
        # that same attachment face through the vine above them.
        columns=set()
        for x,y,z in sorted(tree_leaves):
            if rng.random()>(.22 if kind=='willow' else .12):continue
            for dx,dz,face in rng.sample([(1,0,'west'),(-1,0,'east'),(0,1,'north'),(0,-1,'south')],4):
                vx,vz=x+dx,z+dz
                if not (0<vx<47 and 0<vz<47) or (vx,vz) in columns or not air(vx,y,vz):continue
                if at(vx,y+1,vz).endswith('_leaves'):continue
                stop=max(heights[vx,vz]+(4 if clear_route(vx,vz) else 2),y-rng.randint(4,8))
                if stop>=y:continue
                attachment={f:False for f in ['north','south','east','west','up']};attachment[face]=True
                for yy in range(y,stop-1,-1):
                    if not air(vx,yy,vz):break
                    # Weeping leaf sprays support every vine segment. This also
                    # survives /place template's bottom-up neighbor updates.
                    if air(x,yy,z):
                        put(x,yy,z,leaves,persistent=True,distance=1,waterlogged=False)
                    elif not at(x,yy,z).endswith(('_leaves','_log')):
                        break
                    put(vx,yy,vz,'vine',**attachment)
                columns.add((vx,vz));break
        stats.append(dict(position=[cx,base,cz],shape=kind,leaf_type=leaves,vine_columns=len(columns)))
    # Vegetation grows in clusters, with both short and two-block-tall plants.
    for x in range(1,47):
        for z in range(1,47):
            y=heights[x,z]
            if wet(x,z) and air(x,6,z):
                if rng.random()<.18:put(x,6,z,'lily_pad')
                continue
            if at(x,y,z) not in {'grass_block','rooted_dirt','coarse_dirt','moss_block'} or not air(x,y+1,z):continue
            near_water=y==5 and any(wet(x+dx,z+dz) for dx,dz in [(1,0),(-1,0),(0,1),(0,-1)])
            roll=rng.random()
            if near_water and roll<.12 and at(x,y,z)=='grass_block':
                for yy in range(y+1,y+rng.randint(2,3)+1):
                    if air(x,yy,z):put(x,yy,z,'sugar_cane',age=0)
            elif roll<(.10 if clear_route(x,z) else .26) and air(x,y+2,z):
                name='large_fern' if rng.random()<.23 else 'tall_grass'
                put(x,y+1,z,name,half='lower');put(x,y+2,z,name,half='upper')
            elif roll<.57:
                put(x,y+1,z,rng.choices(['short_grass','fern','blue_orchid'],[12,5,1])[0])
    return stats
