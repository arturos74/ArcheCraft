package com.redcookies.archecraft;

import com.redcookies.archecraft.workbench.WorkbenchBlockEntity;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModBlockEntities {
    public static final DeferredRegister<BlockEntityType<?>> BLOCK_ENTITIES =
            DeferredRegister.create(Registries.BLOCK_ENTITY_TYPE, ArcheCraft.MODID);
    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<WorkbenchBlockEntity>> WORKBENCH =
            BLOCK_ENTITIES.register("workbench", () -> BlockEntityType.Builder.of(
                    WorkbenchBlockEntity::new, ModBlocks.CARPENTER_WORKBENCH.get(), ModBlocks.ARCHEUM_WORKBENCH.get(),
                    ModBlocks.STONEMASON_WORKBENCH.get(), ModBlocks.ALCHEMY_WORKBENCH.get(), ModBlocks.SMELTER.get(),
                    ModBlocks.ANVIL.get()).build(null));

    public static void register(IEventBus bus) {
        BLOCK_ENTITIES.register(bus);
    }
}
