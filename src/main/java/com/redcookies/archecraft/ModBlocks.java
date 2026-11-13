package com.redcookies.archecraft;
import com.redcookies.archecraft.ModCustom.StarshardVeinBlock;
import com.redcookies.archecraft.workbench.WorkbenchBlock;
import com.redcookies.archecraft.workbench.CarpenterWorkbenchBlock;
import com.redcookies.archecraft.workbench.ArcheumWorkbenchBlock;
import com.redcookies.archecraft.workbench.StonemasonWorkbenchBlock;
import com.redcookies.archecraft.workbench.AlchemyWorkbenchBlock;
import com.redcookies.archecraft.workbench.SmelterBlock;
import com.redcookies.archecraft.workbench.AnvilWorkbenchBlock;
import net.minecraft.world.level.material.PushReaction;
import net.minecraft.world.level.ItemLike;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.CropBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredRegister;

public class ModBlocks {
    public static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(ArcheCraft.MODID);

    public static final DeferredBlock<AnvilWorkbenchBlock> ANVIL = BLOCKS.register("anvil",
            () -> new AnvilWorkbenchBlock(BlockBehaviour.Properties.of()
                    .mapColor(MapColor.METAL).strength(3.5F, 3.5F).sound(SoundType.ANVIL)
                    .requiresCorrectToolForDrops().noOcclusion().pushReaction(PushReaction.BLOCK)));

    public static final DeferredBlock<SmelterBlock> SMELTER = BLOCKS.register("smelter",
            () -> new SmelterBlock(BlockBehaviour.Properties.of().mapColor(MapColor.STONE)
                    .strength(3.5F,3.5F).sound(SoundType.STONE).requiresCorrectToolForDrops()
                    .noOcclusion().pushReaction(PushReaction.BLOCK)));

    public static final DeferredBlock<CarpenterWorkbenchBlock> CARPENTER_WORKBENCH = BLOCKS.register("carpenter_workbench",
            () -> new CarpenterWorkbenchBlock(BlockBehaviour.Properties.ofFullCopy(Blocks.CRAFTING_TABLE)
                    .noOcclusion().pushReaction(PushReaction.BLOCK)));

    public static final DeferredBlock<ArcheumWorkbenchBlock> ARCHEUM_WORKBENCH = BLOCKS.register("archeum_workbench",
            () -> new ArcheumWorkbenchBlock(BlockBehaviour.Properties.ofFullCopy(Blocks.CRAFTING_TABLE)
                    .noOcclusion().pushReaction(PushReaction.BLOCK)));

    public static final DeferredBlock<AlchemyWorkbenchBlock> ALCHEMY_WORKBENCH = BLOCKS.register("alchemy_workbench",
            () -> new AlchemyWorkbenchBlock(BlockBehaviour.Properties.ofFullCopy(Blocks.CRAFTING_TABLE)
                    .noOcclusion().pushReaction(PushReaction.BLOCK)));

    public static final DeferredBlock<StonemasonWorkbenchBlock> STONEMASON_WORKBENCH = BLOCKS.register("stonemason_workbench",
            () -> new StonemasonWorkbenchBlock(BlockBehaviour.Properties.of()
                    .mapColor(MapColor.STONE).strength(3.0F, 3.0F).sound(SoundType.STONE)
                    .requiresCorrectToolForDrops().noOcclusion().pushReaction(PushReaction.BLOCK)));

    public static final DeferredBlock<StarshardVeinBlock> STARSHARD_VEIN = BLOCKS.register("starshard_vein",
            () -> new StarshardVeinBlock(BlockBehaviour.Properties.of()
                    .mapColor(MapColor.STONE).strength(3.0F, 3.0F)
                    .requiresCorrectToolForDrops().sound(SoundType.STONE)
                    .lightLevel(state -> 3).noOcclusion()));

    public static final DeferredBlock<Block> EXAMPLE_BLOCK = BLOCKS.registerSimpleBlock("example_block",
            BlockBehaviour.Properties.of().mapColor(MapColor.STONE));

    public static final DeferredBlock<Block> ARCHEUM_BLOCK = BLOCKS.register("archeum_block",
            () -> new Block(BlockBehaviour.Properties.of().strength(3.0f, 3.0f).sound(SoundType.METAL)));

    public static final DeferredBlock<Block> ARCHEUM_ORE = BLOCKS.registerSimpleBlock("archeum_ore",
            BlockBehaviour.Properties.of()
                    .strength(3.0F, 3.0F)
                    .requiresCorrectToolForDrops()
                    .sound(SoundType.STONE)
                    .lightLevel(state -> 1)
    );

    public static final DeferredBlock<Block> CLOVER_CROP = BLOCKS.register("clover_crop",
            properties -> new CropBlock(BlockBehaviour.Properties.ofFullCopy(Blocks.WHEAT)));


    public static final DeferredBlock<Block> YATA_FERTILIZER_BLOCK = BLOCKS.registerSimpleBlock("yata_fertilizer_block",
            BlockBehaviour.Properties.of().sound(SoundType.MUD));

    // This method will be called from your main class
    public static void register(IEventBus modEventBus) {
        BLOCKS.register(modEventBus);
    }
}
