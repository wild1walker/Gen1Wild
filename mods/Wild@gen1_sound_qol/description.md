# Gen1SoundQOL

Two small audio fixes, both optional, both switchable straight back to what
the cartridge does.

## The low-HP beep plays once

Gen 1 mirrors the Game Boy exactly: once a Pokémon's HP bar goes red, the
two-tone siren runs *every frame* until it heals, faints, or the battle ends.
On original hardware that is correct. Over a long battle it is also the single
most complained-about sound in the game.

With this on, the siren plays one cycle when the bar goes red and then shuts
up. It plays again when you take another hit, so a hit still *sounds* like a
hit, and again if you heal out of the red and drop back into it.

If you want a few beeps instead of one, or the endless loop back byte for
byte, both are one option away.

## Auto-mute when something else is playing

Start a podcast or some music on your phone while the game is running and the
game gets out of the way instead of talking over it. When the other app is
done, it comes back, or waits for you to say so, if you would rather.

Your saved volume settings are never touched. The mod holds the live level at
zero and hands your own numbers back when the mute clears.

Two honest limits, both the platform's rather than the mod's: the game can
only tell that *something* took the audio, not what, so a phone call and a
podcast look the same; and it cannot stop the game grabbing the audio when it
launches, so starting music first and *then* opening the game still pauses
your music. This handles the other direction, which is the one that actually
happens.

## Worth knowing

Nothing here is on that you did not ask for. Every behaviour is a row in
**MODS > Gen1SoundQOL > OPTIONS**, and every row can be put back to vanilla.

Red, Blue, Yellow and Gold/Silver. MIT.
