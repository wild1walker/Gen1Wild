# Wild Green

**This is, I think, the definitive way to play Red.**

Every quality-of-life and visual upgrade in the Gen1Wild suite, in one cart —
and only the ones that still feel like Red. That was the whole filter.
Sprinting, autosave, a Pokédex worth opening, a bag with pockets, battle
backdrops, animated Crystal sprites, followers behind you: none of it turns
this into a different game. It is the game you remember, with the parts that
made you put it down taken out.

**And you can catch every single one of them.** All 151, in one save, on one
version, without trading — the legendaries retryable until you land them, the
trade evolutions handled by an item, Mew behind the Mansion journals where it
always should have been. Every vanilla encounter still behaves exactly as
vanilla does; the missing species are placed around them, not on top of them.

So if you are going for a 100% Kanto dex, or you just want Red to feel like a
game made this decade, Wild Green is the most enjoyable way to do it.

It is a **custom cart**: a named, version-pinned set of mods that plays as its
own game, with its own entry in the launcher, its own cartridge, and its own
save slots. Two people running Wild Green run the same mods at the same builds.

| Pinned | |
|---|---|
| **Gen1WildQOL** | The quality-of-life half of the suite: sprinting, autosave, auto continue, sound, followers, all 151, EXP share, move reminder, menu layout, the mod manager and four later-generation conveniences |
| **Crystal Animated Sprites with Shiny Visuals** | Crystal animated battle sprites, Gen 2-style shiny reveals with the cry held until the sparkle finishes, and swappable trainer portraits. Somebody else's mod, pinned unmodified |
| **Gen1WildUI** | The visual half: battle backdrops, the battle intro, the battle menus, the Pokédex, the box, the party menu, the bag, item icons and descriptions, the lift panel |
| **Wild Green** | The version itself: the player in green, and `WILD GREEN VERSION` on the title screen |

The exact build of each is on this card, above, and in the cart's own
`cart.json` — not written out here, where it would go stale the first time the
cart re-pins anything.

## What makes it a version

`Wild Green` — the mod written for this cart — turns the player green and
retitles the game. The overworld walker, the `BICYCLE` sheet, the battle back
pic, the front pic that Oak's intro and the trainer card and the Hall of Fame
share, and the standing figure on the title screen all get the same recolor.

None of that art ships. It is derived from Red's own, so it travels as a
recipe and the pixels come from **your** imported cache — which is also what
makes the switch back real: the recolor is written alongside the vanilla art
rather than over it, so `PLAYER = RED` gives you the original character with
nothing to reinstall.

The title ribbon is drawn from scratch on the four grey shades the importer
writes, and the `LOGO1` palette the ribbon band wears is overridden to the
cart's own green. Under the `OG RED` and `ADVANCED` colour modes that band
comes from elsewhere and keeps its own colour, so there the lettering still
says `WILD GREEN VERSION` but is drawn in red.

## The seal

`sealed+`. The mod set is fixed — you cannot add to it — but any of the four
can be switched off from inside the cart, and switching one does not break the
seal. Every feature in both bundles already switches on and off by itself, so
a cart that could not be taken apart would be a cart you could not play your
own way.

`TITLE RIBBON` is frozen on: it is the cart's name. `PLAYER` deliberately is
not, so `GREEN` or `RED` stays yours to choose.

## Saves

A cart's saves are its own — the engine routes its slots to `cart_wild_green`,
so nothing here writes into your base Red slots. Text speed, battle
animations, battle style, the ruleset and the speed multipliers follow the
cart while it runs; audio, video mode, key bindings and language stay global.

## Installing it

Install from this card, or download the `.g1rcart` from
[the cart's releases](https://github.com/wild1walker/Gen1WildGreen/releases)
and open it from **Custom Carts > Import a cart**.

If a pinned mod is missing, the cart's own page offers **Install required
mods**: it resolves each pin to its release, checks the archive against the
`sha256` the cart recorded, and installs it. That is the remedy to reach for —
breaking the seal is for a pin that cannot be resolved at all.

The cart carries no game data and no ROM bytes. You supply your own, exactly
as the engine already asks you to.

## Credits

- **distilledorion-sketch** — [Crystal Animated Sprites with Shiny
  Visuals](https://github.com/distilledorion-sketch/crystal_animated_sprites_with_shiny_visuals),
  pinned here unmodified rather than forked.
- **Gen1Recomp** — the engine, the cart format, and the asset-transform
  sandbox the recolor runs in.
- **pret** — the disassemblies underneath all of it.
