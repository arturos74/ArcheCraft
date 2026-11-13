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

    // <editor-fold desc="Items">
    public static final DeferredItem<Item> RAW_ARCHEUM = ITEMS.registerSimpleItem("raw_archeum");

    public static final DeferredItem<Item> ARCHEUM_INGOT = ITEMS.registerSimpleItem("archeum_ingot");

    public static final DeferredItem<BlockItem> ARCHEUM_ORE =
            ITEMS.registerSimpleBlockItem("archeum_ore", ModBlocks.ARCHEUM_ORE);

    public static final DeferredItem<Item> YATA_MEAT = ITEMS.registerSimpleItem("yata_meat",
            new Item.Properties().food(new FoodProperties.Builder().nutrition(1).saturationModifier(2f).build()));

    public static final DeferredItem<Item> COOKED_YATA_MEAT = ITEMS.registerSimpleItem("cooked_yata_meat",
            new Item.Properties().food(new FoodProperties.Builder().nutrition(5).saturationModifier(5f).build()));

    public static final DeferredItem<Item> YATA_FUR = ITEMS.registerSimpleItem("yata_fur");

    public static final DeferredItem<Item> YATA_FERTILIZER = ITEMS.registerSimpleItem("yata_fertilizer");

    public static final DeferredItem<Item> GOAT_WOOL = ITEMS.registerSimpleItem("goat_wool");

    public static final DeferredItem<Item> HANDICRAFT_YARN = ITEMS.registerSimpleItem("handicraft_yarn");

    public static final DeferredItem<Item> BEAR_FUR = ITEMS.registerSimpleItem("bear_fur");

    public static final DeferredItem<Item> COMBINED_FEED = ITEMS.registerSimpleItem("combined_feed");

    public static final DeferredItem<Item> CLOVER_SEEDS = ITEMS.registerItem("clover_seeds",
            props -> new ItemNameBlockItem(ModBlocks.CLOVER_CROP.get(), props));

    public static final DeferredItem<Item> CLOVER = ITEMS.registerSimpleItem("clover");

    public static final DeferredItem<Item> SUNLIGHT_ARCHEUM_MOTES = ITEMS.registerSimpleItem("sunlight_archeum_motes");

    public static final DeferredItem<Item> SUNLIGHT_ARCHEUM_DUST = ITEMS.registerSimpleItem("sunlight_archeum_dust");

    public static final DeferredItem<Item> SUNLIGHT_ARCHEUM_SHARD = ITEMS.registerSimpleItem("sunlight_archeum_shard");

    public static final DeferredItem<Item> SUNLIGHT_ARCHEUM_CRYSTAL = ITEMS.registerSimpleItem("sunlight_archeum_crystal");

    public static final DeferredItem<Item> SUNLIGHT_ARCHEUM_ESSENCE = ITEMS.registerSimpleItem("sunlight_archeum_essence");

    public static final DeferredItem<Item> MOONLIGHT_ARCHEUM_MOTES = ITEMS.registerSimpleItem("moonlight_archeum_motes");

    public static final DeferredItem<Item> MOONLIGHT_ARCHEUM_DUST = ITEMS.registerSimpleItem("moonlight_archeum_dust");

    public static final DeferredItem<Item> MOONLIGHT_ARCHEUM_SHARD = ITEMS.registerSimpleItem("moonlight_archeum_shard");

    public static final DeferredItem<Item> MOONLIGHT_ARCHEUM_CRYSTAL =  ITEMS.registerSimpleItem("moonlight_archeum_crystal");

    public static final DeferredItem<Item> MOONLIGHT_ARCHEUM_ESSENCE =  ITEMS.registerSimpleItem("moonlight_archeum_essence");

    public static final DeferredItem<Item> STARLIGHT_ARCHEUM_MOTES = ITEMS.registerSimpleItem("starlight_archeum_motes");

    public static final DeferredItem<Item> STARLIGHT_ARCHEUM_DUST = ITEMS.registerSimpleItem("starlight_archeum_dust");

    public static final DeferredItem<Item> STARLIGHT_ARCHEUM_SHARD = ITEMS.registerSimpleItem("starlight_archeum_shard");

    public static final DeferredItem<Item> STARLIGHT_ARCHEUM_CRYSTAL =  ITEMS.registerSimpleItem("starlight_archeum_crystal");

    public static final DeferredItem<Item> STARLIGHT_ARCHEUM_ESSENCE =  ITEMS.registerSimpleItem("starlight_archeum_essence");

    public static final DeferredItem<Item> HASLA_TOKEN_COURAGE = ITEMS.registerSimpleItem("hasla_token_courage");
    public static final DeferredItem<Item> HASLA_TOKEN_LOYALTY = ITEMS.registerSimpleItem("hasla_token_loyalty");
    public static final DeferredItem<Item> HASLA_TOKEN_CONVICTION = ITEMS.registerSimpleItem("hasla_token_conviction");
    public static final DeferredItem<Item> HASLA_TOKEN_FORTITUDE = ITEMS.registerSimpleItem("hasla_token_fortitude");
    public static final DeferredItem<Item> HASLA_TOKEN_HONOR = ITEMS.registerSimpleItem("hasla_token_honor");
    public static final DeferredItem<Item> HASLA_TOKEN_SACRIFICE = ITEMS.registerSimpleItem("hasla_token_sacrifice");
    public static final DeferredItem<Item> HASLA_TOKEN_COMPASSION = ITEMS.registerSimpleItem("hasla_token_compassion");

    public static final DeferredItem<Item> RUMBLING_ARCHEUM_TREE_SAPLING = ITEMS.registerSimpleItem("rumbling_archeum_tree_sapling");

    public static final DeferredItem<Item> GILDA_STAR = ITEMS.registerSimpleItem("gilda_star");
    public static final DeferredItem<Item> BLUE_SALT_BOND = ITEMS.registerSimpleItem("blue_salt_bond");

    // Wood (Carpentry)
    public static final DeferredItem<Item> LUMBER = ITEMS.registerSimpleItem("lumber");
    public static final DeferredItem<Item> FINE_LUMBER = ITEMS.registerSimpleItem("fine_lumber");
    public static final DeferredItem<Item> NURI_FOREST_LUMBER = ITEMS.registerSimpleItem("nuri_forest_lumber");
    public static final DeferredItem<Item> BLAZING_NURI_FOREST_LUMBER = ITEMS.registerSimpleItem("blazing_nuri_forest_lumber");

    // Metal (Metalwork)
    public static final DeferredItem<Item> SUNRIDGE_INGOT = ITEMS.registerSimpleItem("sunridge_ingot");
    public static final DeferredItem<Item> BLAZING_SUNRIDGE_INGOT = ITEMS.registerSimpleItem("blazing_sunridge_ingot");
    public static final DeferredItem<Item> SILVER_ORE = ITEMS.registerSimpleItem("silver_ore");
    public static final DeferredItem<Item> SILVER_INGOT = ITEMS.registerSimpleItem("silver_ingot");
    public static final DeferredItem<Item> STARSHARD_CHIP = ITEMS.registerSimpleItem("starshard_chip");
    public static final DeferredItem<Item> STARSHARD_INGOT = ITEMS.registerSimpleItem("starshard_ingot");

    // Leather (Leatherwork)
    public static final DeferredItem<Item> PELT = ITEMS.registerSimpleItem("pelt");
    public static final DeferredItem<Item> LEATHER = ITEMS.registerSimpleItem("leather");
    public static final DeferredItem<Item> FINE_LEATHER = ITEMS.registerSimpleItem("fine_leather");
    public static final DeferredItem<Item> WIND_SPIRIT_LEATHER = ITEMS.registerSimpleItem("wind_spirit_leather");
    public static final DeferredItem<Item> BLAZING_WIND_SPIRIT_LEATHER = ITEMS.registerSimpleItem("blazing_wind_spirit_leather");

    // Cloth (Tailoring)
    public static final DeferredItem<Item> COTTON = ITEMS.registerSimpleItem("cotton");
    public static final DeferredItem<Item> FABRIC = ITEMS.registerSimpleItem("fabric");
    public static final DeferredItem<Item> BEAUTIFULLY_COLORED_FABRIC = ITEMS.registerSimpleItem("beautifully_colored_fabric");
    public static final DeferredItem<Item> CLOUDSPUN_FABRIC = ITEMS.registerSimpleItem("cloudspun_fabric");
    public static final DeferredItem<Item> BLAZING_CLOUDSPUN_FABRIC = ITEMS.registerSimpleItem("blazing_cloudspun_fabric");

    // Stone (Masonry)
    public static final DeferredItem<Item> HEREAFTER_STONE = ITEMS.registerSimpleItem("hereafter_stone");
    public static final DeferredItem<Item> STURDY_STONE = ITEMS.registerSimpleItem("sturdy_stone");
    public static final DeferredItem<Item> RISING_STAR_STONE = ITEMS.registerSimpleItem("rising_star_stone");

    // Gems & Special Catalysts
    public static final DeferredItem<Item> RUBY = ITEMS.registerSimpleItem("ruby");
    public static final DeferredItem<Item> SAPPHIRE = ITEMS.registerSimpleItem("sapphire");
    public static final DeferredItem<Item> TOPAZ = ITEMS.registerSimpleItem("topaz");
    public static final DeferredItem<Item> MYSTERIOUS_GARDEN_POWDER = ITEMS.registerSimpleItem("mysterious_garden_powder");
    public static final DeferredItem<Item> BLUE_SALT_WEDGE = ITEMS.registerSimpleItem("blue_salt_wedge");

    // Alchemy Oils
    public static final DeferredItem<Item> SMALL_SEED_OIL = ITEMS.registerSimpleItem("small_seed_oil");
    public static final DeferredItem<Item> VISCOUS_GLOSSY_OIL = ITEMS.registerSimpleItem("viscous_glossy_oil");
    public static final DeferredItem<Item> EMULSIFIED_OIL = ITEMS.registerSimpleItem("emulsified_oil");
    public static final DeferredItem<Item> DEEPLY_COLORED_OIL = ITEMS.registerSimpleItem("deeply_colored_oil");

    // Alchemy Polishes
    public static final DeferredItem<Item> OPAQUE_POLISH = ITEMS.registerSimpleItem("opaque_polish");
    public static final DeferredItem<Item> ROUGH_POLISH = ITEMS.registerSimpleItem("rough_polish");
    public static final DeferredItem<Item> NON_STICK_POLISH = ITEMS.registerSimpleItem("non_stick_polish");
    public static final DeferredItem<Item> RAINBOW_POLISH = ITEMS.registerSimpleItem("rainbow_polish");

    // Alchemy Pigments
    public static final DeferredItem<Item> SMALL_ROOT_PIGMENT = ITEMS.registerSimpleItem("small_root_pigment");
    public static final DeferredItem<Item> SMALL_LEAF_PIGMENT = ITEMS.registerSimpleItem("small_leaf_pigment");
    public static final DeferredItem<Item> SOFT_STEM_PIGMENT = ITEMS.registerSimpleItem("soft_stem_pigment");
    public static final DeferredItem<Item> SCENTED_PETAL_PIGMENT = ITEMS.registerSimpleItem("scented_petal_pigment");

    // Trade Run Stabilizers
    public static final DeferredItem<Item> CHARCOAL_STABILIZER = ITEMS.registerSimpleItem("charcoal_stabilizer");
    public static final DeferredItem<Item> ROCK_SALT_STABILIZER = ITEMS.registerSimpleItem("rock_salt_stabilizer");
    public static final DeferredItem<Item> CRYSTAL_STABILIZER = ITEMS.registerSimpleItem("crystal_stabilizer");
    public static final DeferredItem<Item> DRAGON_ESSENCE_STABILIZER = ITEMS.registerSimpleItem("dragon_essence_stabilizer");

    // </editor-fold>

    // <editor-fold desc="Block Items">
    public static final DeferredItem<BlockItem> CARPENTER_WORKBENCH =
            ITEMS.registerSimpleBlockItem("carpenter_workbench", ModBlocks.CARPENTER_WORKBENCH);

    public static final DeferredItem<BlockItem> STARSHARD_VEIN =
            ITEMS.registerSimpleBlockItem("starshard_vein", ModBlocks.STARSHARD_VEIN);

    public static final DeferredItem<BlockItem> ARCHEUM_BLOCK_ITEM =
            ITEMS.registerSimpleBlockItem("archeum_block", ModBlocks.ARCHEUM_BLOCK);

    public static final DeferredItem<BlockItem> YATA_FERTILIZER_BLOCK_ITEM =
            ITEMS.registerSimpleBlockItem("yata_fertilizer_block", ModBlocks.YATA_FERTILIZER_BLOCK);
    // </editor-fold>

    // <editor-fold desc="Music Discs">
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
    // </editor-fold>


    public static void register(IEventBus modEventBus) {
        ITEMS.register(modEventBus);
    }
}
