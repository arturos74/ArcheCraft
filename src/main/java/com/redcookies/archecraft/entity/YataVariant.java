package com.redcookies.archecraft.entity;

/** Stable network IDs and save names; unknown values load as the ordinary coat. */
public enum YataVariant {
    NORMAL(0, "normal"),
    BLACK(1, "black"),
    PALOMINO(2, "palomino"),
    ALBINO(3, "albino");

    private final int id;
    private final String saveName;

    YataVariant(int id, String saveName) { this.id = id; this.saveName = saveName; }
    public int id() { return id; }
    public String saveName() { return saveName; }
    public static YataVariant byId(int id) {
        return id == BLACK.id ? BLACK : id == PALOMINO.id ? PALOMINO
                : id == ALBINO.id ? ALBINO : NORMAL;
    }
    public static YataVariant byName(String name) {
        return BLACK.saveName.equalsIgnoreCase(name) ? BLACK
                : PALOMINO.saveName.equalsIgnoreCase(name) ? PALOMINO
                : ALBINO.saveName.equalsIgnoreCase(name) ? ALBINO : NORMAL;
    }
}
