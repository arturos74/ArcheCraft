# Archeum Workbench

Open `archeum_workbench.bbmodel` in Blockbench. This original blocky interpretation
of the supplied reference includes a wooden table, a dark engraved processor,
stepped hopper and hand crank, scattered blue/mint crystals and metal tools.
The 128 x 64 texture is embedded and also saved as `archeum_workbench.png`.
The preview is a software render of the same cuboids and texture, not an in-game
screenshot. The footprint is 32 x 16 units (two horizontal spaces); the top of
the hand crank reaches 32 units above the feet.

Place `archecraft:archeum_workbench` from the ArcheCraft creative tab or `/give`.
It uses the same menu, two-by-five input inventory, three-second crafting timer,
and progress arrow as the Carpenter Workbench. Either half opens the same GUI.
Its recipe list is filtered by the Archeum Workbench's block ID.

First recipe: **Disintegration: Gilda Star**, consuming one Gilda Star to produce
four Gilda Dust. Gilda Dust is also registered as a new item with its own sprite.
Icon source and the exact built-in image editing prompt are recorded in
`docs/gilda-dust-icon-source.json`.

`build_model.py` regenerates the editable model, texture, item model, two block
models, blockstates, collision shapes and preview. It overwrites manual edits.
Collision boxes are derived from the split model and rotate with each half.

The shared `TwoBlockWorkbenchBlock` implements placement, rotation, ownership of
the inventory and safe removal of both halves. `ArcheumWorkbenchBlock` supplies
its model-specific shape; both benches share `WorkbenchBlockEntity`,
`WorkbenchMenu`, and `WorkbenchScreen`.

Build and 19 Minecraft server checks passed, including both benches, workstation
recipe isolation, survival/creative drops, exact four-dust output, output stack
limits, repeated-click rejection, and progress saving. Visual appearance still
needs an in-game check.
