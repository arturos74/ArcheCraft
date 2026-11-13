# Smelter

Original blocky model based on the user's ArcheAge screenshot: stepped stone
oven, arched mouth, sloping pouring channel, stirring rod, side air pipe, rear
flue and turquoise ingot molds. It uses 52 cuboids and an original 128 by 128
pixel atlas, without external game textures.

Open `smelter.bbmodel` in Blockbench to edit the complete model and its embedded
texture. The preview shows the authored mesh from the front and back.

Rebuild from the repository root with Python, Pillow and NumPy installed:

```powershell
python art/models/smelter/build_model.py
```

The generator exports the editable project, preview, Minecraft assets, and
`SmelterShapes.java`. Edit the generator to keep future rebuilds reproducible.

The footprint is 32 by 32 model units (two by two horizontal blocks), authored
with the front toward positive Z. Each quadrant exports to its own block model.
Only front-left owns a block entity on normal placement; the separate controller
flag preserves ownership when saved structures are mirrored. Native Java models
use one common texture and require no custom renderer.

Collision and selection use three simple mass envelopes per quadrant rather than
individual decorative cuboids, to avoid expensive crosshair outline traversal.
