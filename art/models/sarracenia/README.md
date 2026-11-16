# Sarracenia mob model

Open **sarracenia.bbmodel** in Blockbench using File > Open Model. The texture
is embedded, so it should appear immediately. `sarracenia.png` is also provided
as a separate editable atlas. Save your edits to the `.bbmodel` file.

This is an editable, textured Bedrock entity model made from 110 cuboids. It has
a stepped bulb, a hollow pitcher mouth with an orange rim, a mouth-sized leaf lid,
golden thorns, short roots, two long tendrils swept backward, and a short shared
rear stalk that forks into two broad drooping leaves.
The supplied front/back/side images are software previews of this same model.

The long tendril groups are:

- `back_stem_left_outer`
- `back_stem_right_outer`

Each has two nested bend groups and a leaf group with a pivot at the blade's
attachment. `rear_stalk` and `rear_stalk_tip` form the shared stalk, with
`rear_fork_left` and `rear_fork_right` branching into the two broad leaves. Each
broad blade has its own leaf pivot. The body, mouth, hood, and roots have separate
groups as well.

The Animate tab includes `animation.sarracenia.idle`, a 4.8-second loop based
on the supplied video: a gentle sway, then a larger fidget with alternating stem
sweeps, trailing leaves, body rocking, and leaf-lid bobs. The broad rear leaves
follow their common stalk, with smaller independent flaps. The reference's motion
is approximated by editable keys at 20 samples per second. The saved animation
is also exported in `sarracenia.animation.json`. Watch
`sarracenia_idle_preview.mp4` to preview two loops.

`animation.sarracenia.walk` is a separate 0.92-second loop based on the side
and front walking videos. It uses an in-place bobbing shuffle with forward/back
rocking, a little lateral sway, curling tendrils, and delayed blade flutter. The
lid stays lower while walking. Root height is keyed to avoid sinking the short
toes below the floor. Keys are sampled at 50 per second. The existing idle and
all geometry/texture data are preserved. `sarracenia_walk_preview.mp4` shows
six loops from front and side angles; `walk_motion.json` records the references.

The front faces -Z and the feet sit at Y=0. There are 16 model units per block.
The current model is approximately 2.45 blocks tall. Its tendrils reach backward
past the body; see `model_manifest.json` for the complete bounds. Those dimensions
are a starting point for later entity work.

The model is integrated as the hostile `archecraft:sarracenia` entity, with a
spawn egg and natural spawns restricted to the registered Hasla structure. See
`docs/sarracenia-entity.md` in the repository for gameplay and spawn details.
`sarracenia.geo.json` remains an interchange export; the native renderer uses
the mesh and animation resources created by `export_runtime.py`. Run that exporter
after saving Blockbench edits to update the in-game artwork.

`build_model.py` reconstructs the model and previews, retaining unchanged face
textures and animation tracks for surviving groups. **Do not rerun it after
editing the model in Blockbench unless you intend to replace your geometry
edits.** `animate_idle.py` reauthors the idle only; `animate_walk.py` reauthors the
walk only. Both preserve geometry and other clips. `validate_model.py` checks the saved model without
modifying it; `preview_idle.py` checks the saved animation and can render it with
`--render`. Add `--walk` to check or render the saved walking clip instead.
