package com.redcookies.archecraft.client;

import com.redcookies.archecraft.workbench.WorkbenchMenu;
import com.redcookies.archecraft.workbench.WorkbenchRecipe;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.util.Mth;

public class WorkbenchScreen extends AbstractContainerScreen<WorkbenchMenu> {
    private static final int RECIPE_Y = 32;
    private static final int RECIPE_HEIGHT = 28;
    private static final int VISIBLE_RECIPES = 3;
    private Button craft;
    private int firstRecipe;
    private boolean draggingScrollbar;
    public WorkbenchScreen(WorkbenchMenu menu, Inventory inventory, Component title) {
        super(menu, inventory, title);
        imageWidth = 320;
        imageHeight = 222;
        inventoryLabelX = WorkbenchMenu.INVENTORY_X;
        inventoryLabelY = 128;
    }

    @Override
    protected void init() {
        super.init();
        craft = addRenderableWidget(Button.builder(Component.translatable("gui.archecraft.workbench.craft"),
                        button -> sendButton(WorkbenchMenu.CRAFT_BUTTON))
                .bounds(leftPos + 263, topPos + 88, 48, 20).build());
        craft.active = menu.canCraft();
    }

    private void sendButton(int id) {
        minecraft.gameMode.handleInventoryButtonClick(menu.containerId, id);
    }

    @Override
    protected void renderBg(GuiGraphics graphics, float partialTick, int mouseX, int mouseY) {
        panel(graphics, leftPos, topPos, imageWidth, imageHeight);
        inset(graphics, 8, 29, 124, 91);
        graphics.fill(leftPos + 121, topPos + 31, leftPos + 130, topPos + 118, 0xFF373737);
        int maxScroll = maxScroll();
        firstRecipe = Mth.clamp(firstRecipe, 0, maxScroll);
        int thumbY = maxScroll == 0 ? 0 : firstRecipe * 66 / maxScroll;
        panel(graphics, leftPos + 122, topPos + 32 + thumbY, 7, 19);
        if (menu.getRecipes().isEmpty()) {
            graphics.drawWordWrap(font, Component.translatable("gui.archecraft.workbench.no_recipes"),
                    leftPos + 15, topPos + 43, 100, 0xFFD0D0D0);
        } else {
            for (int row = 0; row < VISIBLE_RECIPES && firstRecipe + row < menu.getRecipes().size(); row++) {
                int index = firstRecipe + row;
                WorkbenchRecipe recipe = menu.getRecipes().get(index).value();
                int y = topPos + RECIPE_Y + row * RECIPE_HEIGHT;
                boolean selected = index == menu.getSelectedRecipeIndex();
                boolean hovered = hoveredRecipe(mouseX, mouseY) == index;
                graphics.fill(leftPos + 11, y, leftPos + 119, y + RECIPE_HEIGHT - 2,
                        selected ? 0xFF596D44 : hovered ? 0xFF666666 : 0xFF555555);
                graphics.renderItem(recipe.result(), leftPos + 15, y + 5);
                graphics.renderItemDecorations(font, recipe.result(), leftPos + 15, y + 5);
                graphics.drawString(font, font.plainSubstrByWidth(recipe.getDisplayName().getString(), 81),
                        leftPos + 34, y + 3, 0xFFFFFFFF, false);
                int x = leftPos + 34;
                // Compact ingredient icons and counts; hover for the complete ingredient names.
                for (int i = 0; i < Math.min(2, recipe.materials().size()); i++) {
                    WorkbenchRecipe.Material material = recipe.materials().get(i);
                    int color = menu.countInput(material.item()) >= recipe.requiredCounts().get(material.item()) ? 0xFFB4EF92 : 0xFFFFBBBB;
                    if (i > 0) {
                        graphics.drawString(font, "+", x, y + 15, 0xFFD0D0D0, false);
                        x += 8;
                    }
                    String count = String.valueOf(material.count());
                    graphics.drawString(font, count, x, y + 15, color, false);
                    x += font.width(count) + 1;
                    graphics.pose().pushPose();
                    graphics.pose().translate(x, y + 13, 0);
                    graphics.pose().scale(0.6875F, 0.6875F, 1);
                    graphics.renderItem(new ItemStack(material.item()), 0, 0);
                    graphics.pose().popPose();
                    x += 13;
                }
                if (recipe.materials().size() > 2) graphics.drawString(font, "...", x, y + 15, 0xFFD0D0D0, false);
            }
        }
        graphics.fill(leftPos + 8, topPos + 124, leftPos + 312, topPos + 125, 0xFF777777);
        for (Slot slot : menu.slots) {
            inset(graphics, slot.x - 1, slot.y - 1, 18, 18);
        }
        // Fill the arrow from left to right with the server's crafting progress.
        int filled = (int) (menu.getCraftProgress() * 18);
        for (int x = 0; x < 18; x++) {
            int halfHeight = x < 12 ? 2 : 6 - (x - 12);
            graphics.fill(leftPos + 257 + x, topPos + 62 - halfHeight,
                    leftPos + 258 + x, topPos + 62 + halfHeight,
                    x < filled ? 0xFFFFFFFF : 0xFF555555);
        }
    }

    @Override
    protected void renderLabels(GuiGraphics graphics, int mouseX, int mouseY) {
        super.renderLabels(graphics, mouseX, mouseY);
        graphics.drawString(font, Component.translatable("gui.archecraft.workbench.recipes"), 8, 19, 0x404040, false);
        graphics.drawString(font, Component.translatable("gui.archecraft.workbench.ingredients"),
                WorkbenchMenu.INPUT_X, WorkbenchMenu.INPUT_Y - 13, 0x404040, false);
        graphics.drawString(font, Component.translatable("gui.archecraft.workbench.result"), 278, 39, 0x404040, false);
    }

    @Override
    public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        craft.active = menu.canCraft();
        craft.setMessage(Component.translatable(menu.isCrafting()
                ? "gui.archecraft.workbench.crafting" : "gui.archecraft.workbench.craft"));
        super.render(graphics, mouseX, mouseY, partialTick);
        renderTooltip(graphics, mouseX, mouseY);
        int hovered = hoveredRecipe(mouseX, mouseY);
        if (hovered >= 0) {
            WorkbenchRecipe recipe = menu.getRecipes().get(hovered).value();
            java.util.List<Component> lines = new java.util.ArrayList<>();
            lines.add(recipe.getDisplayName());
            lines.add(Component.literal(recipe.result().getCount() + " x ").append(recipe.result().getHoverName()));
            for (WorkbenchRecipe.Material material : recipe.materials()) {
                lines.add(Component.literal(material.count() + " x ").append(material.item().getDescription()));
            }
            graphics.renderComponentTooltip(font, lines, mouseX, mouseY);
        }
    }

    private int maxScroll() {
        return Math.max(0, menu.getRecipes().size() - VISIBLE_RECIPES);
    }

    private int hoveredRecipe(double x, double y) {
        double offsetY = y - topPos - RECIPE_Y;
        if (x < leftPos + 11 || x >= leftPos + 119 || offsetY < 0 || offsetY >= VISIBLE_RECIPES * RECIPE_HEIGHT) return -1;
        if (offsetY % RECIPE_HEIGHT >= RECIPE_HEIGHT - 2) return -1;
        int index = firstRecipe + (int) (offsetY / RECIPE_HEIGHT);
        return index < menu.getRecipes().size() ? index : -1;
    }

    @Override
    public boolean mouseClicked(double x, double y, int button) {
        int hovered = hoveredRecipe(x, y);
        if (button == 0 && hovered >= 0) {
            sendButton(hovered);
            return true;
        }
        if (button == 0 && maxScroll() > 0 && x >= leftPos + 121 && x < leftPos + 131
                && y >= topPos + 31 && y < topPos + 118) {
            draggingScrollbar = true;
            scrollTo(y);
            return true;
        }
        return super.mouseClicked(x, y, button);
    }

    private void scrollTo(double y) {
        double fraction = Mth.clamp((y - topPos - 41) / 66.0, 0, 1);
        firstRecipe = (int) Math.round(fraction * maxScroll());
    }

    @Override
    public boolean mouseDragged(double x, double y, int button, double dx, double dy) {
        if (draggingScrollbar) {
            scrollTo(y);
            return true;
        }
        return super.mouseDragged(x, y, button, dx, dy);
    }

    @Override
    public boolean mouseReleased(double x, double y, int button) {
        draggingScrollbar = false;
        return super.mouseReleased(x, y, button);
    }

    @Override
    public boolean mouseScrolled(double x, double y, double scrollX, double scrollY) {
        if (x >= leftPos + 8 && x < leftPos + 132 && y >= topPos + 29 && y < topPos + 120) {
            firstRecipe = Mth.clamp(firstRecipe - (int) Math.signum(scrollY), 0, maxScroll());
            return true;
        }
        return super.mouseScrolled(x, y, scrollX, scrollY);
    }

    private static void panel(GuiGraphics graphics, int x, int y, int width, int height) {
        graphics.fill(x, y, x + width, y + height, 0xFF373737);
        graphics.fill(x + 1, y + 1, x + width - 1, y + height - 1, 0xFFFFFFFF);
        graphics.fill(x + 3, y + 3, x + width - 1, y + height - 1, 0xFF555555);
        graphics.fill(x + 3, y + 3, x + width - 3, y + height - 3, 0xFFC6C6C6);
    }

    private void inset(GuiGraphics graphics, int x, int y, int width, int height) {
        x += leftPos;
        y += topPos;
        graphics.fill(x, y, x + width, y + height, 0xFFFFFFFF);
        graphics.fill(x, y, x + width - 1, y + height - 1, 0xFF373737);
        graphics.fill(x + 1, y + 1, x + width - 1, y + height - 1, 0xFF8B8B8B);
    }
}
