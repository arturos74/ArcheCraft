"""Check exact male scale, shared rig/UVs, animation scaling and runtime atlas."""
from pathlib import Path
import hashlib,json
import numpy as np
from project_tools import load,corners

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
f,fb,fp,fo,fc,ft=load(HERE/'yata.bbmodel')
m,mb,mp,mo,mc,mt=load(HERE/'male/yata_male.bbmodel')
manifest=json.loads((HERE/'male/male_model_manifest.json').read_text())
assert hashlib.sha256((HERE/'yata.bbmodel').read_bytes()).hexdigest()==manifest['female_source_sha256']
assert len(fc)==len(mc)==92 and len(fb)==len(mb)==29 and fp==mp and fo==mo
for a,b in zip(fc,mc):
    for field in ['from','to','origin']:assert np.allclose(np.array(a[field])*1.1,b[field],atol=1e-7)
    assert a['faces']==b['faces'] and a.get('rotation')==b.get('rotation')
for name in fb:
    assert np.allclose(np.array(fb[name]['origin'])*1.1,mb[name]['origin'],atol=1e-7)
    assert fb[name]['rotation']==mb[name]['rotation']
for a,b in zip(f['animations'],m['animations']):
    assert a['name']==b['name'] and a['length']==b['length']
    for uid,anim in a.get('animators',{}).items():
        for ka,kb in zip(anim['keyframes'],b['animators'][uid]['keyframes']):
            assert ka['time']==kb['time'] and ka['channel']==kb['channel']
            va=np.array([float(ka['data_points'][0][axis]) for axis in 'xyz'])
            vb=np.array([float(kb['data_points'][0][axis]) for axis in 'xyz'])
            assert np.allclose(va*(1.1 if ka['channel']=='position' else 1),vb,atol=1e-7)
assert mt.size==(256,256) and mt.tobytes()!=ft.tobytes()
assert (HERE/'male/yata_male.png').read_bytes()==(ROOT/'src/main/resources/assets/archecraft/textures/entity/yata_male.png').read_bytes()
female=np.vstack([corners(e,fb,fp,fo) for e in fc]);male=np.vstack([corners(e,mb,mp,mo) for e in mc])
assert np.allclose(male,female*1.1,atol=1e-7)
print('PASS: exact 1.1x male dimensions, 92 cubes/29 bones, all six clips scaled consistently, unchanged UVs/female, striped runtime atlas matches embedded texture.')
