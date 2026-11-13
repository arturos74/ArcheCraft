package com.redcookies.archecraft.workbench;

import com.redcookies.archecraft.ModBlockEntities;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.NonNullList;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.ContainerHelper;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ContainerData;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.level.Level;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BaseContainerBlockEntity;
import net.minecraft.world.level.block.state.BlockState;

public class WorkbenchBlockEntity extends BaseContainerBlockEntity {
    public static final int CRAFT_DURATION = 60;
    private NonNullList<ItemStack> items = NonNullList.withSize(WorkbenchMenu.SLOT_COUNT, ItemStack.EMPTY);
    private ResourceLocation activeRecipeId;
    private int craftTicks;
    private final ContainerData craftData = new ContainerData() {
        @Override
        public int get(int index) {
            return index == 0 ? craftTicks : activeRecipeId == null ? 0 : CRAFT_DURATION;
        }

        @Override
        public void set(int index, int value) {
            if (index == 0) craftTicks = value;
        }

        @Override
        public int getCount() {
            return 2;
        }
    };

    public WorkbenchBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.WORKBENCH.get(), pos, state);
    }

    public ContainerData getCraftData() {
        return craftData;
    }

    public ResourceLocation getActiveRecipeId() {
        return activeRecipeId;
    }

    public boolean startCraft(RecipeHolder<WorkbenchRecipe> recipe) {
        if (level == null || level.isClientSide || isRemoved() || activeRecipeId != null
                || !recipe.value().workstation().equals(BuiltInRegistries.BLOCK.getKey(getBlockState().getBlock()))
                || !recipe.value().canCraft(this, level)) return false;
        activeRecipeId = recipe.id();
        craftTicks = 0;
        setChanged();
        return true;
    }

    public static void serverTick(Level level, BlockPos pos, BlockState state, WorkbenchBlockEntity bench) {
        if (bench.activeRecipeId == null) return;
        var holder = level.getRecipeManager().byKey(bench.activeRecipeId).orElse(null);
        if (holder == null || !(holder.value() instanceof WorkbenchRecipe recipe)
                || !recipe.workstation().equals(BuiltInRegistries.BLOCK.getKey(state.getBlock()))
                || !recipe.matches(new WorkbenchRecipe.Input(bench), level)) {
            // Removing required ingredients cancels the job without consuming anything.
            bench.clearJob();
            return;
        }
        // If another player fills the output, wait until there is space again.
        if (!recipe.hasOutputSpace(bench, level)) return;
        bench.craftTicks++;
        if (bench.craftTicks >= CRAFT_DURATION) {
            recipe.finishCraft(bench);
            bench.clearJob();
        }
        bench.setChanged();
    }

    private void clearJob() {
        activeRecipeId = null;
        craftTicks = 0;
        setChanged();
    }

    @Override
    protected Component getDefaultName() {
        return getBlockState().getBlock().getName();
    }

    @Override
    protected AbstractContainerMenu createMenu(int id, Inventory inventory) {
        return new WorkbenchMenu(id, inventory, this);
    }

    @Override
    public int getContainerSize() {
        return WorkbenchMenu.SLOT_COUNT;
    }

    @Override
    protected NonNullList<ItemStack> getItems() {
        return items;
    }

    @Override
    protected void setItems(NonNullList<ItemStack> items) {
        this.items = items;
    }

    @Override
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.saveAdditional(tag, registries);
        ContainerHelper.saveAllItems(tag, items, registries);
        if (activeRecipeId != null) {
            tag.putString("ActiveRecipe", activeRecipeId.toString());
            tag.putInt("CraftTicks", craftTicks);
        }
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.loadAdditional(tag, registries);
        items = NonNullList.withSize(getContainerSize(), ItemStack.EMPTY);
        ContainerHelper.loadAllItems(tag, items, registries);
        activeRecipeId = ResourceLocation.tryParse(tag.getString("ActiveRecipe"));
        craftTicks = activeRecipeId == null ? 0 : Math.clamp(tag.getInt("CraftTicks"), 0, CRAFT_DURATION - 1);
    }
}
