-- Wild Green, as one mod.
--
-- The cart is not a mod.  `wild_green` is a CART: a pinned list of four mods,
-- an order to load them in, and a shell colour.  The launcher installs a cart
-- by fetching each mod and installing it separately, which is why a cart is
-- not a thing you can hand to something that only imports mod .zips.
--
-- This is that list, flattened.  The four mods sit under `mods/` exactly as
-- they were released -- not merged, not edited, not repacked -- and this file
-- runs each of their entry points in the cart's own order, handing each one a
-- `mod` of its own rooted at its own folder.
--
-- ------- why the importer forces this shape
--
-- A .zip with four mod folders in it is rejected before anything reads it:
--
--     if #topDirs > 1 then
--       return nil, "the .zip must contain a single mod folder"
--     end
--     src/mods/LauncherMods.lua:384
--
-- So "put them all in one zip" cannot mean four manifests.  It has to be ONE
-- mod, and the four have to be its payload.
--
-- ------- what a sub-mod gets
--
-- Everything the engine gave this mod, with four things swapped:
--
--   read     rooted at mods/<id>/, so `mod:read("features.lua")` finds the
--            sub-mod's own file rather than this one's
--   assets   the same, so an asset path resolves inside the sub-mod
--   path     for its log lines and stack traces
--   find     answers for its SIBLINGS first.  The two bundles look each other
--            up to decide who installs the features they share, and a
--            compilation where neither can see the other is one where both
--            think they are alone.
--
-- Everything else -- content, hooks, events, game, world, ui, log, storage --
-- is the engine's own object, passed straight through.  A sub-mod is not
-- running in a sandbox here; it is running exactly as it would if the
-- launcher had installed it, which is the only way this stays honest.
--
-- ------- the one thing that had to be worked around
--
-- Options are keyed by the INSTALLED mod's id, and `define` assigns rather
-- than merges:
--
--     loader.optionSchemas[modId] = schema     src/mods/Loader.lua:1508
--
-- Four sub-mods under one id means the last `define` would throw away the
-- other three schemas, and with them every default those rows carry.  So
-- `define` is accumulated here and re-defined as the union each time.
--
-- Sharing one bucket is otherwise correct rather than a compromise.  The two
-- bundles both carry MENU LAYOUT and MOD MANAGER on purpose, and they already
-- store those settings "under a bundle-independent id ... so they do not move
-- when the winner does" (runtime/claims.lua).  Keys that collide are keys
-- that were meant to.

local mod = ...

-- The cart's own load_order, which is also priority order: qol (100), the
-- sprites (980), ui (1100), wild green (1300).
local ORDER = {
  "gen1_wild_qol",
  "crystal_animated_sprites_with_shiny_visuals",
  "gen1_wild_ui",
  "wild_green",
}

-- Names each sub-mod may be looked up by, beyond its id.  `mod.find` is how
-- the bundles recognise each other, and they ask by repository name as well.
local ALIASES = {
  gen1_wild_qol = { "Gen1WildQOL", "gen1_wild_qol" },
  gen1_wild_ui = { "Gen1WildUI", "gen1_wild_ui" },
  wild_green = { "Gen1MakeItGreen", "wild_green" },
  crystal_animated_sprites_with_shiny_visuals = {
    "crystal_animated_sprites_with_shiny_visuals",
  },
}

local ROOT = "mods/"

-- Every row every sub-mod has defined so far, in order, deduplicated by key.
-- First definition wins, which matches how the claim works: the first bundle
-- to load owns the feature, and the second stands down.
local schema, seenKey = {}, {}

local installed = {}

local function facadeFor(id)
  local root = ROOT .. id .. "/"
  local facade = setmetatable({}, { __index = mod })

  facade.path = tostring(mod.path) .. "/" .. root:sub(1, -2)

  function facade:read(relative)
    return mod:read(root .. tostring(relative))
  end

  facade.assets = setmetatable({}, {
    __index = function(_, name)
      local real = mod.assets and mod.assets[name]
      if name == "path" and type(real) == "function" then
        return function(_, p) return real(mod.assets, root .. tostring(p)) end
      end
      return real
    end,
  })

  -- Each sub-mod gets its own exports table, so one mod's exports cannot
  -- overwrite another's -- and so a sibling that finds it reads what that
  -- sub-mod published rather than whatever ran last.
  facade.exports = {}

  facade.options = {
    define = function(_, rows)
      for _, row in ipairs(rows or {}) do
        if type(row) == "table" and type(row.key) == "string"
            and not seenKey[row.key] then
          seenKey[row.key] = true
          schema[#schema + 1] = row
        end
      end
      mod.options:define(schema)
      return rows
    end,
    get = function(_, key) return mod.options:get(key) end,
  }

  facade.find = function(other)
    local wanted = tostring(other)
    for otherId, entry in pairs(installed) do
      if otherId == wanted then return entry end
      for _, alias in ipairs(ALIASES[otherId] or {}) do
        if alias == wanted then return entry end
      end
    end
    if type(mod.find) == "function" then return mod.find(other) end
    return nil
  end

  return facade
end

for _, id in ipairs(ORDER) do
  local relative = ROOT .. id .. "/main.lua"
  local source = mod:read(relative)
  if not source then
    mod.log:error("%s is missing from this bundle -- reinstall it", relative)
  else
    local chunk, compileError = load(source, "@" .. tostring(mod.path) .. "/" .. relative)
    if not chunk then
      mod.log:error("%s did not compile: %s", relative, tostring(compileError))
    else
      local facade = facadeFor(id)
      -- Published BEFORE the entry runs, so a sub-mod loading later can find
      -- one that loaded earlier -- and so a sub-mod that looks itself up
      -- during its own install does not get nil.
      installed[id] = { id = id, version = nil, exports = facade.exports }

      -- Both entry conventions are in the four: three `return function(mod)`,
      -- one `local mod = ...`.  Passing the facade as the vararg serves the
      -- second, and calling what comes back serves the first.
      local ok, result = pcall(chunk, facade)
      if not ok then
        mod.log:error("%s failed to load: %s", id, tostring(result))
      elseif type(result) == "function" then
        local ranOk, err = pcall(result, facade)
        if not ranOk then
          mod.log:error("%s failed to install: %s", id, tostring(err))
        end
      end
    end
  end
end

mod.log:info("Wild Green: %d of %d mods installed", (function()
  local n = 0
  for _ in pairs(installed) do n = n + 1 end
  return n
end)(), #ORDER)
