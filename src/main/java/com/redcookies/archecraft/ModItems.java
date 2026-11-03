package com.redcookies.archecraft;

import com.redcookies.archecraft.ArcheCraft;
import net.minecraft.client.renderer.item.ItemProperties;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemNameBlockItem;
import net.minecraft.world.item.JukeboxSong;
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

    public static final DeferredItem<BlockItem> ARCHEUM_ORE =
            ITEMS.registerSimpleBlockItem("archeum_ore", ModBlocks.ARCHEUM_ORE);

    public static final DeferredItem<BlockItem> ARCHEUM_BLOCK_ITEM =
            ITEMS.registerSimpleBlockItem("archeum_block", ModBlocks.ARCHEUM_BLOCK);

    public static final DeferredItem<Item> YATA_MEAT = ITEMS.registerSimpleItem("yata_meat",
            new Item.Properties().food(new FoodProperties.Builder().nutrition(1).saturationModifier(2f).build()));

    public static final DeferredItem<Item> COOKED_YATA_MEAT = ITEMS.registerSimpleItem("cooked_yata_meat",
            new Item.Properties().food(new FoodProperties.Builder().nutrition(5).saturationModifier(5f).build()));

    public static final DeferredItem<Item> YATA_FUR = ITEMS.registerSimpleItem("yata_fur");

    public static final DeferredItem<Item> YATA_FERTILIZER = ITEMS.registerSimpleItem("yata_fertilizer");

    public static final DeferredItem<BlockItem> YATA_FERTILIZER_BLOCK_ITEM =
            ITEMS.registerSimpleBlockItem("yata_fertilizer_block", ModBlocks.YATA_FERTILIZER_BLOCK);

    public static final DeferredItem<Item> GOAT_WOOL = ITEMS.registerSimpleItem("goat_wool");

    public static final DeferredItem<Item> HANDICRAFT_YARN = ITEMS.registerSimpleItem("handicraft_yarn");

    public static final DeferredItem<Item> BEAR_FUR = ITEMS.registerSimpleItem("bear_fur");

    public static final DeferredItem<Item> COMBINED_FEED = ITEMS.registerSimpleItem("combined_feed");

    public static final DeferredItem<Item> CLOVER_SEEDS = ITEMS.registerItem("clover_seeds",
            props -> new ItemNameBlockItem(ModBlocks.CLOVER_CROP.get(), props));

    public static final DeferredItem<Item> CLOVER = ITEMS.registerSimpleItem("clover");

    public static final ResourceKey<JukeboxSong> ARCHEAGE_THEME =
            ResourceKey.create(
                    Registries.JUKEBOX_SONG,
                    ResourceLocation.fromNamespaceAndPath(
                            ArcheCraft.MODID, "archeage_theme"
                    )
            );

    public static final DeferredItem<Item> AC_DISC_1 =
            ITEMS.registerSimpleItem(
                    "ac_disc_1",
                    new Item.Properties()
                            .stacksTo(1)
                            .jukeboxPlayable(ARCHEAGE_THEME)
            );


    public static final ResourceKey<JukeboxSong> SOLZREED_THEME =
            ResourceKey.create(
                    Registries.JUKEBOX_SONG,
                    ResourceLocation.fromNamespaceAndPath(
                            ArcheCraft.MODID, "solzreed_theme"
                    )
            );

    public static final DeferredItem<Item> AC_DISC_2 =
            ITEMS.registerSimpleItem(
                    "ac_disc_2",
                    new Item.Properties()
                            .stacksTo(1)
                            .jukeboxPlayable(SOLZREED_THEME)
            );

    public static final ResourceKey<JukeboxSong> HOUSING_ZONE_THEME_1 =
            ResourceKey.create(
                    Registries.JUKEBOX_SONG,
                    ResourceLocation.fromNamespaceAndPath(
                            ArcheCraft.MODID, "housing_zone_theme_1"
                    )
            );

    public static final DeferredItem<Item> AC_DISC_3 =
            ITEMS.registerSimpleItem(
                    "ac_disc_3",
                    new Item.Properties()
                            .stacksTo(1)
                            .jukeboxPlayable(HOUSING_ZONE_THEME_1)
            );


    public static void register(IEventBus modEventBus) {
        ITEMS.register(modEventBus);
    }
}
