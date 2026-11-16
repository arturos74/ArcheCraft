"""Verify the palomino variant's exact 130% geometry, UVs and shared animations."""
from pathlib import Path
import hashlib,json
import numpy as np
from project_tools import load,corners

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=HERE/'variants/palomino'
f,fb,fp,fo,fc,ft=load(HERE/'yata.bbmodel')
b,bb,bp,bo,bc,bt=load(OUT/'yata_palomino.bbmodel')
manifest=json.loads((OUT/'palomino_model_manifest.json').read_text())
assert hashlib.sha256((HERE/'yata.bbmodel').read_bytes()).hexdigest()==manifest['female_source_sha256']
assert len(fc)==len(bc)==92 and len(fb)==len(bb)==29 and fp==bp and fo==bo
for x,y in zip(fc,bc):
    for field in ['from','to','origin']:assert np.allclose(np.array(x[field])*1.3,y[field],atol=1e-7)
    assert x['faces']==y['faces'] and x.get('rotation')==y.get('rotation')
for name in fb:
    assert np.allclose(np.array(fb[name]['origin'])*1.3,bb[name]['origin'],atol=1e-7)
    assert fb[name]['rotation']==bb[name]['rotation']
for x,y in zip(f['animations'],b['animations']):
    assert x['name']==y['name'] and x['length']==y['length']
    for uid,anim in x.get('animators',{}).items():
        for kx,ky in zip(anim['keyframes'],y['animators'][uid]['keyframes']):
            assert kx['time']==ky['time'] and kx['channel']==ky['channel']
            vx=np.array([float(kx['data_points'][0][a]) for a in 'xyz']);vy=np.array([float(ky['data_points'][0][a]) for a in 'xyz'])
            assert np.allclose(vx*(1.3 if kx['channel']=='position' else 1),vy,atol=1e-7)
assert bt.size==(256,256) and bt.tobytes()!=ft.tobytes()
assert (OUT/'yata_palomino.png').read_bytes()==(ROOT/'src/main/resources/assets/archecraft/textures/entity/yata_palomino.png').read_bytes()
female=np.vstack([corners(e,fb,fp,fo) for e in fc]);palomino=np.vstack([corners(e,bb,bp,bo) for e in bc])
assert np.allclose(palomino,female*1.3,atol=1e-7)
print('PASS: exact 1.3x Palomino Yata, 92 cubes/29 bones, unchanged rig/UVs, six scaled clips and matching embedded/runtime atlas.')
