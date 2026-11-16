# Abandoned Drill Camp structure rename

The only registered camp worldgen ID is `archecraft:abandoned_drill_camp`.
The previous `archecraft:marsh_ruins` worldgen entry and biome tag were removed.
Its editable structure templates and jigsaw pool paths remain internal assets;
template IDs are separate from `/locate structure` IDs.

To preserve existing saves without retaining an autocomplete alias:

- `DrillCampSaveMigration` renames old chunk structure-start keys and start IDs,
  and moves structure-reference arrays to the current name.
- `ChunkSerializerMixin` runs migration before chunk structure registry lookup
  and marks changed chunks for resaving. It does not change blocks or entities.
- `StructureCheckMixin` applies the same conversion to partial metadata scans,
  so `/locate` can recognize old camps before their full chunks have loaded.
- If both names already have valid starts in one chunk, distinct pieces are
  retained and reference arrays are merged without duplicate chunk positions.
  Repeated migration is a no-op; unrelated structure data is unchanged.

Restart Minecraft/the server when updating, because the migration hooks and
registry changes are loaded during startup.

Validation includes actual command autocomplete, native chunk loading/resaving,
the lightweight locate scanner, preservation of edited blocks, metadata merge
and idempotence, existing camp mob spawns, and the complete gameplay suite.
