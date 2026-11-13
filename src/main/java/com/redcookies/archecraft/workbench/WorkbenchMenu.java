package com.redcookies.archecraft.workbench;

import com.redcookies.archecraft.ModMenus;
import com.redcookies.archecraft.ModRecipes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.Container;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.inventory.DataSlot;
import net.minecraft.world.inventory.ContainerData;
import net.minecraft.world.inventory.SimpleContainerData;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.level.Level;
import java.util.Comparator;
import java.util.List;

public class WorkbenchMenu extends AbstractContainerMenu {
    public static final int INPUT_COLUMNS = 6;
    public static final int INPUT_ROWS = 4;
    public static final int INPUT_COUNT = INPUT_COLUMNS * INPUT_ROWS;
    public static final int RESULT_SLOT = INPUT_COUNT;
    public static final int SLOT_COUNT = INPUT_COUNT + 1;
    public static final int INPUT_X = 144;
    public static final int INPUT_Y = 36;
    public static final int RESULT_X = 286;
    public static final int RESULT_Y = 54;
    public static final int INVENTORY_X = 79;
    public static final int INVENTORY_Y = 140;
    public static final int HOTBAR_Y = 198;
    private final Container container;
    private final Level level;
    private final List<RecipeHolder<WorkbenchRecipe>> recipes;
    private final DataSlot selectedRecipe = DataSlot.standalone();
    private final ContainerData craftData;
    public static final int CRAFT_BUTTON = -1;

    public WorkbenchMenu(int id, Inventory inventory, ResourceLocation workstation) {
        this(id, inventory, new SimpleContainer(SLOT_COUNT), workstation);
    }

    public WorkbenchMenu(int id, Inventory inventory, WorkbenchBlockEntity container) {
        this(id, inventory, container, BuiltInRegistries.BLOCK.getKey(container.getBlockState().getBlock()));
    }

    private WorkbenchMenu(int id, Inventory inventory, Container container, ResourceLocation workstation) {
        super(ModMenus.WORKBENCH.get(), id);
        checkContainerSize(container, SLOT_COUNT);
        this.container = container;
        craftData = container instanceof WorkbenchBlockEntity bench ? bench.getCraftData() : new SimpleContainerData(2);
        addDataSlots(craftData);
        this.level = inventory.player.level();
        this.recipes = level.getRecipeManager().getAllRecipesFor(ModRecipes.WORKBENCH.get()).stream()
                .filter(recipe -> recipe.value().workstation().equals(workstation))
                .sorted(Comparator.comparing(recipe -> recipe.id().toString())).toList();
        selectedRecipe.set(-1);
        if (container instanceof WorkbenchBlockEntity bench) {
            for (int i = 0; i < recipes.size(); i++) {
                if (recipes.get(i).id().equals(bench.getActiveRecipeId())) selectedRecipe.set(i);
            }
        }
        addDataSlot(selectedRecipe);
        container.startOpen(inventory.player);
        for (int row = 0; row < INPUT_ROWS; row++) {
            for (int col = 0; col < INPUT_COLUMNS; col++) {
                addSlot(new Slot(container, row * INPUT_COLUMNS + col, INPUT_X + col * 18, INPUT_Y + row * 18));
            }
        }
        addSlot(new Slot(container, RESULT_SLOT, RESULT_X, RESULT_Y) {
            @Override
            public boolean mayPlace(ItemStack stack) {
                return false;
            }
        });
        for (int row = 0; row < 3; row++) {
            for (int col = 0; col < 9; col++) {
                addSlot(new Slot(inventory, col + row * 9 + 9, INVENTORY_X + col * 18, INVENTORY_Y + row * 18));
            }
        }
        for (int col = 0; col < 9; col++) {
            addSlot(new Slot(inventory, col, INVENTORY_X + col * 18, HOTBAR_Y));
        }
    }

    public List<RecipeHolder<WorkbenchRecipe>> getRecipes() {
        return recipes;
    }

    public int getSelectedRecipeIndex() {
        return selectedRecipe.get();
    }

    public WorkbenchRecipe getSelectedRecipe() {
        int index = selectedRecipe.get();
        return index >= 0 && index < recipes.size() ? recipes.get(index).value() : null;
    }

    public int countInput(Item item) {
        int count = 0;
        for (int slot = 0; slot < INPUT_COUNT; slot++) {
            ItemStack stack = container.getItem(slot);
            if (stack.is(item)) count += stack.getCount();
        }
        return count;
    }

    public boolean canCraft() {
        WorkbenchRecipe recipe = getSelectedRecipe();
        return !isCrafting() && recipe != null && recipe.canCraft(container, level);
    }

    public boolean isCrafting() {
        return craftData.get(1) > 0;
    }

    public float getCraftProgress() {
        return isCrafting() ? Math.clamp((float) craftData.get(0) / craftData.get(1), 0, 1) : 0;
    }

    @Override
    public boolean clickMenuButton(Player player, int id) {
        if (level.isClientSide || !stillValid(player) || player.isSpectator()) return false;
        if (id >= 0 && id < recipes.size()) {
            selectedRecipe.set(id);
            broadcastChanges();
            return true;
        }
        if (id != CRAFT_BUTTON || !canCraft()) return false;
        if (!(container instanceof WorkbenchBlockEntity bench)
                || !bench.startCraft(recipes.get(selectedRecipe.get()))) return false;
        broadcastChanges();
        return true;
    }

    @Override
    public boolean stillValid(Player player) {
        return container.stillValid(player);
    }

    @Override
    public ItemStack quickMoveStack(Player player, int index) {
        if (index < 0 || index >= slots.size()) {
            return ItemStack.EMPTY;
        }
        Slot slot = slots.get(index);
        if (!slot.hasItem()) {
            return ItemStack.EMPTY;
        }
        ItemStack stack = slot.getItem();
        ItemStack original = stack.copy();
        if (index < SLOT_COUNT) {
            if (!moveItemStackTo(stack, SLOT_COUNT, slots.size(), true)) {
                return ItemStack.EMPTY;
            }
        } else if (!moveItemStackTo(stack, 0, INPUT_COUNT, false)) {
            return ItemStack.EMPTY;
        }
        if (stack.isEmpty()) {
            slot.setByPlayer(ItemStack.EMPTY);
        } else {
            slot.setChanged();
        }
        if (stack.getCount() == original.getCount()) {
            return ItemStack.EMPTY;
        }
        slot.onTake(player, stack);
        return original;
    }

    @Override
    public void removed(Player player) {
        super.removed(player);
        container.stopOpen(player);
    }
}
