# Yata entity

The Yata is registered as `archecraft:yata`. Obtain its brown-and-cream spawn egg
from the ArcheCraft creative tab, or use:

```mcfunction
/give @s archecraft:yata_spawn_egg
/summon archecraft:yata ~ ~ ~
```

The current version is a passive pathfinding mob with 24 health. It wanders on
land, looks at nearby players, looks around, floats in water, and panics when
hurt or on fire. It has no hostile target goals and does not despawn merely
because the player moves far away. Its type, position, health and custom name
use normal Minecraft entity saving.

## Sexes and breeding

The original model and tan texture are the female Yata. Ordinary males use the
orange-and-cream striped texture with dark feet and spotted, dark-tipped ears.
Their visual model, collision dimensions, saddle and rider attachment are all
10% larger. All coats share outward-facing ears with a gentle downward tip bend.
Idle, ridden idle, wild/ridden walk and run animate from this same rest pose;
running sweeps the ears backward with soft tips rather than folding them inward.
Babies render at half the size of an adult of their own sex.

New spawn-egg/summoned Yatas receive a random male/female sex. The `Male` boolean
is synchronized to clients and saved to NBT; existing saves without it remain
female. Shift-right-click with an empty hand to see the sex in the action bar
(tamed adults also open the saddle inventory). Unnamed Yatas are identified as
Male Yata or Female Yata in their inventory name.

To breed, tame one adult male and one adult female, dismount both and feed each
one Clover. Keep them close together: they approach one another and produce one
baby. Two males, two females, babies, untamed Yatas, mounted/panicking Yatas and
parents on cooldown cannot breed. Existing horse food handling remains intact.

Each valid breeding has a **5% chance of a Black Male Yata**, a **5% chance of a
Palomino Female Yata**, a **1% chance of an Albino Female Yata**, and an **89%
chance of an ordinary Yata** with a 50/50 sex choice. Black forces male sex;
palomino and albino force female sex, regardless of the initial sex roll.
The outcomes are mutually exclusive. These odds also apply to variant parents,
with no extra inheritance bonus. Black males can breed with palomino or albino
females; two female variants cannot breed together.
The baby is tamed and inherits its
mother's owner (falling back to the father's owner if needed), without a saddle.
Vanilla breeding supplies the five-minute parent cooldown and twenty-minute
baby growth period. Feeding Clover to a tamed baby speeds up growth. Feeding an
ineligible adult does not consume breeding Clover.

For testing specific sexes:

```mcfunction
/summon archecraft:yata ~ ~ ~ {Male:1b}
/summon archecraft:yata ~ ~ ~ {Male:0b}
/summon archecraft:yata ~ ~ ~ {Variant:"black"}
/summon archecraft:yata ~ ~ ~ {Variant:"palomino"}
/summon archecraft:yata ~ ~ ~ {Variant:"albino"}
```

The male Blockbench project is `art/models/yata/male/yata_male.bbmodel`, with an
embedded striped texture, 110%-scale geometry, and all six clips. Its runtime
uses the shared canonical rig, scaled by `getAgeScale`, and selects
`textures/entity/yata_male.png`. This keeps the body, saddle, hitbox and riding
position consistent. `build_male.py` derives the male authoring assets from the
saved female; `validate_male.py` checks exact scale and matching animation/UVs.
Rebuilding the derived male project replaces edits made directly to that copy.

## Black male variant

The Black Yata has charcoal fur, soft light-gray markings across its back and
flanks, light-gray inner ears and muzzle, dark legs and a light-gray tail tuft, based on
ScreenShot0015/16/17. It is always male and measures **1.3x the original female**,
not 1.3x the ordinary male. Body, collision, saddle and rider attachment use the
same factor; babies are half their own adult size (0.65x the female adult).
The original male remains at 1.1x. Existing animations and riding/taming work for
all coats without duplicating the runtime mesh.

`Variant:"black"` is saved alongside sex, owner, age and saddle, and the variant
is synchronized to clients. A conflicting `Male:0b` cannot turn a black Yata
female. Missing or unknown variants load as ordinary Yatas. Standard spawn eggs
and ordinary summons keep their current normal male/female behavior; the black
coat is obtained by rare breeding or the explicit summon command above.

Open `art/models/yata/variants/black/yata_black.bbmodel` for its editable
130%-scale model, embedded texture and all six animation clips. `build_black.py`
derives the assets from the saved female rig; `validate_black.py` verifies exact
scale, matching UVs, clips and runtime texture. The game selects
`textures/entity/yata_black.png` and scales the shared rig to match the project.

## Palomino female variant

The Palomino Yata is based on ScreenShot0018: a muted cream/sand coat with a
warmer tan back, pale throat/belly, sparse dark flank markings, a dark muzzle,
lower legs and tail. It is always female. Its body, hitbox, saddle and rider
attachment use exactly the same 1.3x factor as the Black Yata; babies use 0.65x.
It uses the shared six-clip rig, taming, saddle inventory and riding controls.

`Variant:"palomino"` is saved/synchronized and forces female sex even with
conflicting `Male:1b` data. It breeds with ordinary or black males; ordinary
females and other palominos are not valid mates. Birth ownership, baby growth,
Clover feeding and parent cooldowns are unchanged.

The editable project is `art/models/yata/variants/palomino/yata_palomino.bbmodel`,
with an embedded 256x256 atlas and 130%-scale geometry/animation translations.
`build_palomino.py` uses `variant_authoring.py` to derive this project without
changing the existing Yatas. `validate_palomino.py` checks its scale and atlas.
The runtime selects `textures/entity/yata_palomino.png` on the shared rig.

## Albino female variant

The Albino Yata has white fur, pale feet and black hand/foot claws and white inner ears and a soft pink nose. It uses the existing wingless Yata shape. It is always female and
uses the same 1.3x adult size as black/palomino (0.65x as a baby). Hitbox, saddle
and rider attachment scale together. All existing animations, taming, riding,
Clover feeding, ownership and growth behavior apply.

`Variant:"albino"` is saved and synchronized; conflicting `Male:1b` cannot
change its sex. It can breed with ordinary or black males, with the same birth
odds as every other valid pair. Spawn eggs still produce ordinary male/female
Yatas; obtain albino through the 1% breeding result or the command above.

Open `art/models/yata/variants/albino/yata_albino.bbmodel` for its editable model,
embedded atlas and six scaled clips. `build_albino.py` derives its assets using
`variant_authoring.py`; `validate_albino.py` checks the scale, rig and atlas.
Runtime uses `textures/entity/yata_albino.png` on the shared mesh.

## Taming and riding

1. Right-click an adult wild Yata with an empty hand. It wanders while you ride
   and may throw you off with smoke particles. Keep trying until hearts appear.
2. Equip a vanilla Minecraft Saddle by right-clicking the tamed Yata with it.
   A visible leather saddle and blanket appear on its back.
3. Right-click to mount. Use WASD to steer, the normal sprint key (default Ctrl)
   to run forward, hold/release Space to charge a horse-style jump, and Shift to
   dismount. Ordinary riding uses walk; sprinting uses run and is 30% faster.
4. Shift-right-click the tamed Yata, or press E while riding, to open its saddle
   inventory. Removing the saddle removes steering control immediately.

The entity extends Minecraft's `AbstractHorse` and uses `RunAroundLikeCrazyGoal`
for the actual vanilla temper checks, repeated attempts, ejections, success
hearts, owner assignment and tame advancement. Saddling is allowed only after
taming. Tame state, temper, owner and saddle persist through saving/reloading;
older Yata saves default to wild/unsaddled. The equipped saddle drops on death.
Native horse food handling, jump input, safe dismount placement and inventory
networking are reused. Health remains 24 and base movement speed remains 0.22.
All Yata coats use player-style terrain footsteps for walking, running and
landing, including snow and layered surface sounds. Horse jump/landing clops
are replaced; jumping itself has no horse sound.

The female rider attachment is 1.42 blocks above the feet and 0.265625 blocks
behind the entity origin, rotating with the Yata; the ordinary male uses 1.1x
those offsets and all black/palomino/albino variants use 1.3x. The saddle accessory follows
the animated body bone and uses a separate 32x32 pixel atlas. The source rig,
fur texture, idle, walk and run clips are unchanged. No rearing animation or
separate jump clip is added in this version.

The model is the latest saved `art/models/yata/yata.bbmodel`, including the
artist's edits, the smaller ear flaps, toe stance and wider arms/hands. Its
texture is exported from the embedded project texture. It renders with Minecraft's
lighting, damage overlay, shadow, naming and leash-render support. A 4.2-second
idle based on the supplied video adds gentle breathing, a head lift, arm sway,
a slow tail sweep and an ear flick with delayed ear-tip/flap movement. Hind feet
remain planted. Different Yatas start at different phases; idle fades out as
they move and is disabled in water, while riding another entity or when dying.

`animation.yata.walk` is a separate 0.96-second alternating stride based on the
walking video. Only the Yata's motion was copied; the recorded rider was ignored.
It keeps the torso upright, uses small body/arm/ear movements and gentle tail
sway, and maintains a supporting foot on the ground throughout the loop.

`animation.yata.ridden_walk` is a separate, editable 0.64-second walk cycle,
retimed from the saved wild walk at 1.5x cadence. It is selected only for a
controlling player riding at normal speed. A gentle whole-rig root bounce adds
up to 0.45 model units (about 0.028 blocks) twice per cycle, lifting the body and
animated saddle slightly; the rider's physics attachment remains stable. The
cycle pace is unchanged, and the bounce is milder than the running motion.
Wild wandering retains the original
0.96-second clip; ridden sprinting and panic retain the run clip. The two walk
weights blend over five ticks when mounting/dismounting or changing gait. Travel
speed, saddle requirements and controls are unchanged by this animation change.

The separate `animation.yata.run` clip is a 0.66-second repeating stride based on
the supplied 20%-speed run recording, restored to normal speed. It adds staggered
hind-leg push/tuck/reach motion, body bounce and lean, tucked arms, swept-back
ears and a balancing tail. The visual root moves; the animation does not make
the entity physically jump or change its movement speed.

Standing uses the same idle with or without a rider, across all variants.
The editable `ridden_idle` clips also match each project's own idle, including
scaled translations. Run `art/models/yata/sync_ridden_idle.py` to synchronize
them after editing idle. Ordinary wild movement uses walk; controlled riding uses
ridden_walk. Panic goal start/stop publishes
a synchronized flag to clients. A moving,
panicking Yata blends into the run over five ticks and blends back out when it
stops or calms down. Actual movement gates the animation so it does not run in
place against a wall. Ridden sprint input also selects running; an untamed Yata
moving during a taming attempt uses run as well.
All gait weights transition over five ticks and interpolate between ticks. The
renderer weights idle, walk, ridden_walk and run together, avoiding an idle pose leaking into
the middle of a walk-to-run transition. Movement is measured from displacement
during the tick, including client interpolation, rather than requested velocity.
Hopping/rearing animations, additional color variants, custom drops and natural biome spawning
are future features.

## Updating the model

Save changes in Blockbench, then run this from the repository root using Python
with Pillow and NumPy installed:

```powershell
python art/models/yata/export_runtime.py
```

This reads the saved model without changing it and exports:

- `src/main/resources/assets/archecraft/entity/yata_mesh.json`
- `src/main/resources/assets/archecraft/entity/yata_idle.json`
- `src/main/resources/assets/archecraft/entity/yata_run.json`
- `src/main/resources/assets/archecraft/entity/yata_walk.json`
- `src/main/resources/assets/archecraft/entity/yata_ridden_walk.json`
- `src/main/resources/assets/archecraft/textures/entity/yata.png`
- `docs/yata-runtime-model.json`, recording the exact source checksum and counts.

The separate saddle accessory is built by `art/models/yata/build_saddle.py`,
which writes `entity/yata_saddle.json` and `textures/entity/yata_saddle.png` under
the mod assets. It does not alter the `.bbmodel` or embedded fur texture.

The mesh keeps bone pivots, saved rest rotations and per-face UVs. The native
renderer caches the faces and animation tracks on load and applies 29 bone
transforms during rendering. It does not parse files per frame. Mesh, animations and texture
changes take effect after a client resource reload (F3+T), or a game restart.
This version does not require GeckoLib or another animation library. Edit
`animation.yata.idle`, `animation.yata.walk`, `animation.yata.ridden_walk` or `animation.yata.run` in the saved
`.bbmodel` to adjust the animations. The runtime
exporter supports numeric local rotation, position and scale keys with linear or
step interpolation; unsupported expressions/curves cause an export error.
Run `./gradlew.bat processResources` after export when using the development
client, then F3+T; a packaged installation needs a rebuilt mod JAR and restart.

`art/models/yata/yata_idle_preview.mp4` previews the saved animation.
`art/models/yata/yata_run_preview.mp4` previews the run at normal speed.
`art/models/yata/yata_walk_preview.mp4` previews the walk at the supplied speed.
`art/models/yata/yata_ridden_walk_preview.mp4` previews the quicker mounted walk.
`create_ridden_walk.py` creates/recreates that independent clip from the saved
wild walk. Use `export_runtime.py` to preserve manual keyframe edits. Its original
project is backed up in `versions/before_ridden_walk_animation`.
`versions/before_idle_animation` preserves the project from before the idle was
added. Geometry, textures and the other three animation clips were not changed.
`animate_idle.py` reauthors this specific reference idle; use `export_runtime.py`
for normal artist edits so your keyframes are preserved.
The additional `versions/before_run_animation` backup preserves the completed
idle and model before the run was added. `animate_run.py` reauthors the reference
run; do not use it to export artist keyframe edits. `run_motion.json` records the
reference speed correction and estimated cycle timing.
`versions/before_walk_animation` preserves the model, idle and run before the
walk was authored. `animate_walk.py` reauthors the reference walk;
`walk_motion.json` records its reference and timing. Export artist edits with
`export_runtime.py` to preserve those edits.

Common registration/AI lives in `ModEntities` and `entity/YataEntity`; client-only
rendering lives in `client/YataModel` and `client/YataRenderer`. Entity rendering
is registered from the client mod entry point, keeping dedicated-server class
loading independent of client classes.
