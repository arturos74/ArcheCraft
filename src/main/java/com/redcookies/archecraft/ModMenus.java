package com.redcookies.archecraft;

import com.redcookies.archecraft.workbench.WorkbenchMenu;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.inventory.MenuType;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.common.extensions.IMenuTypeExtension;

public final class ModMenus {
    public static final DeferredRegister<MenuType<?>> MENUS =
            DeferredRegister.create(Registries.MENU, ArcheCraft.MODID);
    public static final DeferredHolder<MenuType<?>, MenuType<WorkbenchMenu>> WORKBENCH =
            MENUS.register("workbench", () -> IMenuTypeExtension.create(
                    (id, inventory, data) -> new WorkbenchMenu(id, inventory, data.readResourceLocation())));

    public static void register(IEventBus bus) {
        MENUS.register(bus);
    }
}
