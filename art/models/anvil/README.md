# Anvil

One-block stump-mounted anvil based on the user's reference. Includes a stepped
iron body and horn, wood end grain and bark, hanging hammer and tongs, and a
decorative blue blade. The crafted sword item uses a temporary vanilla model;
its art is independent of the decorative blade on this workbench.

Open `anvil.bbmodel` in Blockbench to edit the model and embedded original
128 by 64 pixel texture. There are 29 cuboids, all within one horizontal block.
The front faces positive Z in the authored model. Blockstate rotations align
that front with the placing player.

Rebuild from the repository root using Python with Pillow and NumPy installed:

```powershell
python art/models/anvil/build_model.py
```

The generator writes the Blockbench project, preview, texture, Minecraft models,
blockstates, and `AnvilWorkbenchShapes.java`. Edit the generator to preserve
changes across rebuilds. Targeting and collision use only three coarse mass
volumes, independent of the decorative cube count.
