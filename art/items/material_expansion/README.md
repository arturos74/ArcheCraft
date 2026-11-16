# Material expansion

This batch adds 22 basic inventory materials, all in the ArcheCraft creative tab.
Sturdy Ingot was excluded as requested. Recipes, food effects, planting, crop
blocks and growth are future work; the new seeds are currently ordinary items.

| Category | Items |
| --- | --- |
| Plants | Cotton Seeds, Azalea, Narcissus, Lily, Lotus, Lavender |
| Crops | Rice, Rice Seeds, Corn, Corn Seeds, Barley, Barley Seeds |
| Special materials | Thunderstruck Log, Onyx Archeum Essence, Dawn Lake Light Essence |
| Equipment components | Wooden Handle, Wooden Shaft, Leather Strip, Cloth Padding, Rope, Metal Plate, Rivet |

Registry IDs and names are listed in `items.json`. Registrations live in
`ModItems.java`; creative entries live in `ModCreativeTabs.java`. Each item has
an English name, a generated flat-item model and a transparent 48 by 48 PNG.

Sixteen sprites use ArcheAge Codex item icons with their backgrounds removed.
The global database calls the Thunderstruck Log source **Thunderstruck Tree**.
Rice, Corn and Barley seeds use the crop artwork supplied by that database.
Wooden Handle, Wooden Shaft, Leather Strip, Cloth Padding, Metal Plate and Rivet
have original icons. All cutouts and original artwork used built-in image_gen.

Source URLs, database IDs, checksums and the exact 22 image prompts are recorded
in `docs/material-expansion-icon-sources.json`. Final textures are in
`src/main/resources/assets/archecraft/textures/item/`. `preview.png` shows the
complete batch. Original downloads and generated masters are backed up under
`build/material-expansion-originals/` and `build/material-expansion-masters/`.

The Python helpers require Pillow for finalization. Run from the repository root:

```powershell
python art/items/material_expansion/fetch_sources.py
python art/items/material_expansion/write_resources.py
python art/items/material_expansion/finalize_icons.py
```

`finalize_icons.py` requires the image-generation result metadata in
`build/material-expansion-generated.json` and its referenced master images.
It preserves alpha and uses nearest-neighbor downscaling. It does not perform
background extraction itself. Rebuilding item resources does not edit Java
registrations or creative-tab entries.
