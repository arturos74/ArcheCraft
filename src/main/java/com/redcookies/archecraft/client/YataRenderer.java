package com.redcookies.archecraft.client;

import com.redcookies.archecraft.ArcheCraft;
import com.redcookies.archecraft.entity.YataEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import com.mojang.blaze3d.vertex.PoseStack;

public final class YataRenderer extends MobRenderer<YataEntity, YataModel> {
    private static final ResourceLocation TEXTURE =
            ResourceLocation.fromNamespaceAndPath(ArcheCraft.MODID, "textures/entity/yata.png");
    private static final ResourceLocation MALE_TEXTURE =
            ResourceLocation.fromNamespaceAndPath(ArcheCraft.MODID, "textures/entity/yata_male.png");
    private static final ResourceLocation BLACK_TEXTURE =
            ResourceLocation.fromNamespaceAndPath(ArcheCraft.MODID, "textures/entity/yata_black.png");
    private static final ResourceLocation PALOMINO_TEXTURE =
            ResourceLocation.fromNamespaceAndPath(ArcheCraft.MODID, "textures/entity/yata_palomino.png");
    private static final ResourceLocation ALBINO_TEXTURE =
            ResourceLocation.fromNamespaceAndPath(ArcheCraft.MODID, "textures/entity/yata_albino.png");

    public YataRenderer(EntityRendererProvider.Context context) {
        super(context, new YataModel(context.getResourceManager()), 0.7F);
        addLayer(new YataSaddleLayer(this));
    }

    @Override
    public ResourceLocation getTextureLocation(YataEntity entity) {
        return entity.isBlackVariant() ? BLACK_TEXTURE : entity.isPalominoVariant() ? PALOMINO_TEXTURE
                : entity.isAlbinoVariant() ? ALBINO_TEXTURE
                : entity.isMale() ? MALE_TEXTURE : TEXTURE;
    }

    @Override
    protected void scale(YataEntity entity, PoseStack stack, float partialTick) {
        float size = entity.getAgeScale();
        stack.scale(size, size, size);
    }

    @Override
    protected float getShadowRadius(YataEntity entity) {
        return super.getShadowRadius(entity) * entity.getAgeScale();
    }
}
