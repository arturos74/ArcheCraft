package com.redcookies.archecraft.entity;

import com.redcookies.archecraft.ArcheCraft;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.Difficulty;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.levelgen.structure.Structure;

/** Slow melee predator. Its only natural spawn source is the Hasla structure. */
public final class SarraceniaEntity extends Monster {
    public static final ResourceKey<Structure> HABITAT = ResourceKey.create(Registries.STRUCTURE,
            ResourceLocation.fromNamespaceAndPath(ArcheCraft.MODID, "abandoned_drill_camp"));
    private float previousWalkBlend;
    private float walkBlend;

    public SarraceniaEntity(EntityType<? extends SarraceniaEntity> type, Level level) {
        super(type, level);
        getNavigation().setCanFloat(true);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 20.0)
                .add(Attributes.MOVEMENT_SPEED, .18)
                .add(Attributes.ATTACK_DAMAGE, 4.0)
                .add(Attributes.FOLLOW_RANGE, 24.0)
                .add(Attributes.STEP_HEIGHT, 1.0);
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        // Pursuit and wandering use the same speed: there is no sprint/panic gait.
        goalSelector.addGoal(1, new MeleeAttackGoal(this, 1.0, false));
        goalSelector.addGoal(2, new WaterAvoidingRandomStrollGoal(this, 1.0));
        goalSelector.addGoal(3, new LookAtPlayerGoal(this, Player.class, 8.0F));
        goalSelector.addGoal(4, new RandomLookAroundGoal(this));
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
    }

    public static boolean checkSpawnRules(EntityType<SarraceniaEntity> type, ServerLevelAccessor level,
                                          MobSpawnType reason, BlockPos pos, RandomSource random) {
        if (level.getDifficulty() == Difficulty.PEACEFUL
                || !checkAnyLightMonsterSpawnRules(type, level, reason, pos, random)) return false;
        // Eggs, commands and mob spawners remain useful for building/testing.
        if (reason != MobSpawnType.NATURAL && reason != MobSpawnType.CHUNK_GENERATION) return true;
        return level.getLevel().structureManager()
                .getStructureWithPieceAt(pos, holder -> holder.is(HABITAT)).isValid();
    }

    @Override
    public float getWalkTargetValue(BlockPos pos, LevelReader level) {
        // This is a daytime swamp creature; do not prefer darkness like a zombie.
        return 0;
    }

    @Override
    public void tick() {
        double startX = getX(), startZ = getZ();
        super.tick();
        previousWalkBlend = walkBlend;
        double dx = getX() - startX, dz = getZ() - startZ;
        boolean walking = dx * dx + dz * dz > .000025 && !isPassenger() && !isDeadOrDying();
        walkBlend = Mth.clamp(walkBlend + (walking ? .2F : -.2F), 0, 1);
    }

    public float getWalkAnimationBlend(float partialTick) {
        return Mth.lerp(Mth.clamp(partialTick, 0, 1), previousWalkBlend, walkBlend);
    }
}
