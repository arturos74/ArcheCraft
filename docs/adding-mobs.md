# Adding a mob to ArcheCraft

This guide matches this project's **Minecraft 1.21.1 / NeoForge 21.1.265** setup.
It uses **Rafflesia** as the example and copies the existing **Sarracenia**.
The steps below are instructions: Rafflesia has not been registered by this guide.

I can prepare the model, texture, animation and rendering exports. You can then
choose the stats, behavior, drops and spawn locations. A `.bbmodel` is the editable
art project; Java code connects that art to a Minecraft mob.

## 1. Pick the name

Use these three forms consistently:

| Purpose | Rafflesia example |
| --- | --- |
| Java class prefix | `Rafflesia` |
| Registry/resource name | `rafflesia` |
| Java registration constant | `RAFFLESIA` |

Its in-game ID will be `archecraft:rafflesia`.

## 2. Prepare the rendering files

The current model is [rafflesia.bbmodel](G:/ArcheCraft/art/models/rafflesia/rafflesia.bbmodel).
Our mobs use a custom Java renderer that reads exported JSON files. Exporting
Bedrock `.geo.json` from Blockbench alone does not connect it to that renderer.

For the current Rafflesia, copy
[the Sarracenia exporter](G:/ArcheCraft/art/models/sarracenia/export_runtime.py)
to `G:\ArcheCraft\art\models\rafflesia\export_runtime.py`.
In **that new copy only**, replace:

| Find | Replace |
| --- | --- |
| `sarracenia` | `rafflesia` |

This also updates the export manifest filename so Sarracenia's manifest stays
separate. Run it from PowerShell using the Python environment already
available on this computer:

```powershell
& 'C:\Users\redtr\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'G:\ArcheCraft\art\models\rafflesia\export_runtime.py'
```

This creates these game assets under `G:\ArcheCraft\src\main\resources\assets\archecraft`:

```text
entity/rafflesia_mesh.json
entity/rafflesia_idle.json
entity/rafflesia_walk.json
textures/entity/rafflesia.png
```

Rafflesia's idle/walk clips are currently empty, so it will use its saved pose
until animations are added. This is fine for the first spawn test. Re-export
after saving model or animation edits; then rebuild/relaunch the game.

## 3. Copy the three Java files

Make copies beside the originals:

| Existing file | New filename in the same folder |
| --- | --- |
| [SarraceniaEntity.java](G:/ArcheCraft/src/main/java/com/redcookies/archecraft/entity/SarraceniaEntity.java) | `RafflesiaEntity.java` |
| [SarraceniaModel.java](G:/ArcheCraft/src/main/java/com/redcookies/archecraft/client/SarraceniaModel.java) | `RafflesiaModel.java` |
| [SarraceniaRenderer.java](G:/ArcheCraft/src/main/java/com/redcookies/archecraft/client/SarraceniaRenderer.java) | `RafflesiaRenderer.java` |

In **only those three new files**, replace `Sarracenia` with `Rafflesia`, and
`sarracenia` with `rafflesia`. This updates class names, constructors, imports
and resource paths. Keep the package lines because the copies stay in the same folders.

The copied entity already walks, wanders, attacks players, retaliates and floats
in water. Start with this behavior before changing the AI. Its movement-blend
methods are used by the copied model, so keep those methods too.

Inside `RafflesiaEntity.createAttributes()`, change these values as desired:

| Attribute | Meaning | Example |
| --- | --- | --- |
| `MAX_HEALTH` | Total health; 20 points = 10 hearts | `20.0` |
| `MOVEMENT_SPEED` | How quickly it moves | `.18` |
| `ATTACK_DAMAGE` | Base melee damage before armor | `4.0` |
| `FOLLOW_RANGE` | How far away it can acquire a target | `24.0` |

The copied natural-spawn check restricts it to **Abandoned Drill Camp**, just
like the Sarracenia. It does not add the mob to the camp's spawn list by itself.

## 4. Register the mob and its attributes

Open [ModEntities.java](G:/ArcheCraft/src/main/java/com/redcookies/archecraft/ModEntities.java).
Add this import with the other entity imports:

```java
import com.redcookies.archecraft.entity.RafflesiaEntity;
```

Add this field beside `SARRACENIA`, inside the class:

```java
public static final DeferredHolder<EntityType<?>, EntityType<RafflesiaEntity>> RAFFLESIA =
        ENTITY_TYPES.register("rafflesia", () -> EntityType.Builder.of(RafflesiaEntity::new, MobCategory.MONSTER)
                .sized(1.4F, 2.2F)
                .eyeHeight(1.85F)
                .clientTrackingRange(10)
                .build(ArcheCraft.MODID + ":rafflesia"));
```

`.sized(width, height)` sets the collision box in blocks; it does not resize the
art. The numbers above are a starting point for the current model.

Inside the existing `createAttributes` method, add:

```java
event.put(RAFFLESIA.get(), RafflesiaEntity.createAttributes().build());
```

Inside the existing `registerSpawnPlacements` method, add:

```java
event.register(RAFFLESIA.get(), SpawnPlacementTypes.ON_GROUND,
        Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
        RafflesiaEntity::checkSpawnRules, RegisterSpawnPlacementsEvent.Operation.REPLACE);
```

Keep the existing Yata and Sarracenia entries.

## 5. Connect the renderer

Open [ArcheCraftClient.java](G:/ArcheCraft/src/main/java/com/redcookies/archecraft/ArcheCraftClient.java).
Add the import:

```java
import com.redcookies.archecraft.client.RafflesiaRenderer;
```

Inside `registerEntityRenderers`, add:

```java
event.registerEntityRenderer(ModEntities.RAFFLESIA.get(), RafflesiaRenderer::new);
```

Keep renderer code in the client classes, following the existing arrangement.

## 6. Add the spawn egg, names and drops

In [ModItems.java](G:/ArcheCraft/src/main/java/com/redcookies/archecraft/ModItems.java),
add this field beside the other spawn eggs:

```java
public static final DeferredItem<DeferredSpawnEggItem> RAFFLESIA_SPAWN_EGG =
        ITEMS.register("rafflesia_spawn_egg", () -> new DeferredSpawnEggItem(
                ModEntities.RAFFLESIA, 0x64327D, 0xA08043, new Item.Properties()));
```

The two hexadecimal numbers are the egg's background and spot colors.

In [ModCreativeTabs.java](G:/ArcheCraft/src/main/java/com/redcookies/archecraft/ModCreativeTabs.java),
add this inside the existing `displayItems` callback, beside the other eggs:

```java
output.accept(ModItems.RAFFLESIA_SPAWN_EGG);
```

Create `G:\ArcheCraft\src\main\resources\assets\archecraft\models\item\rafflesia_spawn_egg.json`:

```json
{ "parent": "minecraft:item/template_spawn_egg" }
```

Add these entries **inside** the existing object in
[en_us.json](G:/ArcheCraft/src/main/resources/assets/archecraft/lang/en_us.json),
using commas between entries:

```json
"entity.archecraft.rafflesia": "Rafflesia",
"item.archecraft.rafflesia_spawn_egg": "Rafflesia Spawn Egg"
```

For no drops yet, create
`G:\ArcheCraft\src\main\resources\data\archecraft\loot_table\entities\rafflesia.json`:

```json
{ "type": "minecraft:entity", "pools": [] }
```

## 7. Build and test before adding natural spawns

Save the files and run these commands in PowerShell:

```powershell
Set-Location 'G:\ArcheCraft'
.\gradlew.bat --offline build
.\gradlew.bat --offline runClient
```

In a test world with commands enabled:

```mcfunction
/difficulty normal
/summon archecraft:rafflesia ~ ~ ~
/give @s archecraft:rafflesia_spawn_egg
```

Check the model, texture, collision size and egg. Switch to Survival to check
hostile behavior; hostile mobs do not target Creative players normally.

## 8. Add it to the camp when the spawn test works

Open [abandoned_drill_camp.json](G:/ArcheCraft/src/main/resources/data/archecraft/worldgen/structure/abandoned_drill_camp.json).
Add this object to `spawn_overrides.monster.spawns`, keeping the Sarracenia
entry and putting a comma between the two objects:

```json
{ "type": "archecraft:rafflesia", "weight": 100, "minCount": 1, "maxCount": 2 }
```

Weight is relative to the other entries, rather than a percentage. Keeping both
at 100 gives them equal selection weight. The copied spawn predicate still
restricts natural spawning to this structure. Natural spawning also depends on
space, player distance, mob caps and the normal spawning checks.

## Common problems

| Symptom | First thing to check |
| --- | --- |
| Unknown entity in `/summon` | Registration in `ModEntities`, spelling, then rebuild/restart |
| Crash mentioning missing attributes | `event.put(RAFFLESIA.get(), ...)` in `createAttributes` |
| No model or crash loading the renderer | Client renderer registration and all three exported JSON paths |
| Purple/black texture | Texture path in `RafflesiaRenderer` and exported PNG |
| Moves but stays in one pose | Current clips are empty; author animation and re-export |
| Old appearance after an edit | Re-export the saved `.bbmodel`, rebuild resources and relaunch |
| Summons but never appears naturally | Spawn-list entry **and** spawn predicate, plus normal spawning conditions |

The existing Sarracenia files are the version-matched templates for this guide.
NeoForge's [entity overview](https://docs.neoforged.net/docs/1.21.4/entities/)
also explains the entity type, entity class and renderer roles; its examples
target a newer version, so use this repository's code for the exact API syntax.
