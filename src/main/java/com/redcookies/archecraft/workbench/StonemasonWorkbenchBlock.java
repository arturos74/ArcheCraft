package com.redcookies.archecraft.workbench;

import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Mirror;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

public class StonemasonWorkbenchBlock extends WorkbenchBlock {
    public static final MapCodec<StonemasonWorkbenchBlock> CODEC = simpleCodec(StonemasonWorkbenchBlock::new);
    public static final DirectionProperty FACING = BlockStateProperties.HORIZONTAL_FACING;
    // Retained to recognize saved halves from the original two-space version.
    public static final EnumProperty<TwoBlockWorkbenchBlock.Part> PART = TwoBlockWorkbenchBlock.PART;
    private static final VoxelShape[] SHAPES = StonemasonWorkbenchShapes.create();

    public StonemasonWorkbenchBlock(Properties properties) {
        super(properties);
        registerDefaultState(stateDefinition.any().setValue(FACING, Direction.NORTH)
                .setValue(PART, TwoBlockWorkbenchBlock.Part.LEFT));
    }

    @Override
    public MapCodec<StonemasonWorkbenchBlock> codec() {
        return CODEC;
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FACING, PART);
    }

    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        return defaultBlockState().setValue(FACING, context.getHorizontalDirection().getOpposite());
    }

    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return state.getValue(PART) == TwoBlockWorkbenchBlock.Part.RIGHT ? null : super.newBlockEntity(pos, state);
    }

    static void removeLegacyPartner(Level level, BlockPos pos, BlockState state) {
        if (level.isClientSide || state.getValue(PART) != TwoBlockWorkbenchBlock.Part.LEFT) return;
        BlockPos oldPartner = pos.relative(state.getValue(FACING).getClockWise());
        BlockState neighbor = level.getBlockState(oldPartner);
        if (neighbor.is(state.getBlock()) && neighbor.getValue(PART) == TwoBlockWorkbenchBlock.Part.RIGHT
                && neighbor.getValue(FACING) == state.getValue(FACING)) {
            // The retired half never owned an inventory or its own workbench item.
            level.removeBlock(oldPartner, false);
        }
    }

    @Override
    protected void onRemove(BlockState state, Level level, BlockPos pos, BlockState newState, boolean moving) {
        if (!state.is(newState.getBlock())) removeLegacyPartner(level, pos, state);
        super.onRemove(state, level, pos, newState, moving);
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return SHAPES[state.getValue(FACING).get2DDataValue()];
    }

    @Override
    protected BlockState rotate(BlockState state, Rotation rotation) {
        return state.setValue(FACING, rotation.rotate(state.getValue(FACING)));
    }

    @Override
    protected BlockState mirror(BlockState state, Mirror mirror) {
        return state.setValue(FACING, mirror.mirror(state.getValue(FACING)));
    }
}
