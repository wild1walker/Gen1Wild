# Gen1AutoSave

Manual saving, made optional. The game saves itself on a timer, after the
things worth saving after, and on the way out, so a bad guess in a cave never
costs you an hour again.

## What it saves after

Battles, catches, evolutions, hatches, trades, blackouts and walking into a
new area. Plus a timer that counts **play** time rather than wall-clock time,
so `5 MIN` means five minutes of actually playing, not five minutes of
standing on a route with the game open. The write itself waits for a quiet
moment in the overworld.

It also saves when you pick QUIT, before the confirm box, which is the last
moment the game is still around to finish sending it anywhere.

## It tells you, quietly

When a save lands, a Poké Ball wobbles in the corner of the screen instead of
a text box taking over the bottom of it. If you would rather have a small
`SAVED` panel, the classic text box, or nothing at all, that is one option.

Manual saving is left completely alone. It writes and syncs exactly as it does
without this mod. The only thing that happens is the timer resetting, so an
autosave never lands on top of a save you just made yourself.

## Rollback

Optional backups of recent autosaves, kept beside your save rather than in it.
**START > BACKUPS**, pick a time, confirm. Off by default.

## Worth knowing

The interval, the event saves, the quit save, the indicator and the backups
are all separate switches. Link play is unaffected. It conflicts with
`recomp-autosave`, so run one autosave mod, not two.

If saving ever goes quiet, look for `PAUSED` where the indicator usually is:
that means the launcher is holding a save-sync conflict and wants an answer.
**MODS > SAVE SYNC**, pick a side, and saving resumes.

## Credits

By **Wild**, written for this mod rather than derived from anyone else's,
built on the save and map hooks of
[Gen1Recomp](https://github.com/bryanthaboi/gen1recomp). MIT.

**Pokémon** Red, Blue and Yellow are Nintendo / Creatures / GAME FREAK. This
is an unofficial fan mod, distributed free, with no affiliation with or
endorsement by any of them.
