package com.redcookies.archecraft;

import com.redcookies.archecraft.entity.YataEntity;
import com.redcookies.archecraft.entity.SarraceniaEntity;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.SpawnPlacementTypes;
import net.minecraft.world.level.levelgen.Heightmap;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.event.entity.EntityAttributeCreationEvent;
import net.neoforged.neoforge.event.entity.RegisterSpawnPlacementsEvent;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModEntities {
    public static final DeferredRegister<EntityType<?>> ENTITY_TYPES =
            DeferredRegister.create(Registries.ENTITY_TYPE, ArcheCraft.MODID);

    public static final DeferredHolder<EntityType<?>, EntityType<YataEntity>> YATA =
            ENTITY_TYPES.register("yata", () -> EntityType.Builder.of(YataEntity::new, MobCategory.CREATURE)
                    .sized(1.3964844F, 1.6F)
                    .eyeHeight(1.52F)
                    .clientTrackingRange(10)
                    .build(ArcheCraft.MODID + ":yata"));

    public static final DeferredHolder<EntityType<?>, EntityType<SarraceniaEntity>> SARRACENIA =
            ENTITY_TYPES.register("sarracenia", () -> EntityType.Builder.of(SarraceniaEntity::new, MobCategory.MONSTER)
                    .sized(1.2F, 1.7F)
                    .eyeHeight(1.45F)
                    .clientTrackingRange(10)
                    .build(ArcheCraft.MODID + ":sarracenia"));

    private ModEntities() {}

    public static void register(IEventBus bus) {
        // Resolve saved mobs and entity-data components from before the rename.
        ENTITY_TYPES.addAlias(ResourceLocation.fromNamespaceAndPath(ArcheCraft.MODID, "pitcher_plant"),
                ResourceLocation.fromNamespaceAndPath(ArcheCraft.MODID, "sarracenia"));
        ENTITY_TYPES.register(bus);
        bus.addListener(ModEntities::createAttributes);
        bus.addListener(ModEntities::registerSpawnPlacements);
    }

    private static void createAttributes(EntityAttributeCreationEvent event) {
        event.put(YATA.get(), YataEntity.createAttributes().build());
        event.put(SARRACENIA.get(), SarraceniaEntity.createAttributes().build());
    }

    private static void registerSpawnPlacements(RegisterSpawnPlacementsEvent event) {
        event.register(SARRACENIA.get(), SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                SarraceniaEntity::checkSpawnRules, RegisterSpawnPlacementsEvent.Operation.REPLACE);
    }
}
