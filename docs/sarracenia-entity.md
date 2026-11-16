# Sarracenia

The mob is registered as `archecraft:sarracenia`. It uses the saved Blockbench
model and its idle/walk clips, including the swept-back tendrils and forked rear
stalk. There is no attack clip yet; melee damage already works.

- 20 health, 4 base melee damage, 24-block detection range.
- Movement speed attribute 0.18. Wandering and pursuit both use a 1.0 speed
  multiplier. There is no sprint, panic goal, or running animation.
- Targets survival/adventure players with vanilla line-of-sight and targeting
  rules; creative and spectator players are excluded. It can retaliate when hit.
- Floats when submerged and can step up one block. It does not burn in daylight.
- Actual horizontal movement blends from idle to walk over five ticks; stopping
  blends back to idle. Render resources are cached until a resource reload.

## Spawning and testing

Natural spawns come exclusively from the monster spawn override on the registered
`archecraft:abandoned_drill_camp` structure, in groups of one or two. A separate spawn
predicate also checks that the position lies inside an actual structure piece.
Nothing is added to biome spawn lists, so ordinary swamps cannot spawn this mob.
It can spawn during the day as well as at night, with normal ground/collision,
hostile mob cap, player-distance and difficulty rules. Peaceful rejects it.

The **Sarracenia Spawn Egg** is in the ArcheCraft creative tab. Eggs, commands
and configured mob spawners can create it outside the habitat for testing:

```mcfunction
/summon archecraft:sarracenia ~ ~ ~
/give @s archecraft:sarracenia_spawn_egg
/locate structure archecraft:abandoned_drill_camp
```

Natural spawning requires a registered structure start. A standalone NBT template
pasted with `/place template` has no structure spawn boundary. Existing registered
Hasla structures use the updated spawn rules after the mod is reloaded.

Restart Minecraft after adding the entity registration. In an existing world,
new structure generation still requires unexplored chunks; spawning within an
existing registered Hasla structure does not. Saved `marsh_ruins` structure starts
and references are migrated to `abandoned_drill_camp` during chunk loading and
locate scans, preserving their spawn boundaries. The old worldgen entry is
removed from the registry and command suggestions.

## Updating the artwork

Source: `art/models/sarracenia/sarracenia.bbmodel`.
Run `art/models/sarracenia/export_runtime.py` with Python (NumPy and Pillow)
after saving model, texture or animation edits. It updates the mesh, texture and
idle/walk resources under `src/main/resources/assets/archecraft/`, leaving the
Blockbench project untouched. Reload resources with F3+T during development.
`docs/sarracenia-runtime-model.json` records the exported source hash.

The initial loot table is empty; Hasla token drops can be added with the later
weapon progression work.

## Saved-world compatibility

The mob is now registered as `archecraft:sarracenia`, with the spawn egg
`archecraft:sarracenia_spawn_egg`. NeoForge registry aliases resolve the old
`archecraft:pitcher_plant` and `archecraft:pitcher_plant_spawn_egg` IDs to the
current entries. Existing saved mobs and eggs keep their data and save under
the new IDs. The aliases are not additional registered mobs or egg items.

