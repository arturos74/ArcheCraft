package com.redcookies.archecraft.workbench;

import com.mojang.serialization.MapCodec;

public class CarpenterWorkbenchBlock extends TwoBlockWorkbenchBlock {
    public static final MapCodec<CarpenterWorkbenchBlock> CODEC = simpleCodec(CarpenterWorkbenchBlock::new);

    public CarpenterWorkbenchBlock(Properties properties) {
        super(properties, CarpenterWorkbenchShapes.create());
    }

    @Override
    public MapCodec<CarpenterWorkbenchBlock> codec() {
        return CODEC;
    }
}
