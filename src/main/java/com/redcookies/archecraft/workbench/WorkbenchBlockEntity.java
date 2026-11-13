package com.redcookies.archecraft.workbench;

import com.redcookies.archecraft.ModBlockEntities;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.NonNullList;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.world.Containers;
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
import java.util.ArrayList;
import java.util.List;

public class WorkbenchBlockEntity extends BaseContainerBlockEntity {
    public static final int CRAFT_DURATION = 60;
    private NonNullList<ItemStack> items = NonNullList.withSize(WorkbenchMenu.SLOT_COUNT, ItemStack.EMPTY);
    private final List<ItemStack> overflowItems = new ArrayList<>();
    private ResourceLocation activeRecipeId;
    private int craftTicks;
    private boolean legacyFootprintChecked;
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
        if (!bench.legacyFootprintChecked) {
            if (state.getBlock() instanceof StonemasonWorkbenchBlock) {
                StonemasonWorkbenchBlock.removeLegacyPartner(level, pos, state);
            }
            bench.legacyFootprintChecked = true;
        }
        bench.dropOverflowItems();
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

    public void dropOverflowItems() {
        if (level == null || level.isClientSide || overflowItems.isEmpty()) return;
        for (ItemStack stack : overflowItems) {
            Containers.dropItemStack(level, worldPosition.getX() + 0.5, worldPosition.getY() + 0.5,
                    worldPosition.getZ() + 0.5, stack);
        }
        overflowItems.clear();
        setChanged();
    }

    private void recoverLegacyInventory(NonNullList<ItemStack> oldItems) {
        // The old layout had 24 inputs and its result at slot 24.
        items.set(WorkbenchMenu.RESULT_SLOT, oldItems.get(24));
        for (int oldSlot = 0; oldSlot < 24; oldSlot++) {
            ItemStack remaining = oldItems.get(oldSlot).copy();
            if (remaining.isEmpty()) continue;
            for (int slot = 0; slot < WorkbenchMenu.INPUT_COUNT && !remaining.isEmpty(); slot++) {
                ItemStack target = items.get(slot);
                if (!target.isEmpty() && ItemStack.isSameItemSameComponents(target, remaining)) {
                    int amount = Math.min(remaining.getCount(), Math.min(target.getMaxStackSize(), getMaxStackSize(target)) - target.getCount());
                    if (amount > 0) {
                        target.grow(amount);
                        remaining.shrink(amount);
                    }
                }
            }
            for (int slot = 0; slot < WorkbenchMenu.INPUT_COUNT && !remaining.isEmpty(); slot++) {
                if (items.get(slot).isEmpty()) {
                    items.set(slot, remaining.split(Math.min(remaining.getMaxStackSize(), getMaxStackSize(remaining))));
                }
            }
            if (!remaining.isEmpty()) overflowItems.add(remaining);
        }
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
        tag.putInt("InventoryVersion", 2);
        ContainerHelper.saveAllItems(tag, items, registries);
        ListTag overflow = new ListTag();
        for (ItemStack stack : overflowItems) overflow.add(stack.save(registries));
        tag.put("OverflowItems", overflow);
        if (activeRecipeId != null) {
            tag.putString("ActiveRecipe", activeRecipeId.toString());
            tag.putInt("CraftTicks", craftTicks);
        }
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.loadAdditional(tag, registries);
        legacyFootprintChecked = false;
        items = NonNullList.withSize(getContainerSize(), ItemStack.EMPTY);
        overflowItems.clear();
        if (tag.getInt("InventoryVersion") < 2) {
            NonNullList<ItemStack> oldItems = NonNullList.withSize(25, ItemStack.EMPTY);
            ContainerHelper.loadAllItems(tag, oldItems, registries);
            recoverLegacyInventory(oldItems);
        } else {
            ContainerHelper.loadAllItems(tag, items, registries);
        }
        ListTag overflow = tag.getList("OverflowItems", 10);
        for (int i = 0; i < overflow.size(); i++) {
            ItemStack stack = ItemStack.parseOptional(registries, overflow.getCompound(i));
            if (!stack.isEmpty()) overflowItems.add(stack);
        }
        activeRecipeId = ResourceLocation.tryParse(tag.getString("ActiveRecipe"));
        craftTicks = activeRecipeId == null ? 0 : Math.clamp(tag.getInt("CraftTicks"), 0, CRAFT_DURATION - 1);
    }
}
