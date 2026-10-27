# ArcheCraft

ArcheCraft is a Minecraft Java Edition mod inspired by ArcheAge, built with NeoForge for Minecraft 1.21.1.

This project is also a hands-on learning experience in Java and Minecraft mod development. Features will be developed incrementally, starting with basic items and blocks before moving into more complex gameplay systems.

## Planned features

- ArcheAge-inspired items and blocks
- Interactive blocks and gameplay systems
- Yatas and other creatures
- Functional gliders

These are project goals, not a list of currently implemented features. ArcheCraft is in early development.

## Development setup

Requirements:

- A 64-bit Java Development Kit (JDK) 21
- IntelliJ IDEA or another IDE with Gradle support

Clone the repository, open its root folder in IntelliJ IDEA, and allow the Gradle import to finish. Configure the project SDK and Gradle JVM to use JDK 21.

### Run the development client

From PowerShell in the project root:

```powershell
.\gradlew.bat runClient
```

### Build the mod

```powershell
.\gradlew.bat build
```

The built mod JAR is placed in `build/libs/`.

## Resources

- [NeoForge documentation for Minecraft 1.21.1](https://docs.neoforged.net/docs/1.21.1/)
- [NeoForge community Discord](https://discord.neoforged.net/)

## Minecraft mappings

This project uses Mojang's official mappings for Minecraft method and field names. See the [Mojang mappings license reference](https://github.com/NeoForged/NeoForm/blob/main/Mojang.md) for details.
