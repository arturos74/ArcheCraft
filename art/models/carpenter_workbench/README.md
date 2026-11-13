# Carpenter Workbench

Open `carpenter_workbench.bbmodel` in Blockbench. The full model has named groups
for the frame, shelf, tabletop, blue stool, tools, and loose boards. Its original
128 x 64 pixel texture is embedded and also supplied as `carpenter_workbench.png`.

The model was built from cuboids using the supplied reference as a design guide.
Geometry and pixel art are original. The footprint is 32 x 16 model units: two
Minecraft block spaces side by side. The wooden tabletop is 14 units high, and
the stool reaches 22 units high. The preview renders this geometry and texture
in software; it is not an in-game screenshot.

The block is `archecraft:carpenter_workbench`. Its left half owns the inventory
and timer; its right half opens that same menu. Placement checks both spaces,
rotates the model to face the player and consumes one item. Either half can be
broken to remove the complete bench. Survival drops one bench item; creative
drops no bench item. Stored materials are released once in either mode. Pistons
cannot move this block.

Place a fresh bench after restarting the game. Benches saved as the previous
single block should be broken and placed again to create both halves; collect
their dropped contents before replacing them.

Minecraft assets:

- `src/main/resources/assets/archecraft/models/block/carpenter_workbench_left.json`
- `src/main/resources/assets/archecraft/models/block/carpenter_workbench_right.json`
- `src/main/resources/assets/archecraft/models/item/carpenter_workbench.json`
- `src/main/resources/assets/archecraft/blockstates/carpenter_workbench.json`
- `src/main/resources/assets/archecraft/textures/block/carpenter_workbench.png`

`build_model.py` regenerates the project, texture, both block models, full item
model, collision/selection shapes and preview. Rerunning it overwrites manual
edits. Collision boxes are derived from the split model and rotate with each half.

The server checks cover placement in four directions, occupied second spaces,
GUI access and crafting from either half, and breaking either half in survival
and creative. Existing crafting, progress-save and inventory migration checks
also passed. Client appearance still needs an in-game visual check.
