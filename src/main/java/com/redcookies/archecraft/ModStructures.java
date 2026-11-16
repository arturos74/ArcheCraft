package com.redcookies.archecraft;

import com.redcookies.archecraft.worldgen.HaslaSwampStructure;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModStructures {
    private static final DeferredRegister<StructureType<?>> TYPES =
            DeferredRegister.create(Registries.STRUCTURE_TYPE, ArcheCraft.MODID);
    public static final DeferredHolder<StructureType<?>, StructureType<HaslaSwampStructure>> HASLA_SWAMP =
            TYPES.register("hasla_swamp", () -> () -> HaslaSwampStructure.CODEC);

    private ModStructures() {}

    public static void register(IEventBus bus) {
        TYPES.register(bus);
    }
}
