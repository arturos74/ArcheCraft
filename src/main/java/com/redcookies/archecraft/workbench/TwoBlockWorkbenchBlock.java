package com.redcookies.archecraft.workbench;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.StringRepresentable;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.MenuProvider;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Mirror;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.level.pathfinder.PathComputationType;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

public abstract class TwoBlockWorkbenchBlock extends WorkbenchBlock {
    public static final DirectionProperty FACING = BlockStateProperties.HORIZONTAL_FACING;
    public static final EnumProperty<Part> PART = EnumProperty.create("part", Part.class);
    private static final ThreadLocal<Boolean> REMOVING_PAIR = ThreadLocal.withInitial(() -> false);
    private final VoxelShape[][] shapes;

    public enum Part implements StringRepresentable {
        LEFT, RIGHT;

        @Override
        public String getSerializedName() {
            return name().toLowerCase(java.util.Locale.ROOT);
        }
    }

    protected TwoBlockWorkbenchBlock(Properties properties, VoxelShape[][] shapes) {
        super(properties);
        this.shapes = shapes;
        registerDefaultState(stateDefinition.any().setValue(FACING, Direction.NORTH).setValue(PART, Part.LEFT));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FACING, PART);
    }

    public static BlockPos primaryPos(BlockPos pos, BlockState state) {
        return state.getValue(PART) == Part.LEFT ? pos : pos.relative(state.getValue(FACING).getCounterClockWise());
    }

    private static BlockPos partnerPos(BlockPos pos, BlockState state) {
        return pos.relative(state.getValue(PART) == Part.LEFT
                ? state.getValue(FACING).getClockWise() : state.getValue(FACING).getCounterClockWise());
    }

    private boolean isPartner(BlockState state, BlockState other) {
        return other.is(this) && other.getValue(PART) != state.getValue(PART)
                && other.getValue(FACING) == state.getValue(FACING);
    }

    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        Direction facing = context.getHorizontalDirection().getOpposite();
        BlockPos second = context.getClickedPos().relative(facing.getClockWise());
        return context.getLevel().getWorldBorder().isWithinBounds(second)
                && context.getLevel().getBlockState(second).canBeReplaced(context)
                ? defaultBlockState().setValue(FACING, facing) : null;
    }

    @Override
    public void setPlacedBy(Level level, BlockPos pos, BlockState state, LivingEntity placer, ItemStack stack) {
        super.setPlacedBy(level, pos, state, placer, stack);
        if (!level.isClientSide) {
            level.setBlock(partnerPos(pos, state), state.setValue(PART, Part.RIGHT), 3);
        }
    }

    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return state.getValue(PART) == Part.LEFT ? super.newBlockEntity(pos, state) : null;
    }

    @Override
    public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level level, BlockState state, BlockEntityType<T> type) {
        return state.getValue(PART) == Part.LEFT ? super.getTicker(level, state, type) : null;
    }

    @Override
    protected MenuProvider getMenuProvider(BlockState state, Level level, BlockPos pos) {
        BlockPos primary = primaryPos(pos, state);
        return level.getBlockEntity(primary) instanceof WorkbenchBlockEntity bench ? bench : null;
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        BlockPos primary = primaryPos(pos, state);
        return super.useWithoutItem(level.getBlockState(primary), level, primary, player, hit);
    }

    @Override
    protected BlockState updateShape(BlockState state, Direction direction, BlockState neighbor, LevelAccessor level,
                                     BlockPos pos, BlockPos neighborPos) {
        if (!REMOVING_PAIR.get() && neighborPos.equals(partnerPos(pos, state)) && !isPartner(state, neighbor)) {
            return net.minecraft.world.level.block.Blocks.AIR.defaultBlockState();
        }
        return super.updateShape(state, direction, neighbor, level, pos, neighborPos);
    }

    private void removePartner(Level level, BlockPos pos, BlockState state, boolean dropItem) {
        if (level.isClientSide || REMOVING_PAIR.get()) return;
        BlockPos partner = partnerPos(pos, state);
        if (!isPartner(state, level.getBlockState(partner))) return;
        REMOVING_PAIR.set(true);
        try {
            level.destroyBlock(partner, dropItem);
        } finally {
            REMOVING_PAIR.remove();
        }
    }

    @Override
    public BlockState playerWillDestroy(Level level, BlockPos pos, BlockState state, Player player) {
        if (player.isCreative()) removePartner(level, pos, state, false);
        return super.playerWillDestroy(level, pos, state, player);
    }

    @Override
    protected void onRemove(BlockState state, Level level, BlockPos pos, BlockState newState, boolean moving) {
        if (!state.is(newState.getBlock())) {
            // Only the left half has item loot and inventory. Removing the right harvests that half once.
            removePartner(level, pos, state, state.getValue(PART) == Part.RIGHT);
        }
        super.onRemove(state, level, pos, newState, moving);
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        // Authoring models face south. Match the blockstate's 180-degree rotation
        // and swapped source halves while FACING continues to point toward the player.
        return shapes[1 - state.getValue(PART).ordinal()][state.getValue(FACING).getOpposite().get2DDataValue()];
    }

    @Override
    protected BlockState rotate(BlockState state, Rotation rotation) {
        return state.setValue(FACING, rotation.rotate(state.getValue(FACING)));
    }

    @Override
    protected BlockState mirror(BlockState state, Mirror mirror) {
        // Keep inventory attached to the primary half when a structure is reflected.
        if (mirror == Mirror.NONE) return state;
        return state.setValue(FACING, mirror.mirror(state.getValue(FACING)).getOpposite());
    }

    @Override
    protected boolean isPathfindable(BlockState state, PathComputationType type) {
        return false;
    }
}
