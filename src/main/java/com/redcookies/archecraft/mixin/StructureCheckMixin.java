package com.redcookies.archecraft.mixin;

import com.redcookies.archecraft.worldgen.DrillCampSaveMigration;
import it.unimi.dsi.fastutil.objects.Object2IntMap;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureCheck;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(StructureCheck.class)
abstract class StructureCheckMixin {
    // /locate scans structure metadata without loading the complete chunk.
    @Inject(method = "loadStructures", at = @At("HEAD"))
    private void archecraft$renameScannedCamp(CompoundTag tag, CallbackInfoReturnable<Object2IntMap<Structure>> callback) {
        DrillCampSaveMigration.migrateChunk(tag);
    }
}
