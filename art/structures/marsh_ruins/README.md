# Abandoned Drill Camp

The full site is **96 x 36 x 96**, assembled from four **48 x 36 x 48** sections.
The pavilion contains a carved teal Hasla Workbench for Hasla weapon crafting;
its natural scenery shares the swamp vegetation. Three sections provide shallow-swamp
habitat with open roaming routes and two broken masonry ruins each. Their ruins
use stone bricks, mossy stone bricks, cobblestone and mossy cobblestone, including
matching slabs/stairs. Sarracenias spawn naturally inside registered camp pieces, during the day or night.

The scenery uses four tree silhouettes: crooked willows, broad umbrella oaks,
shorter spreading oaks, and tall forked mangrove trees. Hanging vines have leaf
supports, so they survive normal template placement. Mixed grass, moss, mud and
coarse dirt surround irregular half-block puddles, with tall grass, large ferns,
reeds and lily pads. Dry central routes remain clear of water, trunks and ruins.
Natural Swamp biome tint supplies the grass and leaf colors.

The pavilion has one north-facing Hasla Workbench at local (35,16,38), with a clear
wood floor around it. Its first recipe consumes 64 Hasla Tokens of Honor and
produces one Faded Sword of Honor in three seconds. It opens the shared workbench
GUI. No bookshelves, bed, containers, furnace or carpet are included.
The lookout's foundation extends down to solid hillside terrain, and its jagged
battlements remain connected to the tower walls.

Default, unrotated layout (X increases right, Z increases down):

| | X 0–47 | X 48–95 |
|---|---|---|
| Z 0–47 | Fallen Walls | Broken Arch |
| Z 48–95 | Sunken Court | Original crafting pavilion |

`build_site.py` reads the existing saved pavilion NBT, builds the three new tiles,
exports a complete review template, and creates separate assembly copies with
underground jigsaw connectors. The connectors turn into stone during natural
placement. Each tile shares the same terrain anchor and rotates with the site.
`render_site.py` produces the complete block-layout preview.
`swamp_ecology.py` supplies the shared scenery. `refresh_hub_ecology.py` updates
the saved hub's natural blocks while checking that its architecture is intact;
use `--source <saved.nbt>` to work from a particular saved revision.

## Placing the full site

After restarting, use a clear Creative area:

```mcfunction
/place template archecraft:abandoned_drill_camp ~ ~ ~
```

This places the bottom corner of all four sections at the command position.
Use `~ ~-6 ~` to embed the six-layer foundation at the surrounding surface.
The 96-block combined NBT is convenient for review; use the separate 48-block
section templates when saving artist edits through structure blocks.

Natural generation uses the renamed ID with the same rarity settings:

```mcfunction
/locate structure archecraft:abandoned_drill_camp
```

Natural generation starts only in the regular `minecraft:swamp` biome; mangrove
swamps and other biomes are excluded. Eligible locations assemble all four sections.
The 48-chunk candidate grid and 24-chunk separation are unchanged.

## Terrain-safe generation

`archecraft:hasla_swamp` remains the internal custom structure **type** used by
`archecraft:abandoned_drill_camp`. The old `archecraft:marsh_ruins` worldgen entry
has been removed, so only the new camp appears in `/locate`. Saved chunks using
the old name have their structure starts and references migrated before loading;
the lightweight locate scanner performs the same conversion. Loaded chunks are
marked for resaving under the new ID. Blocks and structure pieces are preserved,
including Sarracenia spawn bounds. The existing `marsh_ruins` template/pool
paths remain internal editing and assembly IDs. It retains the native jigsaw layout but
validates the assembled footprint before placing any blocks:

- Height/biome samples cover all four tiles and an eight-block border on an
  eight-block grid, including the far edges.
- Every sample must be in the allowed regular Swamp biome. Mountain/forest
  boundaries are rejected even when the original starting point is in a swamp.
- Sampled base terrain may vary by at most five blocks across the site/border.
  Trees are excluded by querying the generator's base terrain, not loaded chunks.
- The complete site moves to one shared height based on the lowest accepted
  terrain surface. Every sampled foundation column needs solid support within
  eight blocks below its base; deep water and large voids are rejected.
- During generation, short stone footings fill remaining air/water gaps under
  the foundation, stopping at solid ground. Writes are confined to the current
  chunk, so this does not force neighboring chunks to load.

Unsuitable candidate locations are skipped, so suitable sites are rarer. These
checks apply to natural generation and `/place structure archecraft:abandoned_drill_camp`.
`/place template archecraft:abandoned_drill_camp` remains a literal template paste at the
requested coordinates and intentionally bypasses terrain checks. Existing
generated copies are not relocated or repaired; test in fresh chunks/a new world.

## Editable sections

| Section | Template ID | Art file |
|---|---|---|
| Crafting pavilion | `archecraft:marsh_ruins` | `marsh_ruins.nbt` |
| Sunken Court | `archecraft:marsh_ruins/sunken_court` | `sections/sunken_court.nbt` |
| Broken Arch | `archecraft:marsh_ruins/broken_arch` | `sections/broken_arch.nbt` |
| Fallen Walls | `archecraft:marsh_ruins/fallen_walls` | `sections/fallen_walls.nbt` |

For example, `/place template archecraft:marsh_ruins/sunken_court ~ ~ ~` places
one habitat tile. The editable files have no assembly markers. Export edits
under the same ID, update both the art and mod-resource copies, then rebuild
the assembly copies. `build_site.py` preserves the saved pavilion but rebuilds
the three habitats from code, so save habitat edits before running it again.

## Original crafting section

A vanilla-terrain interpretation of the supplied marsh reference, with one custom Hasla Workbench: shallow ponds,
lily pads and reeds, hanging oak trees, broken stone columns, worn paths,
terraced ground and a timber crafting pavilion with a dark tiled roof and ruined
lookout. The pavilion has posts and beams without walls, doors or windows.
Spikes, palisades, training dummies, tents and entities are omitted.

The irregular puddles use waterlogged bottom mud-brick slabs for half-block-deep
footing, interspersed with grass islands and dry clearings for future mobs.

The editable Java 1.21.1 template is `marsh_ruins.nbt`, **48 x 36 x 48** blocks.
`build_structure.py` reproduces it without external Python dependencies.
`render_preview.py` draws block-layout previews from the cached vanilla textures;
these are previews, not in-game screenshots.

## Testing and editing

After restarting the mod, in a Creative world with cheats:

```mcfunction
/place template archecraft:marsh_ruins ~ ~ ~
```

This positions the bottom corner at the command position. It includes six
layers of terrain, so give it clear space; the build extends toward positive
X and Z. The entrance faces north. Place it above a superflat world for editing,
or use an offset six blocks below the surrounding surface to embed its ground.
To find a naturally generated site:

```mcfunction
/locate structure archecraft:abandoned_drill_camp
```

The terrain anchor places each template's local Y=5 water at normal water level.

Save artist edits using a structure block under `archecraft:marsh_ruins`.
The world exports `generated/archecraft/structures/marsh_ruins.nbt`; copy the
edited file to `src/main/resources/data/archecraft/structure/marsh_ruins.nbt`
and the adjacent art copy. Running the Python builder again replaces those edits.
`fix_pavilion.py` applies grounded tower and clear-floor changes while preserving
the Hasla station. `place_hasla_workbench.py` adds the station to a saved hub
without regenerating scenery. Run `build_site.py` afterward to refresh the natural
assembly pieces and combined review template. The scene requires ArcheCraft for
the station; all other terrain and architecture use vanilla blocks.

## Larger sites

The 48-block limit applies to the structure-block save interface, not the whole
generated site. Larger sites can connect multiple templates with jigsaw pieces;
for example, four 48 x 48 terrain tiles can form a 96 x 96 area. In Java 1.21.1,
the jigsaw structure has a separate maximum-distance setting (up to 128 blocks
from its center), so expansion also needs appropriate placement bounds and terrain
planning. The current revision uses four 48 x 48 templates for easy editing.
