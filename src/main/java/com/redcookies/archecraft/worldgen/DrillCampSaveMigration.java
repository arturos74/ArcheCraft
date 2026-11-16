package com.redcookies.archecraft.worldgen;

import it.unimi.dsi.fastutil.longs.LongLinkedOpenHashSet;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;

/** Renames saved camp metadata before registry lookup, without editing its blocks. */
public final class DrillCampSaveMigration {
    private static final String OLD_ID = "archecraft:marsh_ruins";
    private static final String NEW_ID = "archecraft:abandoned_drill_camp";

    private DrillCampSaveMigration() {}

    public static boolean migrateChunk(CompoundTag chunk) {
        if (!chunk.contains("structures", Tag.TAG_COMPOUND)) return false;
        boolean changed = false;
        CompoundTag structures = chunk.getCompound("structures");
        CompoundTag starts = structures.getCompound("starts");
        if (starts.contains(OLD_ID, Tag.TAG_COMPOUND)) {
            CompoundTag oldStart = starts.getCompound(OLD_ID);
            if (oldStart.getString("id").equals(OLD_ID)) oldStart.putString("id", NEW_ID);
            if (!starts.contains(NEW_ID, Tag.TAG_COMPOUND)) {
                starts.put(NEW_ID, oldStart);
            } else {
                CompoundTag current = starts.getCompound(NEW_ID);
                if (!valid(current) && valid(oldStart)) {
                    starts.put(NEW_ID, oldStart);
                } else if (valid(current) && valid(oldStart)) {
                    // An upgraded world can already contain both names in a chunk.
                    // Keep distinct saved pieces and all structure reference data.
                    ListTag pieces = current.getList("Children", Tag.TAG_COMPOUND);
                    for (Tag piece : oldStart.getList("Children", Tag.TAG_COMPOUND)) {
                        if (!pieces.contains(piece)) pieces.add(piece.copy());
                    }
                    current.put("Children", pieces);
                    current.putInt("references", Math.max(current.getInt("references"), oldStart.getInt("references")));
                }
            }
            starts.remove(OLD_ID);
            changed = true;
        }
        CompoundTag references = structures.getCompound("References");
        if (references.contains(OLD_ID, Tag.TAG_LONG_ARRAY)) {
            LongLinkedOpenHashSet merged = new LongLinkedOpenHashSet(references.getLongArray(NEW_ID));
            for (long reference : references.getLongArray(OLD_ID)) merged.add(reference);
            references.putLongArray(NEW_ID, merged.toLongArray());
            references.remove(OLD_ID);
            changed = true;
        }
        return changed;
    }

    private static boolean valid(CompoundTag start) {
        String id = start.getString("id");
        return !id.isEmpty() && !id.equals("INVALID");
    }
}
