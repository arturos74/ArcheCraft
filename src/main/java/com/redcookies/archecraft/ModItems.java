package com.redcookies.archecraft;

import com.redcookies.archecraft.ArcheCraft;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

public class ModItems {
    public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(ArcheCraft.MODID);

    public static final DeferredItem<BlockItem> EXAMPLE_BLOCK_ITEM =
            ITEMS.registerSimpleBlockItem("example_block", ModBlocks.EXAMPLE_BLOCK);

    public static final DeferredItem<Item> EXAMPLE_ITEM = ITEMS.registerSimpleItem("example_item",
            new Item.Properties().food(new FoodProperties.Builder().alwaysEdible().nutrition(1).saturationModifier(2f).build()));

    public static final DeferredItem<Item> RAW_ARCHEUM = ITEMS.registerSimpleItem("raw_archeum");
    public static final DeferredItem<Item> ARCHEUM_INGOT = ITEMS.registerSimpleItem("archeum_ingot");

    public static final DeferredItem<BlockItem> ARCHEUM_BLOCK_ITEM =
            ITEMS.registerSimpleBlockItem("archeum_block", ModBlocks.ARCHEUM_BLOCK);

    public static void register(IEventBus modEventBus) {
        ITEMS.register(modEventBus);
    }
}
