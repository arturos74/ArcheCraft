package com.redcookies.archecraft.workbench;

import com.mojang.serialization.MapCodec;
import net.minecraft.world.phys.shapes.VoxelShape;

public class AlchemyWorkbenchBlock extends TwoBlockWorkbenchBlock {
    public static final MapCodec<AlchemyWorkbenchBlock> CODEC = simpleCodec(AlchemyWorkbenchBlock::new);
    private static final VoxelShape[][] SHAPES = AlchemyWorkbenchShapes.create();

    public AlchemyWorkbenchBlock(Properties properties) {
        super(properties, SHAPES);
    }

    @Override
    public MapCodec<AlchemyWorkbenchBlock> codec() {
        return CODEC;
    }
}
