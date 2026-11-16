package com.redcookies.archecraft.client;

import com.redcookies.archecraft.ArcheCraft;
import com.redcookies.archecraft.entity.SarraceniaEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;

public final class SarraceniaRenderer extends MobRenderer<SarraceniaEntity, SarraceniaModel> {
    private static final ResourceLocation TEXTURE =
            ResourceLocation.fromNamespaceAndPath(ArcheCraft.MODID, "textures/entity/sarracenia.png");

    public SarraceniaRenderer(EntityRendererProvider.Context context) {
        super(context, new SarraceniaModel(context.getResourceManager()), .6F);
    }

    @Override
    public ResourceLocation getTextureLocation(SarraceniaEntity entity) {
        return TEXTURE;
    }
}
