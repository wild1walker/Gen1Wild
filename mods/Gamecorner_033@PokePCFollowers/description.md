All 251 Gen 1 and Gen 2 overworld followers with Pokédex-proportional sizing
and full 3D Voxel compatibility for Red, Blue, Yellow, and Gold.

This entry serves a 0.8.6 build carrying three follower HP-handling fixes on
top of upstream 0.8.3:

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

This build uses the id `PokePCFollowers`, dropping the `_VoxelMerge` suffix the
upstream mod carries. The engine keys enable state, per-version options and
mod-sync entries by id, so it installs alongside an existing
`PokePCFollowers_VoxelMerge` rather than upgrading it: enable state and
follower-size options start fresh, and anything resolving the old provider id
will not find this build. Uninstall the old entry first if you do not want both.
