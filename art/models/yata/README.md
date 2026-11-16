# Yata mount base

Open **yata.bbmodel** in Blockbench. The pixel texture is embedded, so it opens
without having to find or import a separate image. `yata.png` is also supplied
for painting outside Blockbench.

This original project is the **female**. Open `male/yata_male.bbmodel` for the
striped male, with 10% larger geometry and scaled animation translations.
`male/yata_sexes_preview.png` compares them at the same world scale. Runtime
shares the rig with a sex scale and separate male atlas; baby visuals are half
adult size. Male/female sex is saved, and tamed opposite-sex adults can breed
using Clover. Same-sex pairs cannot breed. Each birth has a 5% chance to be the
black male, 5% to be the palomino female, 1% to be the albino female, and 89%
to use the normal male/female choice.

All Yatas share the approved outward ear pose: mirrored 70-degree
turns at the ear roots, with the upper ears gently bent down 25 degrees at
their existing tip hinges. Ear animation rotations are rebased onto this pose,
with soft tip movement during running. Body and leg animation are preserved.
`yata_all_coats_ears.png` shows all five coats with the updated ears.
Idle, ridden_idle, walk, ridden_walk and run all use the new rest pose.
`yata_outward_ears_comparison.png` shows the original before/after trial.
The previous female project is in `versions/before_outward_ears/`.
`yata_flopped_ears_comparison.png` shows the additional downward bend; the
previous outward-only pose is in `versions/before_downward_ear_flop/`.
Each project's `versions/before_shared_floppy_ears/` backs up its previous assets.

Open `variants/black/yata_black.bbmodel` for the **Black Male Yata**: charcoal
fur, soft light-gray markings, light-gray inner ears/muzzle and tail tuft. Its body is 30%
larger than the original female, with scaled translations for all six clips.
`variants/black/yata_black_comparison.png` shows the relative size. Runtime size,
hitbox, saddle and riding position scale together. `build_black.py` regenerates
this derived project, and `validate_black.py` checks its geometry and atlas.

Open `variants/palomino/yata_palomino.bbmodel` for the **Palomino Female Yata**:
muted sand/cream fur, tan back, sparse dark flank markings, dark muzzle, legs and
tail. It is the same 1.3x size as the black variant. `build_palomino.py` and
`variant_authoring.py` derive its separate atlas/scaled rig; `validate_palomino.py`
checks the result. The other Yata projects and textures are preserved.

Open `variants/albino/yata_albino.bbmodel` for the **Albino Female Yata**:
white fur and inner ears, a pink nose and pale feet and black hand/foot claws, using the existing
wingless shape. It is the same 1.3x size as black/palomino. `build_albino.py`
derives the embedded atlas and scaled rig; `validate_albino.py` verifies them.
It is a female-only 1% breeding result, with all shared riding/animation behavior.

The editable model is now used by the spawnable NeoForge entity
`archecraft:yata`, with a spawn egg and passive AI. The game renders its saved
rig with a reference-based 4.2-second idle, 0.96-second wild walk, 0.64-second
ridden walk and 0.66-second run. Ordinary wild movement uses walk; normal
controlled riding uses ridden_walk; sprinting/panic use run. Transitions blend
over five ticks. Horse-style taming, vanilla saddles, WASD riding, sprinting and
charged jumping are implemented. Custom sounds and hopping/rearing animations
are future work. See `docs/yata-entity.md` for taming instructions, commands and model
export instructions.

The shape follows the original Yata reference, with oversized ears, a long
muzzle, small bent front arms, powerful hind legs, broad three-toed feet, and
a long tail with a pale brush. The updated palette follows the second reference:
muted brown fur, taupe ear interiors and legs, gray-beige cream patches, and
dark nose and claws. The saved model has 92 textured cuboids and 29 named bones,
including the user's shortened tail.

## Scale

16 model units equal one Minecraft block. The body and suggested gameplay
hitbox are in the horse-mount range. The ears and tail extend beyond the body:
the posed visual mesh is approximately 1.15 blocks wide, 2.73 blocks tall to the
ear tips, and 3.30 blocks from nose to tail tip. The riding guide is approximately
1.40 blocks above the ground, behind the upright neck. The long tail accounts
for much of the overall visual length.

`yata_preview.png` and `yata_legs_preview.png` show three-quarter and side views
of the current saved model. The side view marks hip, knee and ankle positions.
`yata_scale.json` records exact bounds and the rider point.
The 1.3964844-wide by 1.6-high hitbox matches the Minecraft
1.21.1 horse registration in the project's cached mapped source; it has been
registered and applied to the entity.

## Starting animations

1. Open `yata.bbmodel` and switch to **Animate**.
2. Select the completed `animation.yata.idle`, `animation.yata.walk`, `animation.yata.ridden_walk` or
   `animation.yata.run`, `animation.yata.ridden_idle`, or the empty `animation.yata.hop` clip.
3. Select the bone you want to move, place the timeline cursor, and add keys.
   Ridden idle matches the normal 4.2-second idle in every Yata project. Only hop is still a template.
4. Save your working project as a new `.bbmodel` file to retain your animation
   work independently of the generator.

The file uses Blockbench's built-in **Bedrock Entity** authoring format because
it supports a bone rig and the Animate workspace without a modeling plugin.
That authoring format does not automatically make this a Java Edition entity.
The native Java renderer uses a bone-local mesh and animation tracks exported
from the saved project by `export_runtime.py`. Numeric local linear/step keys
are supported. Run the exporter, then Gradle `processResources` and reload with
F3+T in the development client. Keep bone names stable.

Blockbench format reference:
https://www.blockbench.net/wiki/blockbench/formats/

### Bone hierarchy

```text
root
  body
    chest
      neck
        head
          jaw
          ear_left -> ear_left_tip, ear_left_flap
          ear_right -> ear_right_tip, ear_right_flap
          lead_anchor
      left_upper_arm -> left_forearm -> left_hand
      right_upper_arm -> right_forearm -> right_hand
    tail_base -> tail_mid -> tail_tip
    rider_seat
  left_thigh -> left_shin -> left_foot
  right_thigh -> right_shin -> right_foot
```

`root` moves the whole animal, while `body` lets you add torso bounce separately
from the hind-leg chains. The small `rider_seat` and `lead_anchor` bones are empty
attachment guides, not visible geometry. Leg and arm bones have nonzero rest
rotations that form the bent reference pose; preserve those defaults when
starting your animations.

### Hind legs

The thighs angle forward toward the knees, and the lower legs slope backward
from knee to ankle. The raised ankle/heel is about 6 model units above the ground.
Each foot slopes forward and downward from that joint to three short, flat toe
pads. Only the toe pads contact the ground; the heel and sloping foot remain
raised. The upper end of the sloped foot meets the ankle pivot exactly.

In the neutral rig the thigh rotation is +32 degrees around X, the shin adds
-72 degrees (a net -40-degree backward slope), and the foot bone adds +40.
The sloped foot cube has an additional roughly 38-degree X rotation, while the
toe pads remain level. This preserves the torso and riding-point height.

`left_shin` and `right_shin` pivot at the knees; `left_foot` and `right_foot`
pivot at the ankles. `yata_legs_preview.png` shows the profile joint chain:
cyan = hip, yellow = knee, pink = ankle. The current saved Blockbench 5 project,
its embedded texture, blank clips, and shortened tail were preserved by applying
the leg changes directly. The pre-change file is in `versions/before_leg_fix/`.
The previous flat-foot stance is preserved in `versions/before_toe_stance/`.

### Floppy ears

Each ear now has two controls. `ear_left` and `ear_right` retain the original
root pivots at the skull for turning the whole ear. The new `ear_left_tip` and
`ear_right_tip` bones pivot halfway up the broad ear. The upper shell and inner
lining follow their corresponding tip bone, with matching geometry boundaries
at the hinge. Both tips start with zero rotation, preserving the upright base
pose and existing whole-ear controls.

Animate the tip bones to add flopping. In this author's coordinate convention,
roughly -40 to -70 degrees around X folds an upper ear forward; a little Z
rotation lets it droop to the side. Offset the two ears' keyframe times or angles
to make the motion less uniform. Those angles are suggestions for posing, not
pre-applied animation. `yata_ear_pivots.png` demonstrates neutral and bent poses;
cyan dots mark the two hinge points. The demonstration is not a saved animation.

### Smaller lower ear flaps

The paired smaller lobes beneath the main ears follow the additional close-up
reference. Their controls are `ear_left_flap` and `ear_right_flap`, parented to
the corresponding main ear root. Each flap has its own pivot and six cuboids
forming a tapered outer shell and matching inner lining. They use existing fur
and inner-ear UV regions without changing painted pixels. Flap motion is
independent of the large ear-tip hinges.

`yata_ear_flaps_preview.png` shows the full model and head close-up. The saved
project before this addition is preserved in `versions/before_ear_flaps/`.

### Hand claws

Each hand has three separate dark claws, each with a narrower hooked tip.
The paws and spacing across the claws are 50 percent wider than the first draft.
Claw length is restored to the original shorter version; the broader palm and
spread give the hands their larger silhouette.
Upper arms and forearms are also 50 percent wider than the first draft, tapering
from the shoulders toward the wrists to match the broader hands. Their lengths,
rest rotations and joint pivots are retained.
They are children of `left_hand` or `right_hand`, so they follow those existing
animation controls. The original paw geometry, saved edits, texture pixels and
animation clips were retained; the claws reuse the original nail UV regions.
Shared regions are recorded explicitly in `yata_uv_layout.json`.

`yata_hand_claws_preview.png` shows the whole model and a close view of the hands.
The pre-change project is saved in `versions/before_hand_claws/`.

## Files and rebuilding

- `yata.bbmodel`: main editable model with embedded texture and empty clips.
- `yata.png`: original 256 by 256 pixel fur atlas, with separate face islands.
- `yata.geo.json`: Bedrock-style geometry export, with the bone hierarchy intact.
- `yata.animation.json`: Bedrock idle/ridden_idle/walk/ridden_walk/run export and an empty hop template.
- `sync_ridden_idle.py`: copies each project's own idle into ridden_idle, retaining variant-scaled movement.
- `yata_idle_preview.mp4`, `yata_idle_poses.png`: animated preview and key poses.
- `yata_run_preview.mp4`, `yata_run_poses.png`: normal-speed run preview and key poses.
- `yata_walk_preview.mp4`, `yata_walk_poses.png`: walk preview and key poses, without the reference rider.
- `yata_ridden_walk_preview.mp4`, `ridden_walk_motion.json`: faster ridden walk preview and timing.
- `add_ridden_walk_bounce.py`: gentle root hop added to the existing saved ridden walk;
  its pre-bounce project is preserved in `versions/before_ridden_walk_bounce_animation`.
- `idle_motion.json`: reference timing and authoring controls.
- `run_motion.json`: slowed reference timing, speed correction and run notes.
- `walk_motion.json`: walking reference timing and notes.
- `build_saddle.py`, `yata_saddle_model.json`, `yata_saddle_preview.png`: the separate
  visible saddle accessory. The original Yata project and texture are untouched.
- `yata_uv_layout.json`: maps every face to its editable rectangle in the atlas.
- `yata_preview.png`, `yata_front.png`: software renders of the actual cuboids.
- `yata_ear_pivots.png`: neutral and floppy-ear posing comparison.
- `yata_legs_preview.png`: current side view and leg-joint guide.
- `yata_hand_claws_preview.png`: full model and close view of both hands.
- `yata_ear_flaps_preview.png`: full model and close view of the lower ear flaps.
- `yata_scale.json`: visual bounds, suggested future hitbox and attachment guide.
- `validate_model.py`: geometry, rig, UV, animation and export consistency checks.
  Its optional `--check-generated-pose` flag also checks the original generated
  leg stance; leave it off when validating a project with hand-edited feet.
- `project_tools.py`: shared reader, geometry exporter and renderer for saved
  Blockbench 4 and 5 projects.
- `fix_hind_legs.py`: apply the leg correction directly to a saved model,
  retaining its other edits, texture and animation data.
- `shape_feet.py`: reshape the saved model's feet into the raised-heel,
  toe-planted stance. It is also applied at the end of `build_model.py`.
- `add_hand_claws.py`: add the six claws to a saved project while preserving
  existing elements, bones, texture and animation data.
- `add_ear_flaps.py`: add two smaller independently movable ear flaps to a saved
  project, retaining its existing geometry and texture.
- `export_runtime.py`: bake the latest saved project into the runtime static
  entity mesh and texture, without changing the editable model.

Rebuild from the repository root with Python, Pillow and NumPy:

```powershell
python art/models/yata/build_model.py
python art/models/yata/validate_model.py
```

Rebuilding overwrites these generated authoring files. Save hand-edited model
and animation work under a different filename before rebuilding.

The initial orange model and its texture are preserved under
`versions/orange_base/` for reference.

Texture pixels are painted procedurally on the model's UV islands; no external
game texture was extracted. Geometry and colors were modeled from the user's
reference. Export coordinate conventions follow the official Blockbench codec:
https://github.com/JannisX11/blockbench/blob/v4.12.4/js/io/formats/bedrock.js

The Blockbench UI check could not run because the desktop connection returned
`foreground window did not report a process id`; the standalone file checks
verify the authoring/export data and software previews instead.
