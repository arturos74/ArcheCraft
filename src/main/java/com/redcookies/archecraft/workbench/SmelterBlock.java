package com.redcookies.archecraft.workbench;

import com.mojang.serialization.MapCodec;
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
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.Mirror;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.level.pathfinder.PathComputationType;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

public class SmelterBlock extends WorkbenchBlock {
    public static final MapCodec<SmelterBlock> CODEC = simpleCodec(SmelterBlock::new);
    public static final DirectionProperty FACING = BlockStateProperties.HORIZONTAL_FACING;
    public static final EnumProperty<Part> PART = EnumProperty.create("part", Part.class);
    public static final BooleanProperty CONTROLLER = BooleanProperty.create("controller");
    private static final VoxelShape[][] SHAPES = SmelterShapes.create();
    private static final ThreadLocal<Boolean> CHANGING_STRUCTURE = ThreadLocal.withInitial(() -> false);

    public enum Part implements StringRepresentable {
        FRONT_LEFT(0,0), FRONT_RIGHT(1,0), BACK_LEFT(0,1), BACK_RIGHT(1,1);
        final int right, back;
        Part(int right, int back) { this.right=right; this.back=back; }
        @Override public String getSerializedName() { return name().toLowerCase(java.util.Locale.ROOT); }
        Part reflected() { return values()[ordinal() ^ 1]; }
    }

    public SmelterBlock(Properties properties) {
        super(properties);
        registerDefaultState(stateDefinition.any().setValue(FACING,Direction.NORTH)
                .setValue(PART,Part.FRONT_LEFT).setValue(CONTROLLER,true));
    }

    @Override public MapCodec<SmelterBlock> codec() { return CODEC; }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block,BlockState> builder) {
        builder.add(FACING,PART,CONTROLLER);
    }

    public static BlockPos originPos(BlockPos pos,BlockState state) {
        Part part=state.getValue(PART); Direction facing=state.getValue(FACING);
        return pos.relative(facing.getCounterClockWise(),-part.right).relative(facing.getOpposite(),-part.back);
    }

    public static BlockPos sectionPos(BlockPos origin,Direction facing,Part part) {
        return origin.relative(facing.getCounterClockWise(),part.right).relative(facing.getOpposite(),part.back);
    }

    private boolean matches(BlockState candidate,Direction facing,Part part) {
        return candidate.is(this) && candidate.getValue(FACING)==facing && candidate.getValue(PART)==part;
    }

    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        Direction facing=context.getHorizontalDirection().getOpposite();
        for (Part part : Part.values()) {
            BlockPos target=sectionPos(context.getClickedPos(),facing,part);
            if (!context.getLevel().getWorldBorder().isWithinBounds(target)
                    || !context.getLevel().getBlockState(target).canBeReplaced(context)) return null;
        }
        return defaultBlockState().setValue(FACING,facing);
    }

    @Override
    public void setPlacedBy(Level level,BlockPos pos,BlockState state,LivingEntity placer,ItemStack stack) {
        super.setPlacedBy(level,pos,state,placer,stack);
        if (level.isClientSide) return;
        CHANGING_STRUCTURE.set(true);
        try {
            for (Part part : Part.values()) {
                if (part!=Part.FRONT_LEFT) level.setBlock(sectionPos(pos,state.getValue(FACING),part),
                        state.setValue(PART,part).setValue(CONTROLLER,false),3);
            }
        } finally { CHANGING_STRUCTURE.remove(); }
    }

    @Override
    public BlockEntity newBlockEntity(BlockPos pos,BlockState state) {
        return state.getValue(CONTROLLER) ? super.newBlockEntity(pos,state) : null;
    }

    @Override
    public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level level,BlockState state,BlockEntityType<T> type) {
        return state.getValue(CONTROLLER) ? super.getTicker(level,state,type) : null;
    }

    private WorkbenchBlockEntity findController(BlockState state,Level level,BlockPos pos) {
        BlockPos origin=originPos(pos,state); Direction facing=state.getValue(FACING);
        for (Part part : Part.values()) {
            BlockPos target=sectionPos(origin,facing,part);BlockState candidate=level.getBlockState(target);
            if (matches(candidate,facing,part) && candidate.getValue(CONTROLLER)
                    && level.getBlockEntity(target) instanceof WorkbenchBlockEntity bench) return bench;
        }
        return null;
    }

    @Override
    protected MenuProvider getMenuProvider(BlockState state,Level level,BlockPos pos) {
        return findController(state,level,pos);
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state,Level level,BlockPos pos,Player player,BlockHitResult hit) {
        WorkbenchBlockEntity bench=findController(state,level,pos);
        return bench==null ? InteractionResult.PASS
                : super.useWithoutItem(bench.getBlockState(),level,bench.getBlockPos(),player,hit);
    }

    private boolean complete(BlockState state,LevelAccessor level,BlockPos pos) {
        BlockPos origin=originPos(pos,state);Direction facing=state.getValue(FACING);int controllers=0;
        for (Part part : Part.values()) {
            BlockState candidate=level.getBlockState(sectionPos(origin,facing,part));
            if (!matches(candidate,facing,part)) return false;
            if (candidate.getValue(CONTROLLER)) controllers++;
        }
        return controllers==1;
    }

    @Override
    protected BlockState updateShape(BlockState state,Direction direction,BlockState neighbor,LevelAccessor level,
                                     BlockPos pos,BlockPos neighborPos) {
        // Client section packets arrive separately. The server validates and removes the structure.
        if (!(level instanceof Level world && world.isClientSide) && !CHANGING_STRUCTURE.get()
                && direction.getAxis().isHorizontal() && !complete(state,level,pos)) {
            return Blocks.AIR.defaultBlockState();
        }
        return super.updateShape(state,direction,neighbor,level,pos,neighborPos);
    }

    private void removeOthers(Level level,BlockPos pos,BlockState state,boolean dropController) {
        if (level.isClientSide || CHANGING_STRUCTURE.get()) return;
        BlockPos origin=originPos(pos,state);Direction facing=state.getValue(FACING);
        CHANGING_STRUCTURE.set(true);
        try {
            for (Part part : Part.values()) {
                BlockPos target=sectionPos(origin,facing,part);
                if (target.equals(pos)) continue;
                BlockState candidate=level.getBlockState(target);
                if (matches(candidate,facing,part)) level.destroyBlock(target,dropController && candidate.getValue(CONTROLLER));
            }
        } finally { CHANGING_STRUCTURE.remove(); }
    }

    @Override
    public BlockState playerWillDestroy(Level level,BlockPos pos,BlockState state,Player player) {
        if (player.isCreative() || !player.hasCorrectToolForDrops(state,level,pos)) removeOthers(level,pos,state,false);
        return super.playerWillDestroy(level,pos,state,player);
    }

    @Override
    protected void onRemove(BlockState state,Level level,BlockPos pos,BlockState newState,boolean moving) {
        if (!state.is(newState.getBlock())) removeOthers(level,pos,state,!state.getValue(CONTROLLER));
        super.onRemove(state,level,pos,newState,moving);
    }

    @Override
    protected VoxelShape getShape(BlockState state,BlockGetter level,BlockPos pos,CollisionContext context) {
        return SHAPES[state.getValue(PART).ordinal()][state.getValue(FACING).get2DDataValue()];
    }

    @Override protected BlockState rotate(BlockState state,Rotation rotation) {
        return state.setValue(FACING,rotation.rotate(state.getValue(FACING)));
    }
    @Override protected BlockState mirror(BlockState state,Mirror mirror) {
        return mirror==Mirror.NONE ? state : state.setValue(FACING,mirror.mirror(state.getValue(FACING)))
                .setValue(PART,state.getValue(PART).reflected());
    }
    @Override protected boolean isPathfindable(BlockState state,PathComputationType type) { return false; }
}
