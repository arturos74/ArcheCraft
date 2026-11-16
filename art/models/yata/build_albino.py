"""White female Yata with a pink nose, using the existing wingless rig."""
from variant_authoring import build_variant

def paint(point, material, name, face, e, context):
    if material == 'fur':
        return [236, 235, 233]
    if material == 'cream':
        return [244, 242, 239]
    if material == 'inner':
        return [236, 235, 233]
    if material == 'nose':
        return [220, 158, 164]
    if material == 'foot':
        return [224, 222, 219]
    if material == 'claw':
        return [26, 25, 23]
    if material == 'eyelid':
        return [207, 168, 171]
    if material == 'eye':
        return [86, 40, 45]
    if material == 'white':
        return [252, 249, 245]
    return [236, 235, 233]


if __name__ == '__main__':
    build_variant('albino', 'Albino Female Yata', 'female', paint,
        'Shared wingless canonical rig at 1.3 scale. White fur, pale feet, black hand/foot claws, '
        'white inner ears and a soft pink nose. '
        'Female only; same size as black/palomino.')
