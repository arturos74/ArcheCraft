# Rafflesia model

Open **rafflesia.bbmodel** in Blockbench with **File > Open Model**. The painted
256 x 256 pixel texture is embedded. `rafflesia.png` is also available separately.
The model uses the built-in Bedrock Entity format for its editable cuboids and
bone hierarchy, matching the other ArcheCraft creature projects.

This first pass follows the two foreground Rafflesias in **ScreenShot0057.jpg**:
a broad purple five-petal flower, hollow dark trumpet, magenta forked tongue,
olive calyx with two pointed bracts, pale S-shaped neck, orange leaf collar,
thorny vine arms, a tapered segmented seed-pod abdomen, and two branching root
feet. The hidden surfaces are an interpretation of the supplied view.

The front is **-Z**, the feet touch **Y=0**, and 16 model units equal one block.
The creature is approximately 2.6 blocks tall. Exact bounds are recorded in
`model_manifest.json`. Front, rear, side and face previews are provided, with a
combined view in `rafflesia_preview.png`.

The rig has separate controls for:

- Body and collar; two neck joints and head.
- Each petal, mouth, tongue joints, tongue forks and rear bracts.
- Each upper arm, forearm and hand leaf.
- Each root leg, ankle and foot.
- Six connected abdomen sections for later swaying or curling.

The Animate tab contains **empty** `idle`, `walk`, `attack` and `death` templates.
No motion has been authored yet. This is the editable model base; an in-game
entity, spawn egg, AI and spawn rules have not been added.

`rafflesia.geo.json` and `rafflesia.animation.json` are interchange exports.
Save your Blockbench changes in the `.bbmodel` file to preserve the complete
project. `build_model.py` recreates the initial model and previews and will
replace model or texture edits if rerun; keep a copy before regenerating.
