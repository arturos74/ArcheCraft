package com.redcookies.archecraft;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredRegister;

public class ModBlocks {
    public static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(ArcheCraft.MODID);

    public static final DeferredBlock<Block> EXAMPLE_BLOCK = BLOCKS.registerSimpleBlock("example_block",
            BlockBehaviour.Properties.of().mapColor(MapColor.STONE));

    public static final DeferredBlock<Block> ARCHEUM_BLOCK = BLOCKS.register("archeum_block",
            () -> new Block(BlockBehaviour.Properties.of().strength(3.0f, 3.0f).sound(SoundType.METAL)));

    // This method will be called from your main class
    public static void register(IEventBus modEventBus) {
        BLOCKS.register(modEventBus);
    }
}
