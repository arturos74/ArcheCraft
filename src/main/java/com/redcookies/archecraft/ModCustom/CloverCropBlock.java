package com.redcookies.archecraft.ModCustom;

import com.redcookies.archecraft.ModBlocks;
import com.redcookies.archecraft.ModItems;
import net.minecraft.world.level.ItemLike;
import net.minecraft.world.level.block.CropBlock;

public class CloverCropBlock extends CropBlock {

    public CloverCropBlock(Properties properties) {
        super(properties);
    }

    @Override
    protected ItemLike getBaseSeedId() {
        return ModItems.CLOVER_SEEDS.get();
    }
}
