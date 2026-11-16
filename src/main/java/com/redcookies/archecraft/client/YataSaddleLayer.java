package com.redcookies.archecraft.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.redcookies.archecraft.ArcheCraft;
import com.redcookies.archecraft.entity.YataEntity;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;

/** The saddle uses the parent's current animated bone transforms. */
public final class YataSaddleLayer extends RenderLayer<YataEntity, YataModel> {
    private static final ResourceLocation TEXTURE =
            ResourceLocation.fromNamespaceAndPath(ArcheCraft.MODID, "textures/entity/yata_saddle.png");

    public YataSaddleLayer(RenderLayerParent<YataEntity, YataModel> parent) {
        super(parent);
    }

    @Override
    public void render(PoseStack stack, MultiBufferSource buffers, int light, YataEntity yata,
                       float limbSwing, float limbSwingAmount, float partialTick, float ageInTicks,
                       float netHeadYaw, float headPitch) {
        if (yata.isSaddled() && !yata.isInvisible()) {
            getParentModel().renderSaddle(stack, buffers.getBuffer(RenderType.entityCutoutNoCull(TEXTURE)),
                    light, OverlayTexture.NO_OVERLAY);
        }
    }
}
