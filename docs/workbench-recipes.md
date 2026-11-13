# Workbench recipes

The Carpenter Workbench's first recipe produces one Fine Lumber from 10 Lumber
and one Small Seed Oil. Click the recipe on the left, put materials in the input
inventory in any arrangement, then click Craft. Matching materials can be spread
across multiple stacks. Each click starts one three-second (60-tick) craft. The
arrow fills as crafting advances, and Craft is disabled during the job. Materials
are consumed and the result appears when the timer finishes. Crafting continues
with the screen closed while the chunk is loaded; the active recipe and elapsed
ticks are saved with the block so it can resume after loading.

A compatible result stack can grow up to its stack limit. An incompatible or full
result slot blocks starting a job; if it becomes blocked during a job, progress
pauses until there is space again. Removing required materials cancels the job
and resets progress without consuming anything. Breaking the bench during a job
drops its inventory, including the unconsumed materials. Jobs do not auto-repeat.

The ingredient inventory has two rows of five slots. The recipe panel shows
three compact entries at a time, with output names and ingredient icons/counts.
Hover an entry for full ingredient names, and use the wheel or scrollbar to
navigate longer lists.

Older 24-slot workbenches recover their materials into the ten input slots and
move their result into the new output slot. Stacks are merged where possible.
Anything that cannot fit is dropped beside the bench when it next ticks (or when
it is broken). Pending overflow is saved so it also survives saving before that
first tick. Active crafting progress is retained when its ingredients still fit.

The Carpenter Workbench now occupies two horizontal spaces. Both halves open
the same GUI, and only the left half stores items and advances crafting. Place
a fresh bench to use the two-part model; older single-block benches can be
broken and placed again, with their stored materials collected from the ground.

Recipe definitions live in `src/main/resources/data/archecraft/recipe/workbench/`.
The serializer type is `archecraft:workbench`. The `workstation` field is the block
ID that should list the recipe. For example:

```json
{
  "type": "archecraft:workbench",
  "workstation": "archecraft:carpenter_workbench",
  "ingredients": [
    { "item": "archecraft:lumber", "count": 10 },
    { "item": "archecraft:small_seed_oil", "count": 1 }
  ],
  "result": { "id": "archecraft:fine_lumber", "count": 1 }
}
```

Ingredients currently specify exact item IDs and counts. The menu lists only
recipes for its workbench, sorted by recipe ID. The recipe panel supports the
mouse wheel and dragging the scrollbar when there is more than one recipe.
The selected recipe and inventory are synchronized with the server, which
validates materials and output space before consuming anything.

Recipes can optionally set `"name"` to a translation key. If omitted, the output
item's name is shown. **Disintegration: Gilda Star** uses
`recipe.archecraft.disintegration_gilda_star`; its workstation is
`archecraft:archeum_workbench`, with one `archecraft:gilda_star` as the ingredient
and four `archecraft:gilda_dust` as the output. Its definition is
`src/main/resources/data/archecraft/recipe/workbench/disintegration_gilda_star.json`.
The name is synchronized with the recipe and shown in full in its tooltip.

The Stonemason Workbench (`archecraft:stonemason_workbench`) uses the same GUI and
timer, with its own recipe list. One vanilla `minecraft:stone` block can be
converted into one `archecraft:raw_stone` item using
`src/main/resources/data/archecraft/recipe/workbench/raw_stone.json`.
The Stone Brick recipe converts three ArcheCraft
`raw_stone` material items into one `stone_brick` material item. The definition is
`src/main/resources/data/archecraft/recipe/workbench/stone_brick.json`. Both new
materials are available in the ArcheCraft creative tab. The bench occupies one
horizontal block space and requires a pickaxe for harvesting. Old two-space
Stonemason benches remove their obsolete second half on their first loaded tick,
preserving the main block's inventory and crafting progress.

After changing recipes during development, run `/reload` and reopen the menu.
The Alchemy Workbench (`archecraft:alchemy_workbench`) occupies two horizontal
spaces and uses the same GUI, input inventory and crafting timer. Its first
recipe is three `archecraft:charcoal_stabilizer`, twenty `archecraft:clover` and
twenty vanilla `minecraft:poppy`, producing one `archecraft:small_root_pigment`.
Poppies are used in place of roses. The definition is
`src/main/resources/data/archecraft/recipe/workbench/small_root_pigment.json`.

Adding a new workbench block also requires adding it to the supported block list
in `ModBlockEntities.WORKBENCH`; it can reuse the existing menu and screen
classes. Two-space benches extend `TwoBlockWorkbenchBlock` and supply their own
shapes. The opening packet identifies the workbench so its recipes can be filtered.

Two-block model orientation: the Carpenter, Archeum and Alchemy authoring models
have their fronts toward positive Z (south). Blockstate mappings add a half-turn
and swap the source model halves so the state `facing` direction points toward
the placing player. `TwoBlockWorkbenchBlock.getShape` uses the corresponding
opposite source half and facing to keep targeting and collision aligned. The
placed halves and primary inventory location are preserved, including for
existing benches. Model generators retain this orientation mapping on rebuild.

The Smelter (`archecraft:smelter`) occupies a 2 by 2 horizontal footprint. All four
spaces must be replaceable before placement succeeds; one item places the whole
structure. Its front faces the placing player. Every section opens the same GUI,
with only one section storing the inventory and advancing the three-second
timer. Breaking any section removes all four and drops the stored materials;
harvesting with a pickaxe returns one Smelter item. Creative removal returns no
Smelter item. Decorative geometry uses a few cached targeting/collision volumes
per section to keep outline rendering inexpensive.

Its first recipe consumes three **Archeum Ore block items**
(`archecraft:archeum_ore`) and produces one `archecraft:archeum_ingot`. This uses
the ore block rather than the separate `archecraft:raw_archeum` material. The
definition is `src/main/resources/data/archecraft/recipe/workbench/archeum_ingot.json`.
It uses the existing workbench inputs, Craft button, progress arrow and result
slot, without an additional fuel slot.

The four-part authoring model faces positive Z (south), with front sections in
Z=16..32 and back sections in Z=0..16. Blockstate rotation maps south to 0,
west to 90, north to 180 and east to 270 degrees. Section positions and shapes
use that same rotation. `controller` is independent of `part` so reflection of a
saved structure preserves the block entity and inventory at its transformed
position. The editable model is `art/models/smelter/smelter.bbmodel`; rebuilding
`art/models/smelter/build_model.py` exports all four Minecraft models, item
model, blockstates, texture, cached shapes and preview.

The Anvil (`archecraft:anvil`) occupies a single horizontal block. It uses the
shared workbench GUI and three-second timer, with its own recipe list. Its first
recipe consumes 64 `archecraft:hasla_token_honor` and produces one
`archecraft:faded_sword_of_honor`. The existing Honor token's display name is now
**Faded Token of Honor**; its registry ID is unchanged so existing stacks remain
usable. Ingredients can be split across the input slots. The recipe definition
is `src/main/resources/data/archecraft/recipe/workbench/faded_sword_of_honor.json`.

Faded Sword of Honor is currently an unstackable result item with a temporary
vanilla iron-sword model. Custom weapon art, combat attributes and durability are
left for later. The Anvil itself has an original blocky stump-mounted model,
faces the placing player, and requires a pickaxe for harvesting. Its model
source is `art/models/anvil/anvil.bbmodel`; `art/models/anvil/build_model.py`
rebuilds its assets and three cached collision/targeting volumes.
