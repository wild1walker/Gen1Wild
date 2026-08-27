All 251 Gen 1 and Gen 2 overworld followers with Pokédex-proportional sizing
and full 3D Voxel compatibility for Red, Blue, Yellow, and Gold.

The Pokémon that are part of the maps are drawn from those same sheets. Gen 1
gives every one of them one of five shared sprites — a "monster", a "bird", a
"fairy", a "seel" and the one Snorlax — so the Pokémon Fan Club's Pikachu, both
sleeping Snorlax, Mewtwo and the three legendary birds all wore art that was
never theirs. Fifty map objects now match the follower, at the same
Pokédex-proportional size — Bill's fused form among them, drawn as a Kabuto,
which is a choice rather than a reading: the game only says he "got combined
with a #MON" and never names it. The Copycat's three dolls and the Power
Plant's disguised Voltorb keep the sprites the cart gives them, both being
jokes the game is telling; `MAP POKEMON` turns the rest off.

Built from **Antigravity & gamecorner33's** PokéPC Followers. Gen1Follower is
its own mod rather than a fork listing: it has its own repository, its own
release numbering starting at 1.0.0, and its own id. The follower code is
theirs, the build and the fixes below are Wild's, and the credit stays with
them.

1.0.0 carries three follower HP-handling fixes on top of upstream 0.8.3:

- The follower no longer fails to spawn when the party lead is fainted. On
  0.1.86+ sandbox engines the shim borrows the selected follower's own party
  slot when spoofing the native Gen 1 spawn gate, so the gate's species and HP
  checks are satisfied by the same Pokémon.
- A fainted Pokémon is never drawn as the follower. Every render-path
  resolution is healthy-only, matching the spawn gate. The stored selection is
  preserved, so the original follower resumes on revival.
- The party submenu label fits the eight-character window: `FOLLOWER` for the
  active follower, `FOLLOW?` as the prompt on other party members.

## Mod id

This build uses the id `Gen1Follower`. The engine keys enable state, per-version
options and mod-sync entries by id, so it installs alongside an existing
`PokePCFollowers` or `PokePCFollowers_VoxelMerge` rather than upgrading it:
enable state and follower-size options start fresh, and anything resolving one
of the old provider ids will not find this build. Uninstall the old entry
first — two copies of the same follower hooks running at once is not a
supported configuration.

For mod authors: `mod.exports.providerRepository` reports
`wild1walker/Gen1Follower`, and `mod.exports.upstreamRepository` still reports
`mfrtechconsult/PokePCFollowers` for anything that matched the old provider
string literally. The sprite contract itself is unchanged.
