package com.redcookies.archecraft.worldgen;

import com.mojang.serialization.MapCodec;
import com.redcookies.archecraft.ModStructures;
import java.util.List;
import java.util.Optional;
import java.util.OptionalInt;
import net.minecraft.core.BlockPos;
import net.minecraft.core.QuartPos;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.levelgen.structure.pieces.PiecesContainer;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructurePiece;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.PoolElementStructurePiece;
import net.minecraft.world.level.levelgen.structure.pools.JigsawJunction;
import net.minecraft.world.level.levelgen.structure.structures.JigsawStructure;

/** Validates the complete rigid swamp site before any chunks are modified. */
public final class HaslaSwampStructure extends Structure {
    // Keep the existing jigsaw JSON fields and native four-piece assembly.
    public static final MapCodec<HaslaSwampStructure> CODEC =
            JigsawStructure.CODEC.xmap(HaslaSwampStructure::new, structure -> structure.layout);
    private static final int SITE_WIDTH = 96;
    private static final int SITE_HEIGHT = 36;
    private static final int EDGE_MARGIN = 8;
    private static final int SAMPLE_STEP = 8;
    private static final int MAX_HEIGHT_DIFFERENCE = 5;
    private static final int MAX_FOOTING_DEPTH = 8;
    // Six authored terrain layers put local water Y=5 immediately below surface Y.
    private static final int FOUNDATION_DEPTH = 6;
    private final JigsawStructure layout;

    public HaslaSwampStructure(JigsawStructure layout) {
        super(layout.modifiableStructureInfo().getOriginalStructureInfo().structureSettings());
        this.layout = layout;
    }

    @Override
    public Optional<GenerationStub> findGenerationPoint(GenerationContext context) {
        Optional<GenerationStub> assembled = layout.findGenerationPoint(context);
        if (assembled.isEmpty()) return Optional.empty();
        List<StructurePiece> pieces = assembled.get().getPiecesBuilder().build().pieces();
        if (pieces.size() != 4) return Optional.empty();
        BoundingBox footprint = BoundingBox.encapsulatingBoxes(
                pieces.stream().map(StructurePiece::getBoundingBox).toList()).orElseThrow();
        if (footprint.getXSpan() != SITE_WIDTH || footprint.getZSpan() != SITE_WIDTH) return Optional.empty();
        OptionalInt base = findSupportedBase(context, footprint);
        if (base.isEmpty()) return Optional.empty();
        int shiftY = base.getAsInt() - footprint.minY();
        pieces.forEach(piece -> {
            piece.move(0, shiftY, 0);
            if (shiftY != 0 && piece instanceof PoolElementStructurePiece poolPiece) {
                // Piece.move does not move the absolute heights used by Beardifier.
                poolPiece.getJunctions().replaceAll(junction -> new JigsawJunction(
                        junction.getSourceX(), junction.getSourceGroundY() + shiftY,
                        junction.getSourceZ(), junction.getDeltaY(), junction.getDestProjection()));
            }
        });
        BlockPos anchor = assembled.get().position().offset(0, shiftY, 0);
        return Optional.of(new GenerationStub(anchor, builder -> pieces.forEach(builder::addPiece)));
    }

    private OptionalInt findSupportedBase(GenerationContext context, BoundingBox footprint) {
        int minX = footprint.minX() - EDGE_MARGIN;
        int minZ = footprint.minZ() - EDGE_MARGIN;
        // Include the far edge exactly, rather than leaving an unsampled strip.
        int maxX = footprint.maxX() + EDGE_MARGIN + 1;
        int maxZ = footprint.maxZ() + EDGE_MARGIN + 1;
        var generator = context.chunkGenerator();
        var randomState = context.randomState();
        var height = context.heightAccessor();
        int lowest = Integer.MAX_VALUE;
        int highest = Integer.MIN_VALUE;

        // Base terrain queries do not load neighboring chunks or count tree canopies.
        for (int x = minX; x <= maxX; x += SAMPLE_STEP) {
            for (int z = minZ; z <= maxZ; z += SAMPLE_STEP) {
                int surface = generator.getFirstFreeHeight(x, z, Heightmap.Types.WORLD_SURFACE_WG, height, randomState);
                var biome = generator.getBiomeSource().getNoiseBiome(
                        QuartPos.fromBlock(x), QuartPos.fromBlock(surface), QuartPos.fromBlock(z), randomState.sampler());
                if (!biomes().contains(biome) || !context.validBiome().test(biome)) return OptionalInt.empty();
                lowest = Math.min(lowest, surface);
                highest = Math.max(highest, surface);
                if (highest - lowest > MAX_HEIGHT_DIFFERENCE) return OptionalInt.empty();
            }
        }
        int base = lowest - FOUNDATION_DEPTH;
        if (base <= height.getMinBuildHeight() || base + SITE_HEIGHT > height.getMaxBuildHeight()) return OptionalInt.empty();
        for (int x = minX; x <= maxX; x += SAMPLE_STEP) {
            for (int z = minZ; z <= maxZ; z += SAMPLE_STEP) {
                var column = generator.getBaseColumn(x, z, height, randomState);
                boolean supported = false;
                for (int y = base - 1; y >= base - MAX_FOOTING_DEPTH; y--) {
                    var support = column.getBlock(y);
                    if (support.blocksMotion() && support.getFluidState().isEmpty()) {
                        supported = true;
                        break;
                    }
                }
                if (!supported) return OptionalInt.empty();
            }
        }
        return OptionalInt.of(base);
    }

    @Override
    public void afterPlace(WorldGenLevel level, StructureManager structures, ChunkGenerator generator,
                           RandomSource random, BoundingBox chunkBounds, ChunkPos chunk, PiecesContainer pieces) {
        // Fill only the current chunk. Native terrain adaptation blends the rim;
        // these short footings close water pockets and cavities under the floor.
        for (StructurePiece piece : pieces.pieces()) {
            BoundingBox box = piece.getBoundingBox();
            int minX = Math.max(box.minX(), chunk.getMinBlockX());
            int maxX = Math.min(box.maxX(), chunk.getMaxBlockX());
            int minZ = Math.max(box.minZ(), chunk.getMinBlockZ());
            int maxZ = Math.min(box.maxZ(), chunk.getMaxBlockZ());
            for (int x = minX; x <= maxX; x++) {
                for (int z = minZ; z <= maxZ; z++) {
                    if (!level.getBlockState(new BlockPos(x, box.minY(), z)).blocksMotion()) continue;
                    for (int y = box.minY() - 1; y >= box.minY() - MAX_FOOTING_DEPTH && y >= level.getMinBuildHeight(); y--) {
                        BlockPos pos = new BlockPos(x, y, z);
                        var ground = level.getBlockState(pos);
                        if (ground.blocksMotion() && ground.getFluidState().isEmpty()) break;
                        level.setBlock(pos, Blocks.STONE.defaultBlockState(), 18);
                    }
                }
            }
        }
    }

    @Override
    public StructureType<?> type() {
        return ModStructures.HASLA_SWAMP.get();
    }
}
