# Stonemason Workbench

Open `stonemason_workbench.bbmodel` in Blockbench. This version was rebuilt from
scratch as 22 new cuboids authored directly within a one-block footprint. It has
a low hand-hewn stone foundation, compact working pedestal, nearly cubic blue
workpiece, straight-handled leaning sledgehammer and chisel, and loose chips.
The tools use native 22.5-degree model rotations. All proportions and the original
128 x 64 pixel texture were rebuilt for this layout. The texture is embedded and
also saved as `stonemason_workbench.png`.

The bench occupies one horizontal block space: 16 x 16 model units, with the
top of the blue workpiece at 17.225 units high. The workpiece is 15% smaller in
each dimension, centered on the pedestal with its bottom resting at 10 units.
Its collision and selection shape uses three simple volumes for the foundation,
working pedestal and blue workpiece. Tools and chips are visual details. This
keeps targeting and collision inexpensive while preserving the visible model.
The shape rotates with its facing direction. The preview is a
depth-buffered software render of the textured, rotated model, not a Minecraft
screenshot.

The item is `archecraft:stonemason_workbench`, available in the ArcheCraft creative
tab. Right-click opens the shared workbench GUI, including the two-by-five input
inventory, scrollable recipe list and three-second progress arrow. Harvest the
stone bench with a pickaxe. Breaking it releases its stored items once. Adjacent
benches are independent.

Previously placed two-space Stonemason Workbenches retain their main block's
inventory and crafting progress. The obsolete second half is removed without
dropping another workbench item on the main block's first loaded server tick.
The legacy `part` property remains solely to recognize those saved second halves;
new placements create only one block.

Recipes: one vanilla `minecraft:stone` produces one `archecraft:raw_stone`;
three `archecraft:raw_stone` produce one `archecraft:stone_brick`.
Both are new ArcheCraft material items, with creative-tab entries, translations,
item models and transparent 48 x 48 database-derived icons. Their icon sources,
hashes and exact built-in image editing prompts are documented in
`docs/stonemason-item-icon-sources.json`.

`build_model.py` regenerates the project, texture, single block model, complete item
model, blockstates, collision shapes and preview. It overwrites manual edits.

The build and 26 Minecraft server tests passed, covering all workbenches,
single-space placement with blocked neighbors, independent adjacent benches,
migration of the old second half, survival and creative drops,
recipe isolation, split input stacks, exact ingredient consumption and output,
the 60-tick craft duration, progress saving, and blocked result slots. Client
appearance still needs an in-game visual check.

Targeting performance: the former 42-slice detailed shape expanded into a
71 x 60 x 34 voxel grid (144,840 cells), with 74 decomposed boxes and 510 outline
edges. Minecraft traverses this grid each frame while the crosshair targets the
block. The replacement has a 5 x 3 x 5 grid (75 cells), three boxes and 36 edges.
In the same headless Minecraft test, after ten warmup calls and averaging 50
iterations, outline traversal changed from approximately 18.50 ms to 0.11 ms per
call. Ray-targeting traversal changed from approximately 0.185 ms to 0.0064 ms.
These are isolated traversal timings, not client FPS measurements. The model
generator deliberately keeps the simple gameplay shape when rebuilding assets.
