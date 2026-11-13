# Starshard Vein

Open `starshard_vein.bbmodel` with File > Open Model in Blockbench. The original
64 x 32 pixel texture is embedded, so the model can be moved without losing it.
All 20 pieces are named and individually editable. The stepped silhouette fits
within one Minecraft block (16 x 16 x 16 model units).

The reference informed the dark, tapered rock silhouette. The earlier reference
informed the red mineral ribbons and sparse pale inclusions. Geometry and pixel
art are original assets; no imagery was extracted from the screenshots.

Minecraft exports are already placed at:

- `src/main/resources/assets/archecraft/models/block/starshard_vein.json`
- `src/main/resources/assets/archecraft/textures/block/starshard_vein.png`

The model is registered as the placeable `archecraft:starshard_vein` block, with
an item in the ArcheCraft creative tab, matching collision/outline geometry and
waterlogging. Any pickaxe harvests the block itself. Natural generation and ore
chip drops are not implemented. The block emits light level 3, matching magma.
Red pixels use the ordinary block texture.

The preview is a software render of the exported geometry and mapped atlas, not
an in-game screenshot. JSON bounds, face UV ranges, texture references and matching
geometry were checked by the build script; the model has not been opened in the
Blockbench app or tested in Minecraft.

`build_model.py` regenerates every asset and preview using Python and Pillow.
It overwrites manual edits, so only rerun it when intentionally rebuilding.

Format references:
- https://blockbench.net/wiki/docs/bbmodel/
- https://github.com/JannisX11/blockbench/blob/master/js/formats/bbmodel.js
