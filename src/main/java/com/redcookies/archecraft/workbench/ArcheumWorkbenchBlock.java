package com.redcookies.archecraft.workbench;

import com.mojang.serialization.MapCodec;

public class ArcheumWorkbenchBlock extends TwoBlockWorkbenchBlock {
    public static final MapCodec<ArcheumWorkbenchBlock> CODEC = simpleCodec(ArcheumWorkbenchBlock::new);

    public ArcheumWorkbenchBlock(Properties properties) {
        super(properties, ArcheumWorkbenchShapes.create());
    }

    @Override
    public MapCodec<ArcheumWorkbenchBlock> codec() {
        return CODEC;
    }
}
