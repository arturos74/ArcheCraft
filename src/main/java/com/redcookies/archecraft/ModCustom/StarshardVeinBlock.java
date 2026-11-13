package com.redcookies.archecraft.ModCustom;

import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SimpleWaterloggedBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.material.FluidState;
import net.minecraft.world.level.material.Fluids;
import net.minecraft.world.level.pathfinder.PathComputationType;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

public class StarshardVeinBlock extends Block implements SimpleWaterloggedBlock {
    public static final MapCodec<StarshardVeinBlock> CODEC = simpleCodec(StarshardVeinBlock::new);
    public static final BooleanProperty WATERLOGGED = BlockStateProperties.WATERLOGGED;

    // Same cuboids as models/block/starshard_vein.json, shared by outline and collision.
    private static final VoxelShape SHAPE = Shapes.or(
            Block.box(2, 0, 2, 14, 2, 14),
            Block.box(0, 0, 5, 3, 2, 11),
            Block.box(13, 0, 4, 16, 1.5, 10),
            Block.box(5, 0, 0, 11, 1.5, 3),
            Block.box(3, 2, 3, 13, 5, 13),
            Block.box(4, 1.5, 1, 10, 4, 4),
            Block.box(1, 2, 6, 4, 4, 11),
            Block.box(12, 1.5, 5, 15, 4, 11),
            Block.box(4, 5, 4, 12, 6, 12),
            Block.box(3, 6, 5, 12, 8.5, 12),
            Block.box(5, 4, 2, 11, 7, 5),
            Block.box(11, 4, 7, 14, 7, 11),
            Block.box(5, 8.5, 6, 11, 9.5, 11),
            Block.box(5, 9.5, 5, 11, 12, 11),
            Block.box(4, 8.5, 7, 6, 10.5, 10),
            Block.box(6, 12, 6, 10, 12.75, 10),
            Block.box(6, 12.75, 7, 10, 15, 10),
            Block.box(7, 15, 7, 9, 16, 9),
            Block.box(12, 0, 1, 15, 2, 3),
            Block.box(0, 0, 13, 2, 1, 15)
    ).optimize();

    public StarshardVeinBlock(Properties properties) {
        super(properties);
        registerDefaultState(stateDefinition.any().setValue(WATERLOGGED, false));
    }

    @Override
    public MapCodec<StarshardVeinBlock> codec() {
        return CODEC;
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return SHAPE;
    }

    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        return defaultBlockState().setValue(WATERLOGGED,
                context.getLevel().getFluidState(context.getClickedPos()).getType() == Fluids.WATER);
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(WATERLOGGED);
    }

    @Override
    protected FluidState getFluidState(BlockState state) {
        return state.getValue(WATERLOGGED) ? Fluids.WATER.getSource(false) : super.getFluidState(state);
    }

    @Override
    protected BlockState updateShape(BlockState state, Direction direction, BlockState neighborState,
                                     LevelAccessor level, BlockPos pos, BlockPos neighborPos) {
        if (state.getValue(WATERLOGGED)) {
            level.scheduleTick(pos, Fluids.WATER, Fluids.WATER.getTickDelay(level));
        }
        return super.updateShape(state, direction, neighborState, level, pos, neighborPos);
    }

    @Override
    protected boolean isPathfindable(BlockState state, PathComputationType type) {
        return false;
    }
}
