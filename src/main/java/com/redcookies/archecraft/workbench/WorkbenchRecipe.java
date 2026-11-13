package com.redcookies.archecraft.workbench;

import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import com.redcookies.archecraft.ModRecipes;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.Container;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeInput;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.level.Level;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public record WorkbenchRecipe(ResourceLocation workstation, List<Material> materials, ItemStack result)
        implements Recipe<WorkbenchRecipe.Input> {
    public record Material(Item item, int count) {
        public static final Codec<Material> CODEC = RecordCodecBuilder.create(instance -> instance.group(
                BuiltInRegistries.ITEM.byNameCodec().fieldOf("item").forGetter(Material::item),
                Codec.intRange(1, 1536).fieldOf("count").forGetter(Material::count)
        ).apply(instance, Material::new));
        public static final StreamCodec<RegistryFriendlyByteBuf, Material> STREAM_CODEC = StreamCodec.composite(
                ByteBufCodecs.registry(Registries.ITEM), Material::item,
                ByteBufCodecs.VAR_INT, Material::count, Material::new);
    }

    public record Input(Container container) implements RecipeInput {
        @Override
        public ItemStack getItem(int index) {
            if (index < 0 || index >= size()) throw new IndexOutOfBoundsException(index);
            return container.getItem(index);
        }

        @Override
        public int size() {
            return WorkbenchMenu.INPUT_COUNT;
        }
    }

    public Map<Item, Integer> requiredCounts() {
        Map<Item, Integer> counts = new HashMap<>();
        for (Material material : materials) counts.merge(material.item(), material.count(), Integer::sum);
        return counts;
    }

    public boolean hasOutputSpace(Container container, Level level) {
        if (!result.isItemEnabled(level.enabledFeatures())) return false;
        ItemStack output = container.getItem(WorkbenchMenu.RESULT_SLOT);
        int limit = Math.min(result.getMaxStackSize(), container.getMaxStackSize(result));
        return (output.isEmpty() || ItemStack.isSameItemSameComponents(output, result))
                && output.getCount() + result.getCount() <= limit;
    }

    public boolean canCraft(Container container, Level level) {
        return matches(new Input(container), level) && hasOutputSpace(container, level);
    }

    // Only called by the server ticker after validating the complete recipe.
    public void finishCraft(Container container) {
        for (var required : requiredCounts().entrySet()) {
            int remaining = required.getValue();
            for (int slot = 0; slot < WorkbenchMenu.INPUT_COUNT && remaining > 0; slot++) {
                ItemStack stack = container.getItem(slot);
                if (stack.is(required.getKey())) {
                    int taken = Math.min(remaining, stack.getCount());
                    container.removeItem(slot, taken);
                    remaining -= taken;
                }
            }
        }
        ItemStack output = container.getItem(WorkbenchMenu.RESULT_SLOT);
        if (output.isEmpty()) container.setItem(WorkbenchMenu.RESULT_SLOT, result.copy());
        else output.grow(result.getCount());
        container.setChanged();
    }

    @Override
    public boolean matches(Input input, Level level) {
        for (var required : requiredCounts().entrySet()) {
            int available = 0;
            for (int slot = 0; slot < input.size(); slot++) {
                ItemStack stack = input.getItem(slot);
                if (stack.is(required.getKey())) available += stack.getCount();
            }
            if (available < required.getValue()) return false;
        }
        return true;
    }

    @Override
    public ItemStack assemble(Input input, HolderLookup.Provider registries) {
        return result.copy();
    }

    @Override
    public ItemStack getResultItem(HolderLookup.Provider registries) {
        return result;
    }

    @Override
    public boolean canCraftInDimensions(int width, int height) {
        return width * height >= materials.size();
    }

    @Override
    public boolean isSpecial() {
        return true;
    }

    @Override
    public RecipeSerializer<?> getSerializer() {
        return ModRecipes.WORKBENCH_SERIALIZER.get();
    }

    @Override
    public RecipeType<?> getType() {
        return ModRecipes.WORKBENCH.get();
    }

    public static class Serializer implements RecipeSerializer<WorkbenchRecipe> {
        private static final MapCodec<WorkbenchRecipe> CODEC = RecordCodecBuilder.mapCodec(instance -> instance.group(
                ResourceLocation.CODEC.fieldOf("workstation").forGetter(WorkbenchRecipe::workstation),
                Material.CODEC.listOf(1, 24).fieldOf("ingredients").forGetter(WorkbenchRecipe::materials),
                ItemStack.STRICT_CODEC.fieldOf("result").forGetter(WorkbenchRecipe::result)
        ).apply(instance, WorkbenchRecipe::new));
        private static final StreamCodec<RegistryFriendlyByteBuf, WorkbenchRecipe> STREAM_CODEC = StreamCodec.composite(
                ResourceLocation.STREAM_CODEC, WorkbenchRecipe::workstation,
                Material.STREAM_CODEC.apply(ByteBufCodecs.list()), WorkbenchRecipe::materials,
                ItemStack.STREAM_CODEC, WorkbenchRecipe::result, WorkbenchRecipe::new);

        @Override
        public MapCodec<WorkbenchRecipe> codec() {
            return CODEC;
        }

        @Override
        public StreamCodec<RegistryFriendlyByteBuf, WorkbenchRecipe> streamCodec() {
            return STREAM_CODEC;
        }
    }
}
