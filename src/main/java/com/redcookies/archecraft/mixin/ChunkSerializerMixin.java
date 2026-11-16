package com.redcookies.archecraft.mixin;

import com.redcookies.archecraft.worldgen.DrillCampSaveMigration;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.ai.village.poi.PoiManager;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.chunk.ProtoChunk;
import net.minecraft.world.level.chunk.storage.ChunkSerializer;
import net.minecraft.world.level.chunk.storage.RegionStorageInfo;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(ChunkSerializer.class)
abstract class ChunkSerializerMixin {
    @Inject(method = "read", at = @At("HEAD"))
    private static void archecraft$renameSavedCamp(ServerLevel level, PoiManager poi, RegionStorageInfo storage,
                                                  ChunkPos pos, CompoundTag tag, CallbackInfoReturnable<ProtoChunk> callback) {
        if (DrillCampSaveMigration.migrateChunk(tag)) tag.putBoolean("shouldSave", true);
    }
}
