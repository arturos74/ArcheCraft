"""Copy each saved Yata's own idle into its editable ridden_idle clip."""
from pathlib import Path
import copy
import hashlib
import json
import shutil
import uuid

from project_tools import write

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
IDLE = 'animation.yata.idle'
RIDDEN_IDLE = 'animation.yata.ridden_idle'


def sync(project_path):
    original = project_path.read_bytes()
    project = json.loads(original)
    before = copy.deepcopy(project)
    source = next(c for c in project['animations'] if c['name'] == IDLE)
    index = next(i for i, c in enumerate(project['animations']) if c['name'] == RIDDEN_IDLE)
    previous = project['animations'][index]
    clip = copy.deepcopy(source)
    clip.update(name=RIDDEN_IDLE, uuid=previous['uuid'], selected=previous.get('selected', False))
    # Bone UUIDs address this project's rig. Keyframes need separate editor identities.
    for animator in clip['animators'].values():
        for key in animator['keyframes']:
            key['uuid'] = str(uuid.uuid5(uuid.UUID(clip['uuid']), key['uuid']))
    project['animations'][index] = clip
    animation_path = project_path.with_suffix('.animation.json')
    external = json.loads(animation_path.read_text())
    external['animations'][RIDDEN_IDLE] = copy.deepcopy(external['animations'][IDLE])

    assert {k: v for k, v in project.items() if k != 'animations'} == {
        k: v for k, v in before.items() if k != 'animations'}
    assert all(a == b for a, b in zip(before['animations'], project['animations']) if a['name'] != RIDDEN_IDLE)
    backup = project_path.parent / 'versions/before_matching_ridden_idle'
    if not backup.exists():
        backup.mkdir(parents=True)
        for path in (project_path, animation_path):
            shutil.copy2(path, backup / path.name)
    write(project_path, project)
    write(animation_path, external)
    print(f'{project_path.relative_to(ROOT)}: ridden_idle matches {source["length"]}s idle ({len(clip["animators"])} bones)')
    return hashlib.sha256(original).hexdigest(), hashlib.sha256(project_path.read_bytes()).hexdigest()


if __name__ == '__main__':
    projects = [HERE / 'yata.bbmodel', HERE / 'male/yata_male.bbmodel']
    projects += sorted(HERE.glob('variants/*/yata_*.bbmodel'))
    hashes = {str(p.relative_to(ROOT)).replace('\\', '/'): sync(p) for p in projects}
    # Refresh provenance only when it matched the actual pre-edit source.
    manifests = [ROOT / 'docs/yata-runtime-model.json', *HERE.glob('male/*model_manifest.json'),
                 *HERE.glob('variants/*/*model_manifest.json')]
    for path in manifests:
        data = json.loads(path.read_text())
        for key, value in list(data.items()):
            if key.endswith('sha256'):
                for old, new in hashes.values():
                    if value == old:
                        data[key] = new
                        break
        write(path, data)
