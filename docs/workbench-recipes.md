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

After changing recipes during development, run `/reload` and reopen the menu.
Adding a new workbench block also requires adding it to the supported block list
in `ModBlockEntities.WORKBENCH`; it can reuse the existing block, menu and screen
classes. The opening packet identifies the workbench so its recipes can be filtered.
