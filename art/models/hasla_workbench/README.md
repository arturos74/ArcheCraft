# Hasla Workbench

Open `hasla_workbench.bbmodel` in Blockbench to edit the one-block jade altar.
It includes the carved guardian face, side reliefs, stone paws, dark worktop,
and cyan display sword from the reference. The embedded 128 x 64 atlas is also
saved as `hasla_workbench.png`. The front of the authoring model faces +Z;
the exported blockstate rotations make its `facing` property match the front.

The block is registered as `archecraft:hasla_workbench` and uses the shared
workbench GUI, ten material slots, result slot and three-second crafting timer.
Its first recipe is 64 Hasla Tokens of Honor for one Faded Sword of Honor.
That recipe has moved from the Anvil to this station.

Natural Abandoned Drill Camps place one station on the pavilion floor at hub-local
(35,16,38), facing the northern entrance. The full 96-block template places it at
(83,16,86). Structure rotations rotate its position and facing together.

The collision/selection shape uses three cached mass envelopes to keep crosshair
outlines inexpensive. `build_model.py` rebuilds the initial artwork, native JSON,
texture and shape source; rerunning it replaces saved artwork edits.
