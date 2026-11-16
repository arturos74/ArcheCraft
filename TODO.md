# ArcheCraft todo list

## Dungeon foundations

- [ ] Create a dedicated dimension for each dungeon type.
- [ ] Add Overworld dungeon entrances with portals that send players to the appropriate dungeon or assigned instance.
- [ ] Return players to their entrance when they leave a dungeon.
- [ ] Disable block breaking, block placement, and terrain destruction inside dungeon dimensions while allowing combat and intended doors, switches, portals, and reward interactions.
- [ ] Save dungeon membership, progress, return locations, and relevant timers across server restarts.
- [ ] Handle deaths, disconnects, rejoining, and abandoned runs safely.
- [ ] Manage chunk loading around active dungeon areas and release unneeded instance regions.

## Greater Howling Abyss

Private, resettable dungeon runs in `archecraft:greater_howling_abyss`.

- [ ] Build the GHA dungeon layout, encounters, boss, and completion reward.
- [ ] Support multiple simultaneous parties by assigning each party an isolated dungeon copy within the GHA dimension.
- [ ] Keep each run's players, enemies, progression, and rewards separate.
- [ ] Prevent players from entering another party's copy or escaping its boundaries.
- [ ] Unlock progression through encounters and grant completion rewards once per successful run.
- [ ] Reset and reuse a completed or abandoned copy without affecting other active runs.
- [ ] Start with one portal, one dungeon layout, one boss, and one completion reward before expanding the system.

## Ayanad Library

One shared, persistent dungeon in `archecraft:ayanad_library`, open to all players.

- [ ] Build one Library location, including its floors, exploration areas, farming areas, and special boss locations.
- [ ] Send all entrances and visiting players into the same shared Library.
- [ ] Preserve the Library's layout and shared world state across visits and server restarts; no whole-dungeon resets.
- [ ] Respawn ordinary mobs for ongoing farming.
- [ ] Add special bosses with configurable respawn timers and boss loot.

## Dungeon validation

- [ ] Verify separate parties can run GHA concurrently without sharing enemies, rewards, or resets.
- [ ] Verify everyone sees the same persistent Library and its shared enemies and bosses.
- [ ] Verify dungeon protection, portal returns, reconnect/restart recovery, and reward duplication prevention.


## White Arden Forest Biome

A New White Forest Biome based off White Arden

- [ ] Add New Aspen Tree Blocks
- [ ] Create new tree builds using aspen blocks that will generate
- [ ] Add Special Music that plays inside biome
- [ ] Add Terrain Generation
- [ ] Add Special Mobs that spawn in the forest

## Windscour Savannah Biome

A new savannah biome that contains giant Baobab trees and some special creatures

- [ ] New Baobab Log, Planks, Leaves
- [ ] Giant Baobab Trees
- [ ] Animals that spawn here
  - [ ] Yata
  - [ ] Snowlion
  - [ ] Elephants
- [ ] Firran Outposts Spawn here
- [ ] Plants that spawn here
  - [ ] Aloe
  - [ ] Mint
  - [ ] Saffron
  - [ ] Wheat
- [ ] Mobs that spawn here
  - [ ] Sandworms
  - [ ] Giant Ants
  - [ ] Gorillas
  - [ ] Shadow Invasion Monsters
  - [ ] Goretusk - Open World Boss

## Custom Structures

These are structures that will generate around the world for the player to find (Dungeons not included here)

- [ ] Abandoned Drill Camp
- [ ] Firran Outpost
- [ ] 

## Custom Music

There are 3 new types of music, Exploration music, Queued Music, Music Discs

- [ ] Exploration music that will queue randomly similar to how minecraft's music plays
- [ ] Queued music will play whenever the user enters an archecraft biome or structure, this will play a specific song based on the biome/structure the user enters
- [ ] Music discs will contain most if not all the archeage music for the user to listen to

## Weapons/Models

- [ ] Add Illustrious, Magnificient, Epherium, Delphinad, and Ayanad Weapons/Models
- [ ] Add T1-T7 Obsidian Weapons/Models
- [ ] Add Faded, Brilliant, Eternal Hasla Weapons/Models
- [ ] Consider disabling vanilla weapons to encourage ArcheCraft weapon progression. Tentative idea only; do not implement yet.
- [ ] As part of the deferred vanilla weapon restrictions, reduce vanilla axe combat damage so axes serve as tools, preserving their harvesting speed, block stripping, and other tool functions. Choose the damage values when implementing; do not change gameplay yet.
- [ ] Before implementing vanilla weapon restrictions, establish ArcheCraft starter weapons and the upgrade path, and decide how weapons from crafting, loot, trades, and mob drops should be handled.


## Mounts

Mounts that the user will be able to tame and ride

- [X] Yata Mount/Variants
- [ ] Elk Mount / Gallant
- [ ] Boar Mount / Gallant
- [ ] Snowlion / Gallant
- [ ] Leomorph / Gallant
- [ ] Pangolin / Gallant
- [ ] Stormdarter / Thunderdash