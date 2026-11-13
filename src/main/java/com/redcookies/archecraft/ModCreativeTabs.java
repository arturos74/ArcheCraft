package com.redcookies.archecraft;

import com.redcookies.archecraft.ArcheCraft;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.CreativeModeTabs;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public class ModCreativeTabs {
    public static final DeferredRegister<CreativeModeTab> CREATIVE_MODE_TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, ArcheCraft.MODID);

    public static final DeferredHolder<CreativeModeTab, CreativeModeTab> EXAMPLE_TAB = CREATIVE_MODE_TABS.register("archecraft",
            () -> CreativeModeTab.builder()
                    .title(Component.translatable("itemGroup.archecraft"))
                    .withTabsBefore(CreativeModeTabs.COMBAT)
                    .icon(() -> ModItems.RAW_ARCHEUM.get().getDefaultInstance())
                    .displayItems((parameters, output) -> {
                        output.accept(ModItems.EXAMPLE_ITEM.get());
                        output.accept(ModItems.RAW_ARCHEUM.get());
                        output.accept(ModItems.ARCHEUM_INGOT.get());
                        output.accept(ModItems.ARCHEUM_BLOCK_ITEM.get());
                        output.accept(ModItems.YATA_MEAT.get());
                        output.accept(ModItems.COOKED_YATA_MEAT.get());
                        output.accept(ModItems.YATA_FUR);
                        output.accept(ModItems.YATA_FERTILIZER);
                        output.accept(ModItems.YATA_FERTILIZER_BLOCK_ITEM);
                        output.accept(ModItems.CLOVER_SEEDS);
                        output.accept(ModItems.CLOVER);
                        output.accept(ModItems.ARCHEUM_ORE);
                        output.accept(ModItems.GOAT_WOOL);
                        output.accept(ModItems.HANDICRAFT_YARN);
                        output.accept(ModItems.BEAR_FUR);
                        output.accept(ModItems.COMBINED_FEED);
                        // Sunlight Archeum
                        output.accept(ModItems.SUNLIGHT_ARCHEUM_MOTES);
                        output.accept(ModItems.SUNLIGHT_ARCHEUM_DUST);
                        output.accept(ModItems.SUNLIGHT_ARCHEUM_SHARD);
                        output.accept(ModItems.SUNLIGHT_ARCHEUM_CRYSTAL);
                        output.accept(ModItems.SUNLIGHT_ARCHEUM_ESSENCE);
                        // Moonlight Archeum
                        output.accept(ModItems.MOONLIGHT_ARCHEUM_MOTES);
                        output.accept(ModItems.MOONLIGHT_ARCHEUM_DUST);
                        output.accept(ModItems.MOONLIGHT_ARCHEUM_SHARD);
                        output.accept(ModItems.MOONLIGHT_ARCHEUM_CRYSTAL);
                        output.accept(ModItems.MOONLIGHT_ARCHEUM_ESSENCE);
                        // Starlight Archeum
                        output.accept(ModItems.STARLIGHT_ARCHEUM_MOTES);
                        output.accept(ModItems.STARLIGHT_ARCHEUM_DUST);
                        output.accept(ModItems.STARLIGHT_ARCHEUM_SHARD);
                        output.accept(ModItems.STARLIGHT_ARCHEUM_CRYSTAL);
                        output.accept(ModItems.STARLIGHT_ARCHEUM_ESSENCE);
                        output.accept(ModItems.HASLA_TOKEN_COURAGE);
                        output.accept(ModItems.HASLA_TOKEN_LOYALTY);
                        output.accept(ModItems.HASLA_TOKEN_CONVICTION);
                        output.accept(ModItems.HASLA_TOKEN_FORTITUDE);
                        output.accept(ModItems.HASLA_TOKEN_HONOR);
                        output.accept(ModItems.HASLA_TOKEN_SACRIFICE);
                        output.accept(ModItems.HASLA_TOKEN_COMPASSION);
                        output.accept(ModItems.RUMBLING_ARCHEUM_TREE_SAPLING);
                        output.accept(ModItems.GILDA_STAR);
                        output.accept(ModItems.BLUE_SALT_BOND);
                        // Wood (Carpentry)
                        output.accept(ModItems.LOG);
                        output.accept(ModItems.LUMBER);
                        output.accept(ModItems.FINE_LUMBER);
                        output.accept(ModItems.NURI_FOREST_LUMBER);
                        output.accept(ModItems.BLAZING_NURI_FOREST_LUMBER);
                        // Metal (Metalwork)
                        output.accept(ModItems.SUNRIDGE_INGOT);
                        output.accept(ModItems.BLAZING_SUNRIDGE_INGOT);
                        output.accept(ModItems.SILVER_ORE);
                        output.accept(ModItems.SILVER_INGOT);
                        output.accept(ModItems.STARSHARD_CHIP);
                        output.accept(ModItems.STARSHARD_INGOT);
                        // Leather (Leatherwork)
                        output.accept(ModItems.PELT);
                        output.accept(ModItems.LEATHER);
                        output.accept(ModItems.FINE_LEATHER);
                        output.accept(ModItems.WIND_SPIRIT_LEATHER);
                        output.accept(ModItems.BLAZING_WIND_SPIRIT_LEATHER);
                        // Cloth (Tailoring)
                        output.accept(ModItems.COTTON);
                        output.accept(ModItems.FABRIC);
                        output.accept(ModItems.BEAUTIFULLY_COLORED_FABRIC);
                        output.accept(ModItems.CLOUDSPUN_FABRIC);
                        output.accept(ModItems.BLAZING_CLOUDSPUN_FABRIC);
                        // Stone (Masonry)
                        output.accept(ModItems.HEREAFTER_STONE);
                        output.accept(ModItems.STURDY_STONE);
                        output.accept(ModItems.RISING_STAR_STONE);
                        // Gems & Special Catalysts
                        output.accept(ModItems.ROUGH_RUBY);
                        output.accept(ModItems.RUBY);
                        output.accept(ModItems.SAPPHIRE);
                        output.accept(ModItems.TOPAZ);
                        output.accept(ModItems.MYSTERIOUS_GARDEN_POWDER);
                        output.accept(ModItems.BLUE_SALT_WEDGE);
                        // Alchemy Oils
                        output.accept(ModItems.SMALL_SEED_OIL);
                        output.accept(ModItems.VISCOUS_GLOSSY_OIL);
                        output.accept(ModItems.EMULSIFIED_OIL);
                        output.accept(ModItems.DEEPLY_COLORED_OIL);
                        // Alchemy Polishes
                        output.accept(ModItems.OPAQUE_POLISH);
                        output.accept(ModItems.ROUGH_POLISH);
                        output.accept(ModItems.NON_STICK_POLISH);
                        output.accept(ModItems.RAINBOW_POLISH);
                        // Alchemy Pigments
                        output.accept(ModItems.SMALL_ROOT_PIGMENT);
                        output.accept(ModItems.SMALL_LEAF_PIGMENT);
                        output.accept(ModItems.SOFT_STEM_PIGMENT);
                        output.accept(ModItems.SCENTED_PETAL_PIGMENT);
                        // Trade Run Stabilizers
                        output.accept(ModItems.CHARCOAL_STABILIZER);
                        output.accept(ModItems.ROCK_SALT_STABILIZER);
                        output.accept(ModItems.CRYSTAL_STABILIZER);
                        output.accept(ModItems.DRAGON_ESSENCE_STABILIZER);
                        output.accept(ModItems.AC_DISC_1);
                        output.accept(ModItems.AC_DISC_2);
                        output.accept(ModItems.AC_DISC_3);
                    }).build());

    public static void register(IEventBus modEventBus) {
        CREATIVE_MODE_TABS.register(modEventBus);
    }
}
