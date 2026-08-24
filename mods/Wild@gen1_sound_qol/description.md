Two audio fixes, both optional, both off-able back to the cart's own behaviour:
the low-HP battle siren beeps once instead of looping forever, and on mobile
the game mutes itself when another app takes the audio.

Nothing here is on that you did not ask for. Every behaviour below is a row in
**MODS > Gen1SoundQOL > OPTIONS**, and every row can be put back to vanilla.

## The low-HP beep plays once

Vanilla mirrors the Game Boy exactly: once a POKéMON's HP bar goes red,
`audio/low_health_alarm.asm` runs the two-tone siren *every frame* until the
mon heals, faints, or the battle ends. On original hardware that is correct.
Over a long battle it is also the single most complained-about sound in the
game.

With this on, the siren plays one cycle when the bar enters the red and then
goes quiet. It plays again when you take another hit, so a hit still *sounds*
like a hit, and again if you heal out of the red and drop back in.

`LOW HP BEEP` is `ONCE`, `N BEEPS` or `VANILLA` — `VANILLA` restores the
endless loop byte for byte. `BEEP COUNT` sets how many cycles `N BEEPS` plays,
and `BEEP EACH HIT` decides whether losing more HP while already in the red
beeps again.

This runs through the engine's own `battle.low_health_alarm` hook: the mod
reshapes the on/off toggle and lets the engine start and stop the loop. It
never touches the audio system, and it never changes the engine's internal
`wLowHealthAlarm` latch — so the alarm's own rules (a running siren rides out
the HP drain, a heal silences it, a KO clears it) stay the engine's.

## Auto-mute when something else is playing

If a music or podcast app takes the audio session, the game goes quiet instead
of coming back over the top of it when the OS hands the session back.

`BG AUDIO MUTE` picks which buses to silence (`OFF`, `MUSIC`, `MUSIC+SFX`),
`BG MUTE ON` is `MOBILE` or `EVERYWHERE`, and `BG MUTE ENDS` decides whether
the game un-mutes itself when the OS gives the audio back or waits for you.
While the feature is live the in-game **OPTIONS** menu grows a `BG AUDIO MUTE`
row reading `OFF` or `MUTED`, which is both the manual un-mute and a plain
"shut the game up right now" button.

Muting never edits your saved `MUSIC VOL` / `SFX VOL`. The mod holds the live
level at zero and restores your own numbers when the mute clears; changing the
volume rows while muted still stores what you picked, and you hear it the
moment the mute ends.

## The honest limits

These are the platform's, not the mod's:

- **The signal is the OS audio session, not "is Spotify playing".** Android
  reports audio-focus loss and iOS an `AVAudioSession` interruption; both reach
  Lua as `audiosuspend` / `audioreset`, and there is no "is other audio
  playing" query on the mod surface. A phone call and a podcast look identical,
  which is what `BG MUTE ENDS: AUTOMATICALLY` is for — that is the
  duck-during-a-call reading.
- **It cannot stop the game asking for the audio in the first place.** On
  Android the engine requests `AUDIOFOCUS_GAIN` when it resumes, so starting
  music first and *then* opening the game still pauses your music. That is a
  native change, not one a Lua mod can reach. This handles the other
  direction: start audio in another app while the game is running, and the
  game gets out of the way.
- **On desktop, `MOBILE` scope means the feature never fires.** Desktop raises
  these events for audio-device changes too, which is not the same thing, so
  opting in there is deliberate.

## Compatibility

Red, Blue, Yellow and Gold/Silver, mod api 2. Requires `engine_internals`,
which is the first thing to switch off if a game update breaks it. MIT.
