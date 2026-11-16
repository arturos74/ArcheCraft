"""Palomino female UV colors and markings, based on ScreenShot0018."""
import math
from variant_authoring import build_variant

BELLY_COLOR = [207,200,184]

def is_tail_spot(point,name,face,e):
    """Broken cream markings on the dorsal tail, with a small upper-edge wrap."""
    if 'tail' not in name.lower() or face not in ('up','east','west'):
        return False
    x,y,z=point
    x0,y0,z0=e['from'];x1,y1,z1=e['to']
    if face!='up' and y<y1-(y1-y0)*.23:
        return False
    across=(x-(x0+x1)/2)/((x1-x0)/2)
    return any(((across-offset)/.78)**2+((z-center)/1.05)**2<1
               for center,offset in [(15.3,-.4),(18.7,.4),(22.4,-.4),
                                     (25.7,.4),(29.3,-.35),(32.4,.35)])

def paint(point,material,name,face,e,context):
    x,y,z=point;lower=name.lower();color=[178,165,145]
    if material=='fur':
        color=[182,168,146]
        if name in ('Back and shoulders','Rounded haunch core'):
            color=[162,139,115] if face=='up' or y>18.4 else [192,183,165]
        if 'thigh' in lower or 'knee' in lower:
            color=[192,184,167]
        # A few dark flank marks/bands, rather than the black coat's pale spots.
        if any(s in lower for s in ['haunch','upper thigh','knee']) and face in ('east','west','south'):
            q=z+.35*y+.5*math.sin(x);distance=abs((q+4.75)%9.5-4.75)
            if distance<.40 and y<18.5:color=[98,91,76]
            elif distance<.65 and y<18.5:color=[137,128,109]
            for yy,zz,r in [(16.4,2.2,.32),(17.3,3.7,.28),(16.9,5.2,.23)]:
                if (y-yy)**2+(z-zz)**2<r*r:color=[89,82,69]
        if name=='Head':color=[121,105,85]
        if 'ear' in lower:
            high=(y-context['ear_low'])/(context['ear_high']-context['ear_low'])
            color=[136,119,96] if high<.81 else [63,54,43]
        if 'forearm' in lower:color=[98,87,70]
        if 'tail' in lower:
            color=[91,76,58] if 'root' in lower else [70,59,46]
    elif material=='cream':
        color=BELLY_COLOR
        if 'muzzle' in lower or 'jaw' in lower:color=[66,59,49]
        elif 'brush' in lower:color=[40,36,30]
    elif material=='inner':
        high=(y-context['ear_low'])/(context['ear_high']-context['ear_low'])
        color=[193,185,168] if high<.91 else [105,94,77]
    elif material=='foot':
        color=[60,53,44]
        if 'lower leg' in lower or 'ankle' in lower:
            color=[82,72,59] if (y*2)%2>.4 else [61,53,44]
    elif material in ('claw','nose'):color=[26,25,23]
    elif material=='eyelid':color=[84,72,56]
    elif material=='eye':color=[15,17,16]
    elif material=='white':color=[234,232,222]
    return BELLY_COLOR if is_tail_spot(point,name,face,e) else color

if __name__=='__main__':
    build_variant('palomino','Palomino Female Yata','female',paint,
        'Shared canonical runtime rig at 1.3 scale. Muted sand/beige coat, pale throat/belly, dark muzzle/legs/tail and sparse dark flank markings. Dorsal tail spots match the belly cream. Female only.')
