package com.redcookies.archecraft.entity;

import com.redcookies.archecraft.ModEntities;
import com.redcookies.archecraft.ModItems;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.AgeableMob;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.animal.horse.AbstractHorse;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.BreedGoal;
import net.minecraft.world.entity.ai.goal.FollowParentGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.PanicGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.RunAroundLikeCrazyGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.tags.BlockTags;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.util.Mth;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;
import javax.annotation.Nullable;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.SpawnGroupData;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.level.ServerLevelAccessor;

public class YataEntity extends AbstractHorse {
    private static final EntityDataAccessor<Boolean> PANICKING =
            SynchedEntityData.defineId(YataEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Boolean> MALE =
            SynchedEntityData.defineId(YataEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Integer> VARIANT =
            SynchedEntityData.defineId(YataEntity.class, EntityDataSerializers.INT);
    private boolean sexAssigned;
    private float previousRunBlend;
    private float runBlend;
    private float previousWalkBlend;
    private float walkBlend;
    private float previousRiddenWalkBlend;
    private float riddenWalkBlend;
    private boolean riddenSprintActive;

    public YataEntity(EntityType<? extends YataEntity> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return createBaseHorseAttributes()
                .add(Attributes.MAX_HEALTH, 24.0)
                .add(Attributes.MOVEMENT_SPEED, 0.22)
                .add(Attributes.FOLLOW_RANGE, 16.0)
                .add(Attributes.STEP_HEIGHT, 1.0);
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(1, new PanicGoal(this, 1.4) {
            @Override
            public void start() {
                super.start();
                entityData.set(PANICKING, true);
            }

            @Override
            public void stop() {
                super.stop();
                entityData.set(PANICKING, false);
            }
        });
        // Vanilla horse temper checks, failed-attempt smoke/ejection and success hearts.
        goalSelector.addGoal(2, new RunAroundLikeCrazyGoal(this, 1.2));
        goalSelector.addGoal(3, new BreedGoal(this, 1.0, YataEntity.class));
        goalSelector.addGoal(4, new FollowParentGoal(this, 1.0));
        goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, 1.0));
        goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 8.0F));
        goalSelector.addGoal(7, new RandomLookAroundGoal(this));
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(PANICKING, false);
        builder.define(MALE, false);
        builder.define(VARIANT, YataVariant.NORMAL.id());
    }

    public boolean isPanicking() {
        return entityData.get(PANICKING);
    }

    public boolean isMale() {
        return !isPalominoVariant() && !isAlbinoVariant() && (isBlackVariant() || entityData.get(MALE));
    }

    public void setMale(boolean male) {
        sexAssigned = true;
        entityData.set(MALE, !isPalominoVariant() && !isAlbinoVariant() && (male || isBlackVariant()));
    }

    public YataVariant getVariant() {
        return YataVariant.byId(entityData.get(VARIANT));
    }

    public boolean isBlackVariant() {
        return getVariant() == YataVariant.BLACK;
    }

    public boolean isPalominoVariant() {
        return getVariant() == YataVariant.PALOMINO;
    }

    public boolean isAlbinoVariant() {
        return getVariant() == YataVariant.ALBINO;
    }

    public void setVariant(YataVariant variant) {
        entityData.set(VARIANT, variant.id());
        if (variant == YataVariant.BLACK) setMale(true);
        else if (variant == YataVariant.PALOMINO || variant == YataVariant.ALBINO) setMale(false);
    }

    @Override
    public float getAgeScale() {
        return super.getAgeScale() * (getVariant() != YataVariant.NORMAL ? 1.3F : isMale() ? 1.1F : 1.0F);
    }

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> key) {
        super.onSyncedDataUpdated(key);
        if (MALE.equals(key) || VARIANT.equals(key)) refreshDimensions();
    }

    @Override
    protected Component getTypeName() {
        return Component.translatable(isBlackVariant() ? "entity.archecraft.yata.black_male"
                : isPalominoVariant() ? "entity.archecraft.yata.palomino_female"
                : isAlbinoVariant() ? "entity.archecraft.yata.albino_female"
                : isMale() ? "entity.archecraft.yata.male" : "entity.archecraft.yata.female");
    }

    @Nullable
    @Override
    public SpawnGroupData finalizeSpawn(ServerLevelAccessor level, DifficultyInstance difficulty,
                                       MobSpawnType reason, @Nullable SpawnGroupData groupData) {
        SpawnGroupData result = super.finalizeSpawn(level, difficulty, reason, groupData);
        if (!sexAssigned) setMale(level.getRandom().nextBoolean());
        return result;
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putBoolean("Male", isMale());
        tag.putString("Variant", getVariant().saveName());
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        // Existing Yatas retain the original female model when upgrading a save.
        setVariant(YataVariant.byName(tag.getString("Variant")));
        setMale(tag.getBoolean("Male"));
    }

    @Override
    public InteractionResult mobInteract(Player player, InteractionHand hand) {
        ItemStack held = player.getItemInHand(hand);
        if (held.is(ModItems.CLOVER.get())) {
            if (!level().isClientSide) {
                if (isBaby() && isTamed()) {
                    held.consume(1, player);
                    ageUp(getSpeedUpSecondsWhenFeeding(-getAge()), true);
                } else if (canBreedNow() && canFallInLove()) {
                    held.consume(1, player);
                    setInLove(player);
                }
            }
            return InteractionResult.sidedSuccess(level().isClientSide);
        }
        if (player.isSecondaryUseActive() && held.isEmpty() && !level().isClientSide) {
            player.displayClientMessage(Component.translatable("message.archecraft.yata.sex",
                    getTypeName()), true);
        }
        if (player.isSecondaryUseActive() && held.isEmpty() && !isTamed()) {
            return InteractionResult.sidedSuccess(level().isClientSide);
        }
        // Match Horse's food/empty-hand taming interaction, then delegate saddle,
        // mounting and the saddle inventory to AbstractHorse.
        if (!isVehicle() && !(isTamed() && !isBaby() && player.isSecondaryUseActive())) {
            ItemStack stack = player.getItemInHand(hand);
            if (!stack.isEmpty()) {
                if (isFood(stack)) return fedFood(player, stack);
                if (!isTamed()) {
                    makeMad();
                    return InteractionResult.sidedSuccess(level().isClientSide);
                }
            }
        }
        return super.mobInteract(player, hand);
    }

    @Nullable
    @Override
    public LivingEntity getControllingPassenger() {
        return isTamed() ? super.getControllingPassenger() : null;
    }

    @Override
    public boolean canSprint() {
        // LocalPlayer uses this to enable its ordinary sprint key while mounted;
        // the normal player sprint packet also reaches the server.
        return isTamed() && isSaddled() && isAlive();
    }

    @Override
    protected void tickRidden(Player player, Vec3 input) {
        super.tickRidden(player, input);
        riddenSprintActive = player.isSprinting() && input.z > 0 && !isInWaterOrBubble();
        // Vanilla sprinting supplies the 30% speed bonus and synced sprint flag.
        setSprinting(riddenSprintActive);
    }

    @Override
    protected Vec3 getPassengerAttachmentPoint(Entity passenger, EntityDimensions dimensions, float partialTick) {
        // Authored rider_seat = (0, 22.35486, 4.25). The entity renderer turns
        // model -Z forward, so the seat's positive model Z is behind the rider.
        float size = getScale() * getAgeScale();
        return new Vec3(0, 1.42 * size, -0.265625 * size)
                .yRot(-getYRot() * Mth.DEG_TO_RAD);
    }

    @Override
    protected boolean canPerformRearing() {
        return false;
    }

    @Override
    public boolean canEatGrass() {
        return false;
    }

    @Override
    protected void playStepSound(BlockPos pos, BlockState block) {
        // Match Player's terrain footsteps instead of AbstractHorse's hoof sounds.
        if (isInWater()) {
            waterSwimSound();
            playMuffledStepSound(block, pos);
            return;
        }
        BlockPos primaryPos = getPrimaryStepSoundBlockPos(pos);
        BlockState primary = primaryPos.equals(pos) ? block : level().getBlockState(primaryPos);
        if (!primaryPos.equals(pos) && primary.is(BlockTags.COMBINATION_STEP_SOUND_BLOCKS)) {
            playCombinationStepSounds(primary, block, primaryPos, pos);
            return;
        }
        SoundType sound = primary.getSoundType(level(), primaryPos, this);
        playSound(sound.getStepSound(), sound.getVolume() * 0.15F, sound.getPitch());
    }

    @Override
    public void playSound(SoundEvent sound, float volume, float pitch) {
        // AbstractHorse plays these directly during jump takeoff and landing.
        if (sound == SoundEvents.HORSE_JUMP) return;
        if (sound == SoundEvents.HORSE_LAND) {
            BlockPos pos = getOnPos();
            BlockState block = level().getBlockState(pos);
            if (!block.isAir()) playStepSound(pos, block);
            return;
        }
        super.playSound(sound, volume, pitch);
    }

    @Nullable
    @Override
    public AgeableMob getBreedOffspring(ServerLevel level, AgeableMob otherParent) {
        if (!(otherParent instanceof YataEntity mate) || !canMate(mate)) return null;
        YataEntity child = ModEntities.YATA.get().create(level);
        if (child == null) return null;
        child.setMale(getRandom().nextBoolean());
        // Mutually exclusive 5% black, 5% palomino, 1% albino; ordinary births retain the sex roll.
        int coatRoll = getRandom().nextInt(100);
        if (coatRoll < 5) child.setVariant(YataVariant.BLACK);
        else if (coatRoll < 10) child.setVariant(YataVariant.PALOMINO);
        else if (coatRoll == 10) child.setVariant(YataVariant.ALBINO);
        child.setBaby(true);
        child.setTamed(true);
        YataEntity mother = isMale() ? mate : this;
        YataEntity father = isMale() ? this : mate;
        child.setOwnerUUID(mother.getOwnerUUID() != null ? mother.getOwnerUUID() : father.getOwnerUUID());
        return child;
    }

    private boolean canBreedNow() {
        return isAlive() && isTamed() && getAge() == 0 && !isVehicle() && !isPassenger() && !isPanicking();
    }

    @Override
    public boolean canFallInLove() {
        return canBreedNow() && super.canFallInLove();
    }

    @Override
    public boolean canMate(Animal other) {
        return other != this && other instanceof YataEntity mate && isMale() != mate.isMale()
                && canBreedNow() && mate.canBreedNow() && isInLove() && mate.isInLove();
    }

    @Override
    public void spawnChildFromBreeding(ServerLevel level, Animal mate) {
        if (canMate(mate)) super.spawnChildFromBreeding(level, mate);
    }

    @Override
    public void tick() {
        if (riddenSprintActive && getControllingPassenger() == null) {
            setSprinting(false);
            riddenSprintActive = false;
        }
        double startX = getX(), startZ = getZ();
        super.tick();
        previousRunBlend = runBlend;
        previousWalkBlend = walkBlend;
        previousRiddenWalkBlend = riddenWalkBlend;
        // Actual movement gates the run: damage/knockback by itself is not a gait.
        // Ridden sprinting and wild panic share the run clip.
        double movedX = getX() - startX, movedZ = getZ() - startZ;
        boolean moving = movedX * movedX + movedZ * movedZ > 0.0001
                && !isInWaterOrBubble() && !isPassenger() && !isDeadOrDying();
        boolean running = moving && (isPanicking() || isSprinting() || (!isTamed() && isVehicle()));
        boolean riddenWalking = moving && !running && getControllingPassenger() instanceof Player;
        runBlend = Mth.clamp(runBlend + (running ? 0.2F : -0.2F), 0, 1);
        walkBlend = Mth.clamp(walkBlend + (moving && !running && !riddenWalking ? 0.2F : -0.2F), 0, 1);
        riddenWalkBlend = Mth.clamp(riddenWalkBlend + (riddenWalking ? 0.2F : -0.2F), 0, 1);
    }

    public float getRunAnimationBlend(float partialTick) {
        return Mth.lerp(Mth.clamp(partialTick, 0, 1), previousRunBlend, runBlend);
    }

    public float getWalkAnimationBlend(float partialTick) {
        return Mth.lerp(Mth.clamp(partialTick, 0, 1), previousWalkBlend, walkBlend);
    }

    public float getRiddenWalkAnimationBlend(float partialTick) {
        return Mth.lerp(Mth.clamp(partialTick, 0, 1), previousRiddenWalkBlend, riddenWalkBlend);
    }

    @Override
    public boolean removeWhenFarAway(double distanceToClosestPlayer) {
        return false;
    }
}
