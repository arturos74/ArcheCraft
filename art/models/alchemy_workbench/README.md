# Alchemy Workbench

Open `alchemy_workbench.bbmodel` in Blockbench. This original 82-cuboid model
uses the supplied reference as a design guide: a dark wooden table, three blue
and pale reagent flasks, iron ring stand, mixing bowl, tilted open book with
illustrated parchment, small weighing balance and spilled turquoise ingredients.
The 128 x 64 pixel atlas is original and embedded in the editable project.

The footprint is 32 x 16 model units, occupying two horizontal block spaces.
The highest stopper reaches 26.6 units. The book uses Minecraft's native 45-degree
element rotation. Each half has a separate block model, with correctly shifted
rotation origins. The inventory item renders the complete bench.

The block/item ID is `archecraft:alchemy_workbench`. Either half opens the shared
workbench GUI, using its two-by-five ingredient inventory and three-second timer.
Only the primary half owns the inventory and timer. Placement checks both spaces,
and breaking either half removes the pair and drops the inventory once.

First recipe: **3 Charcoal Stabilizer + 20 Clover + 20 vanilla Poppies ->
1 Small Root Pigment**. Poppies are the requested substitute for roses. Existing
material items are reused. No separate ingredient registrations were required.

Targeting/collision is intentionally simplified to two volumes in the left half
and three in the right, with cached shapes for each facing. It does not trace
each decorative flask, book leaf or scale component. Minecraft tests enforce
a maximum of 1,000 voxel cells and 100 outline edges in each half and facing.

`build_model.py` regenerates the project, textures, split block models, complete
item model, blockstates, simple shapes and preview. It uses the shared exporter
in `art/models/common/workbench_model.py`. Running it overwrites manual edits.
The preview uses a depth-buffered software renderer; it is not an in-game image.

Build and 33 Minecraft server tests passed. Alchemy-specific checks include all
placement directions, obstruction rejection, GUI access through either half,
survival/creative drops, targeting complexity, recipe isolation, three-ingredient
network serialization, insufficient materials, exact consumption/output,
split input stacks, saved progress, repeated-click rejection and output capacity.
Client appearance still needs an in-game visual check.
