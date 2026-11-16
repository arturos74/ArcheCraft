package com.redcookies.archecraft.client;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.redcookies.archecraft.ArcheCraft;
import com.redcookies.archecraft.entity.SarraceniaEntity;
import net.minecraft.client.model.EntityModel;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.util.Mth;
import org.joml.Quaternionf;

import java.io.IOException;
import java.io.Reader;
import java.util.ArrayList;
import java.util.List;

/** Cached saved Blockbench mesh with smoothly blended idle and walking clips. */
public final class SarraceniaModel extends EntityModel<SarraceniaEntity> {
    public static final ResourceLocation MESH = asset("entity/sarracenia_mesh.json");
    private static final ResourceLocation IDLE = asset("entity/sarracenia_idle.json");
    private static final ResourceLocation WALK = asset("entity/sarracenia_walk.json");
    private final List<Bone> bones = new ArrayList<>();
    private final List<Bone> roots = new ArrayList<>();
    private final float duration;
    private final float walkDuration;

    public SarraceniaModel(ResourceManager resources) {
        // Renderers are rebuilt on F3+T. Nothing is read or parsed during rendering.
        try {
            JsonObject mesh = read(resources, MESH);
            if (mesh.get("format_version").getAsInt() != 2) throw new IllegalArgumentException("Unsupported Sarracenia mesh");
            for (JsonElement element : mesh.getAsJsonArray("bones")) {
                JsonObject data = element.getAsJsonObject();
                Bone bone = new Bone(data.get("name").getAsString(), vector(data.getAsJsonArray("pivot")),
                        vector(data.getAsJsonArray("rotation")));
                int parent = data.get("parent").getAsInt();
                if (parent == -1) roots.add(bone);
                else {
                    if (parent < 0 || parent >= bones.size()) throw new IllegalArgumentException("Invalid bone parent");
                    bones.get(parent).children.add(bone);
                }
                bones.add(bone);
            }
            for (JsonElement element : mesh.getAsJsonArray("quads")) {
                JsonObject quad = element.getAsJsonObject();
                bones.get(quad.get("bone").getAsInt()).quads.add(readQuad(quad));
            }
            if (bones.isEmpty()) throw new IllegalArgumentException("Empty Sarracenia rig");
            JsonObject idle = read(resources, IDLE);
            duration = finite(idle.get("duration").getAsFloat());
            if (duration <= 0) throw new IllegalArgumentException("Invalid idle duration");
            JsonObject tracks = idle.getAsJsonObject("tracks");
            for (String name : tracks.keySet()) {
                Bone bone = bones.stream().filter(b -> b.name.equals(name)).findFirst().orElseThrow();
                JsonObject channels = tracks.getAsJsonObject(name);
                bone.rotation = track(channels, "rotation", duration);
                bone.position = track(channels, "position", duration);
                bone.scale = track(channels, "scale", duration);
            }
            JsonObject walk = read(resources, WALK);
            walkDuration = finite(walk.get("duration").getAsFloat());
            if (walkDuration <= 0) throw new IllegalArgumentException("Invalid walk duration");
            JsonObject walkTracks = walk.getAsJsonObject("tracks");
            for (String name : walkTracks.keySet()) {
                Bone bone = bones.stream().filter(b -> b.name.equals(name)).findFirst().orElseThrow();
                JsonObject channels = walkTracks.getAsJsonObject(name);
                bone.walkRotation = track(channels, "rotation", walkDuration);
                bone.walkPosition = track(channels, "position", walkDuration);
                bone.walkScale = track(channels, "scale", walkDuration);
            }
        } catch (IOException | RuntimeException exception) {
            throw new IllegalStateException("Unable to load the Sarracenia rig/animations", exception);
        }
    }

    @Override
    public void setupAnim(SarraceniaEntity entity, float limbSwing, float limbSwingAmount,
                          float ageInTicks, float netHeadYaw, float headPitch) {
        float seconds = ageInTicks / 20.0F + Math.floorMod(entity.getUUID().hashCode(), 97) * .071F;
        float walkWeight = entity.isDeadOrDying() || entity.isPassenger() ? 0
                : entity.getWalkAnimationBlend(ageInTicks - entity.tickCount);
        applyIdle(seconds, 1 - walkWeight);
        applyWalk(seconds, walkWeight);
    }

    private void applyIdle(float seconds, float weight) {
        float time = seconds % duration;
        if (time < 0) time += duration;
        for (Bone bone : bones) {
            // Every channel is reset for every entity, including unanimated bones.
            bone.sample(bone.rotation, time, weight, 0, 0);
            bone.sample(bone.position, time, weight, 3, 0);
            bone.sample(bone.scale, time, weight, 6, 1);
        }
    }

    private void applyWalk(float seconds, float weight) {
        if (weight <= 0) return;
        float time = seconds % walkDuration;
        if (time < 0) time += walkDuration;
        for (Bone bone : bones) {
            bone.addMovement(bone.walkRotation, bone.walkPosition, bone.walkScale, time, weight);
        }
    }

    @Override
    public void renderToBuffer(PoseStack stack, VertexConsumer buffer, int light, int overlay, int color) {
        for (Bone bone : roots) renderBone(bone, stack, buffer, light, overlay, color);
    }

    private void renderBone(Bone bone, PoseStack stack, VertexConsumer buffer, int light, int overlay, int color) {
        stack.pushPose();
        float[] p = bone.pose;
        stack.translate(bone.pivot[0] + p[3], bone.pivot[1] + p[4], bone.pivot[2] + p[5]);
        stack.mulPose(bone.quaternion.rotationZYX((bone.rest[2] + p[2]) * Mth.DEG_TO_RAD,
                (bone.rest[1] + p[1]) * Mth.DEG_TO_RAD, (bone.rest[0] + p[0]) * Mth.DEG_TO_RAD));
        if (p[6] != 1 || p[7] != 1 || p[8] != 1) stack.scale(p[6], p[7], p[8]);
        PoseStack.Pose pose = stack.last();
        for (Quad quad : bone.quads) {
            for (int vertex = 0; vertex < 4; vertex++) {
                int offset = vertex * 5;
                buffer.addVertex(pose, quad.vertices[offset], quad.vertices[offset + 1], quad.vertices[offset + 2])
                        .setColor(color).setUv(quad.vertices[offset + 3], quad.vertices[offset + 4])
                        .setOverlay(overlay).setLight(light).setNormal(pose, quad.nx, quad.ny, quad.nz);
            }
        }
        for (Bone child : bone.children) renderBone(child, stack, buffer, light, overlay, color);
        stack.popPose();
    }

    private static ResourceLocation asset(String path) { return ResourceLocation.fromNamespaceAndPath(ArcheCraft.MODID, path); }
    private static JsonObject read(ResourceManager resources, ResourceLocation path) throws IOException {
        try (Reader reader = resources.openAsReader(path)) { return JsonParser.parseReader(reader).getAsJsonObject(); }
    }
    private static float finite(float value) {
        if (!Float.isFinite(value)) throw new IllegalArgumentException("Non-finite Sarracenia value");
        return value;
    }
    private static Quad readQuad(JsonObject quad) {
        float[] normal = vector(quad.getAsJsonArray("normal"));
        JsonArray vertices = quad.getAsJsonArray("vertices");
        if (vertices.size() != 4) throw new IllegalArgumentException("Invalid Sarracenia quad");
        float[] data = new float[20];
        for (int vertex = 0; vertex < 4; vertex++) {
            JsonArray values = vertices.get(vertex).getAsJsonArray();
            if (values.size() != 5) throw new IllegalArgumentException("Invalid Sarracenia vertex");
            for (int component = 0; component < 5; component++) {
                data[vertex * 5 + component] = finite(values.get(component).getAsFloat());
            }
        }
        return new Quad(data, normal[0], normal[1], normal[2]);
    }
    private static float[] vector(JsonArray values) {
        if (values.size() != 3) throw new IllegalArgumentException("Expected three components");
        return new float[]{finite(values.get(0).getAsFloat()), finite(values.get(1).getAsFloat()), finite(values.get(2).getAsFloat())};
    }
    private static Track track(JsonObject channels, String channel, float duration) {
        if (!channels.has(channel)) return null;
        JsonArray keys = channels.getAsJsonArray(channel);
        if (keys.isEmpty()) throw new IllegalArgumentException("Empty Sarracenia track");
        float[] times = new float[keys.size()];
        float[][] values = new float[keys.size()][];
        boolean[] steps = new boolean[keys.size()];
        for (int i = 0; i < keys.size(); i++) {
            JsonObject key = keys.get(i).getAsJsonObject();
            times[i] = finite(key.get("time").getAsFloat());
            if (times[i] < 0 || times[i] > duration || (i > 0 && times[i] <= times[i - 1]))
                throw new IllegalArgumentException("Unordered Sarracenia key times");
            values[i] = vector(key.getAsJsonArray("value"));
            steps[i] = key.get("step").getAsBoolean();
        }
        return new Track(times, values, steps);
    }

    private static final class Bone {
        final String name;
        final float[] pivot, rest;
        final float[] pose = {0, 0, 0, 0, 0, 0, 1, 1, 1};
        final float[] movementPose = new float[9];
        final Quaternionf quaternion = new Quaternionf();
        final List<Bone> children = new ArrayList<>();
        final List<Quad> quads = new ArrayList<>();
        Track rotation, position, scale;
        Track walkRotation, walkPosition, walkScale;
        Bone(String name, float[] pivot, float[] rest) { this.name = name; this.pivot = pivot; this.rest = rest; }
        void addMovement(Track rotation, Track position, Track scale, float time, float weight) {
            sampleTo(movementPose, rotation, time, 1, 0, 0);
            sampleTo(movementPose, position, time, 1, 3, 0);
            sampleTo(movementPose, scale, time, 1, 6, 1);
            for (int component = 0; component < 9; component++) {
                float neutral = component >= 6 ? 1 : 0;
                pose[component] += (movementPose[component] - neutral) * weight;
            }
        }
        void sample(Track track, float time, float weight, int offset, float neutral) {
            sampleTo(pose, track, time, weight, offset, neutral);
        }
        void sampleTo(float[] target, Track track, float time, float weight, int offset, float neutral) {
            if (track == null || weight == 0) {
                for (int axis = 0; axis < 3; axis++) target[offset + axis] = neutral;
                return;
            }
            int low = 0, high = track.times.length - 1;
            while (low < high) {
                int mid = (low + high + 1) >>> 1;
                if (track.times[mid] <= time) low = mid; else high = mid - 1;
            }
            int next = Math.min(low + 1, track.times.length - 1);
            float blend = next == low || time <= track.times[low] || track.steps[low] ? 0
                    : (time - track.times[low]) / (track.times[next] - track.times[low]);
            for (int axis = 0; axis < 3; axis++) {
                float value = Mth.lerp(blend, track.values[low][axis], track.values[next][axis]);
                target[offset + axis] = neutral + (value - neutral) * weight;
            }
        }
    }
    private record Track(float[] times, float[][] values, boolean[] steps) {}
    private record Quad(float[] vertices, float nx, float ny, float nz) {}
}
