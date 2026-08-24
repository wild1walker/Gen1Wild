The party menu, drawn like the rest of the set.

## Every POKéMON in its own colours

Vanilla lays **one** palette zone over the icon column — all six members at
once — so every POKéMON in your party comes out wearing the same salmon. This
replaces that single zone with one per member, so each wears its own species
colours: the same thing Gen1Dex does for its rows and Gen1BillsBox does for its
grid. A party opened next to either of them stops looking like a different
game.

The base palette becomes the plain grey ramp too, so the names, numbers and
boxes read as black line art rather than sitting under a bar palette standing
in for a screen palette.

An icon mod's authored full-colour art is left exactly as its author drew it.
Those icons are detected per **mon** rather than per species — so a shiny tells
itself apart from an ordinary one of its kind — then marked true-colour and
kept out of the palette pass, which keys off the red channel and would
otherwise paint an orange pixel white.

## Nothing runs off the edge

The vanilla row is packed to the last pixel of the screen: the status column
runs 136–160 and the HP numbers 104–160. That is authentic, and it is why an
`FNT` reads as clipped rather than placed.

Both stop at **152** now, the same right margin every other screen in the set
keeps — and nothing was given up to pay for it:

- The **status** moves from a fixed `x=136` to right-aligned on 152. Free: the
  level always ends at 128, because `PrintLevel` overwrites the `<LV>` tile
  with the third digit at L100, so two digits and three end in the same place.
- The **HP bar** moves one tile left, from tile 5 to tile 4, and the numbers
  right-align on 152. The bar keeps **all six segments** — it is the
  at-a-glance read on this screen — and the gap it moves into is the one
  between the icon and the bar that nothing was using.
- The **numbers** keep their `%3d/%3d` padding rather than becoming variable
  width, because that padding is load-bearing: the bar's right cap sits under
  the first glyph, and a *space* over that cap is what stops the two colliding.

## What it does not touch

`PartyMenu` is not one screen but seven behind a single id — the field menu,
the battle switch, the forced switch after a faint, the item target, the TM/HM
teach list with its `ABLE` / `NOT ABLE` column, the `SOFTBOILED` donor, and the
evolution-stone list. Each has its own input rules, its own bottom message and
its own idea of what A does.

This mod replaces **two methods**, `draw` and `sgbPalettes`, and nothing else.
It has an opinion about how the party *looks* and none at all about what it
does. The test suite checks that directly: it diffs every field the vanilla
constructor sets against the one this mod hands back, and fails if any of them
went missing.

## Options

**SPECIES COLOURS** (on) — every member in its own species colours over the
grey ramp. Off restores the vanilla answer exactly, for anyone who wants the
1996 screen with nothing changed but the margins.

## Known limits

There is **no header box** on this screen and there cannot be: six members at
16 pixels fill rows 0–11 exactly and the message box owns rows 12–17, so a
boxed top would cost either a party slot or the second line the TM/HM prompt
needs. The message box is the footer instead, and was already the right chrome.

There is **no ruled icon column** either, unlike the Pokédex list. That rule
needs the names to start at 32; here they start at 24, and the eight pixels can
only come out of the name column — which holds a **nickname**, and a nickname
is the player's own text. Cutting `CHARMANDER` to `CHARMANDE` to make room for
a hairline is not a trade worth making.

A three-digit HP still lands a digit on the bar's right cap, exactly as it does
in vanilla.
