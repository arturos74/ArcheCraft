"""Isometric block-layout preview using the cached vanilla Minecraft textures."""
from pathlib import Path
from zipfile import ZipFile
import io
import math
import random
import numpy as np
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
import build_structure as scene

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
archive = ZipFile(ROOT / 'build/moddev/artifacts/neoforge-21.1.265-client-extra-aka-minecraft-resources.jar')
textures = {}
plants = {'short_grass', 'tall_grass', 'large_fern', 'fern', 'allium', 'blue_orchid', 'cornflower', 'poppy', 'sugar_cane'}
thin = plants | {'vine', 'air', 'water', 'glass', 'lily_pad', 'lantern', 'brown_carpet', 'spruce_door'}


def texture(name, face):
    key = name, face
    if key in textures:
        return textures[key]
    filename = name
    tint = None
    if name == 'grass_block':
        filename = 'grass_block_top' if face == 'up' else 'grass_block_side'
        tint = (88, 112, 58) if face == 'up' else None
    elif name.endswith('_stairs'):
        filename = name[:-7] + ('s' if name[:-7].endswith(('brick', 'tile')) else '')
        if filename in ('spruce', 'dark_oak'):
            filename += '_planks'
    elif name.endswith('_slab'):
        filename = name[:-5] + ('s' if name[:-5].endswith(('brick', 'tile')) else '')
    elif name.endswith('_log'):
        filename = name + ('_top' if face == 'up' else '')
    elif name.endswith('_leaves'):
        tint = (78, 101, 49) if name == 'oak_leaves' else (85, 116, 60)
    elif name == 'water':
        filename = 'water_still'; tint = (83, 116, 94)
    elif name == 'lily_pad':
        tint = (87, 129, 61)
    elif name in ('short_grass', 'fern', 'sugar_cane','vine'):
        tint = (107, 127, 55)
    elif name.startswith(('tall_grass','large_fern')):
        filename = name if name.endswith(('_top','_bottom')) else name+'_top'
        tint = (107, 127, 55)
    elif name in ('furnace', 'crafting_table', 'barrel', 'bookshelf'):
        filename = {'furnace': 'furnace_top' if face == 'up' else 'furnace_front',
                    'crafting_table': 'crafting_table_top' if face == 'up' else 'crafting_table_side',
                    'barrel': 'barrel_top' if face == 'up' else 'barrel_side',
                    'bookshelf': 'oak_planks' if face == 'up' else 'bookshelf'}[name]
    elif name == 'spruce_door':
        filename = 'spruce_door_bottom'
    elif name == 'brown_carpet' or name == 'brown_bed':
        filename = 'brown_wool'
    elif name == 'chest':
        filename = 'spruce_planks'
    try:
        image = Image.open(io.BytesIO(archive.read('assets/minecraft/textures/block/' + filename + '.png'))).convert('RGBA')
        image = image.crop((0, 0, 16, 16))
    except KeyError:
        image = Image.new('RGBA', (16, 16), (116, 111, 96, 255))
    if tint:
        arr = np.array(image).astype(float)
        arr[:, :, :3] *= np.array(tint)[None, None, :] / 180
        image = Image.fromarray(np.clip(arr, 0, 255).astype('uint8'))
    if name == 'grass_block' and face != 'up':
        overlay = Image.open(io.BytesIO(archive.read('assets/minecraft/textures/block/grass_block_side_overlay.png'))).convert('RGBA')
        arr = np.array(overlay).astype(float);arr[:, :, :3] *= np.array([88,112,58])[None,None,:] / 180
        image.alpha_composite(Image.fromarray(np.clip(arr,0,255).astype('uint8')))
    if name == 'water':
        image.putalpha(225)
    image = ImageEnhance.Brightness(image).enhance({'up': 1.03, 'north': .79, 'west': .65}.get(face, 1))
    textures[key] = image
    return image


def render(output, overhead=False, title='MARSH RUINS', subtitle=None):
    width, height = 1900, 1450
    rise = .62 if overhead else .38
    def raw(p):
        x,y,z=p
        return np.array([x*.85-z*.60, -x*rise-z*(rise+.12)-y*.90])
    bounds=np.array([raw((x+dx,y+dy,z+dz)) for (x,y,z),(name,_) in scene.blocks.items()
                     if name!='minecraft:air' for dx,dy,dz in [(0,0,0),(1,1,1),(0,1,1),(1,0,0)]])
    low=bounds.min(axis=0);high=bounds.max(axis=0)
    scale=min((width-120)/(high[0]-low[0]),(height-240)/(high[1]-low[1]))
    origin=np.array([(width-(high[0]-low[0])*scale)/2,160.])
    def project(p):
        return origin+(raw(p)-low)*scale
    image = Image.new('RGBA',(width,height),(31,39,38,255))
    shadow = ImageDraw.Draw(image)
    sx,_,sz=scene.SIZE
    shadow.polygon([tuple(project(p)+np.array([20,25])) for p in [(0,0,0),(sx,0,0),(sx,0,sz),(0,0,sz)]], fill=(19,25,24,255))
    def face(a,b,d,tex):
        a,b,d = map(project,(a,b,d));c = b+d-a
        low = np.floor(np.minimum.reduce([a,b,c,d])).astype(int)
        high = np.ceil(np.maximum.reduce([a,b,c,d])).astype(int)
        w,h = high-low
        if w<=0 or h<=0:return
        inv = np.linalg.inv(np.stack((b-a,d-a),axis=1))*16
        offset = inv@(low-a)
        coefficients = (inv[0,0],inv[0,1],offset[0],inv[1,0],inv[1,1],offset[1])
        patch = tex.transform((int(w),int(h)),Image.Transform.AFFINE,coefficients,resample=Image.Resampling.NEAREST)
        image.alpha_composite(patch,(int(low[0]),int(low[1])))
    def cube(x,y,z,lo,hi,name,visible=(True,True,True)):
        x0,y0,z0 = x+lo[0],y+lo[1],z+lo[2];x1,y1,z1=x+hi[0],y+hi[1],z+hi[2]
        if visible[0]:face((x0,y1,z1),(x0,y1,z0),(x0,y0,z1),texture(name,'west'))
        if visible[1]:face((x0,y1,z0),(x1,y1,z0),(x0,y0,z0),texture(name,'north'))
        if visible[2]:face((x0,y1,z1),(x1,y1,z1),(x0,y1,z0),texture(name,'up'))
    def opaque(pos,name):
        other=scene.blocks.get(pos,('minecraft:air',()))[0].split(':')[1]
        if name=='water' and other=='water':return True
        return other not in thin and not other.endswith(('_stairs','_slab'))
    count=0
    for (x,y,z),(namespace,props) in sorted(scene.blocks.items(),key=lambda kv:kv[0][0]+kv[0][2]-kv[0][1]*.8,reverse=True):
        name=namespace.split(':')[1];props=dict(props)
        if name=='air':continue
        visible=(not opaque((x-1,y,z),name),not opaque((x,y,z-1),name),not opaque((x,y+1,z),name))
        if not any(visible):continue
        if name in plants:
            tex=texture(name+('_bottom' if props.get('half')=='lower' else '_top') if name in ('tall_grass','large_fern') else name,'north')
            face((x,y+1,z+.5),(x+1,y+1,z+.5),(x,y,z+.5),tex)
            face((x+.5,y+1,z+1),(x+.5,y+1,z),(x+.5,y,z+1),tex)
        elif name=='vine':
            tex=texture('vine','north')
            for facing in ['north','south']:
                if props.get(facing)=='true':
                    zz=z+(.02 if facing=='north' else .98)
                    face((x,y+1,zz),(x+1,y+1,zz),(x,y,zz),tex)
            for facing in ['west','east']:
                if props.get(facing)=='true':
                    xx=x+(.02 if facing=='west' else .98)
                    face((xx,y+1,z+1),(xx,y+1,z),(xx,y,z+1),tex)
        elif name in ('lily_pad','brown_carpet'):
            face((x,y+.035,z+1),(x+1,y+.035,z+1),(x,y+.035,z),texture(name,'up'))
        elif name.endswith('_slab'):
            cube(x,y,z,(0,0,0),(1,.5,1),name,visible)
            if props.get('waterlogged')=='true':
                cube(x,y,z,(0,.5,0),(1,.86,1),'water',visible)
        elif name.endswith('_stairs'):
            top=props.get('half')=='top'
            cube(x,y,z,(0,.5 if top else 0,0),(1,1 if top else .5,1),name,visible)
            lo=[0,0 if top else .5,0];hi=[1,.5 if top else 1,1]
            facing=props.get('facing','north')
            if facing=='east':lo[0]=.5
            elif facing=='west':hi[0]=.5
            elif facing=='south':lo[2]=.5
            else:hi[2]=.5
            cube(x,y,z,lo,hi,name)
        elif name=='lantern':
            cube(x,y,z,(.3,.2,.3),(.7,.8,.7),name)
        elif name=='spruce_door':
            cube(x,y,z,(0,0,.02),(1,1,.20),name)
        elif name=='brown_bed':
            cube(x,y,z,(0,0,0),(1,.55,1),name)
        elif name=='water':
            cube(x,y,z,(0,0,0),(1,.86,1),name,visible)
        else:
            cube(x,y,z,(0,0,0),(1,1,1),name,visible)
        count+=1
    draw=ImageDraw.Draw(image)
    font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',34)
    small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',23)
    draw.text((40,35),title,font=font,fill=(231,224,203))
    draw.text((40,86),subtitle or 'Vanilla block layout preview | 48 x 36 x 48 | front entrance faces north',font=small,fill=(178,193,175))
    image.convert('RGB').save(output)
    print(f'Rendered {count} visible blocks: {output}')


if __name__=='__main__':
    from types import SimpleNamespace
    from build_site import read_template
    saved,_=read_template(HERE/'marsh_ruins.nbt')
    scene=SimpleNamespace(blocks=saved,SIZE=(48,36,48))
    render(HERE/'marsh_ruins_preview.png')
    render(HERE/'marsh_ruins_overview.png',overhead=True)
