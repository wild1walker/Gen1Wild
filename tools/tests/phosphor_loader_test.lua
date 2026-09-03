-- The compilation loader, driven against synthetic payloads.
--
-- The four real mods cannot install without a real engine, so what is checked
-- here is the part this bundle actually adds: that every payload is run, in
-- the cart's order, with a `mod` rooted at its own folder; that a sub-mod can
-- find its siblings; and that four `define` calls do not throw each other
-- away.

package.path = "./?.lua;" .. package.path

-- Run from the repository root:  luajit tools/tests/phosphor_loader_test.lua
local LOADER = "tools/phosphor_main.lua"
local passed, failed = 0, 0
local function ok(c, d) if c then passed = passed + 1 else failed = failed + 1; io.write("  FAIL  ", d, "\n") end end
local function eq(a, b, d)
  if a ~= b then d = ("%s (got %s, wanted %s)"):format(d, tostring(a), tostring(b)) end
  ok(a == b, d)
end

-- A payload per id, in whichever entry style we want to exercise.
local PAYLOAD = {}
local ran, readsFrom, foundBy = {}, {}, {}

PAYLOAD["gen1_wild_qol"] = [[
  return function(mod)
    RAN[#RAN + 1] = "gen1_wild_qol"
    READS["gen1_wild_qol"] = mod:read("features.lua")
    mod.options:define({ { key = "sprint_enabled", default = true },
                         { key = "menus_enabled", default = true } })
    mod.exports.hello = "qol"
  end
]]
PAYLOAD["crystal_animated_sprites_with_shiny_visuals"] = [[
  local mod = ...
  RAN[#RAN + 1] = "crystal_animated_sprites_with_shiny_visuals"
  mod.options:define({ { key = "front_sprites", default = false } })
]]
PAYLOAD["gen1_wild_ui"] = [[
  return function(mod)
    RAN[#RAN + 1] = "gen1_wild_ui"
    FOUND["by_id"] = mod.find("gen1_wild_qol")
    FOUND["by_repo"] = mod.find("Gen1WildQOL")
    FOUND["missing"] = mod.find("nothing_like_this")
    -- the key QOL already took, and one of its own
    mod.options:define({ { key = "menus_enabled", default = false },
                         { key = "backdrops_enabled", default = true } })
  end
]]
PAYLOAD["wild_green"] = [[
  return function(mod)
    RAN[#RAN + 1] = "wild_green"
    mod.options:define({ { key = "ribbon", default = false } })
  end
]]

RAN, READS, FOUND = ran, readsFrom, foundBy

local defined, stored = nil, { menus_enabled = true }
local logged = {}

local mod = {
  id = "wild_green_phosphor",
  path = "/mods/wild_green_phosphor",
  exports = {},
  content = {}, hooks = {}, events = {},
  read = function(_, relative)
    local id = relative:match("^mods/([^/]+)/main%.lua$")
    if id then return PAYLOAD[id] end
    -- anything else is a file inside a payload; echo the path back so the
    -- test can see WHICH folder the sub-mod's read was rooted at
    return "READ:" .. relative
  end,
  assets = {},
  options = {
    define = function(_, rows) defined = rows; return rows end,
    get = function(_, key)
      if stored[key] ~= nil then return stored[key] end
      for _, row in ipairs(defined or {}) do
        if row.key == key then return row.default end
      end
      return nil
    end,
  },
  log = {
    info = function(_, fmt, ...) logged[#logged + 1] = ("i " .. fmt):format(...) end,
    warn = function(_, fmt, ...) logged[#logged + 1] = ("w " .. fmt):format(...) end,
    error = function(_, fmt, ...) logged[#logged + 1] = ("e " .. fmt):format(...) end,
  },
  find = function() return nil end,
}

assert(loadfile(LOADER))(mod)

io.write("every payload runs, in the cart's order\n")
eq(table.concat(ran, ","),
   "gen1_wild_qol,crystal_animated_sprites_with_shiny_visuals,gen1_wild_ui,wild_green",
   "all four run, in the cart's load_order -- which is also priority order")

io.write("each is rooted at its own folder\n")
eq(readsFrom["gen1_wild_qol"], "READ:mods/gen1_wild_qol/features.lua",
   "a sub-mod's read resolves inside its OWN folder, not the bundle's -- "
   .. "without this every mod reads the first one's files")

io.write("siblings can find each other\n")
ok(foundBy.by_id, "a sub-mod finds a sibling by id")
eq(foundBy.by_id and foundBy.by_id.exports.hello, "qol",
   "and gets that sibling's own exports, not the bundle's")
ok(foundBy.by_repo, "and by repository name, which is how the bundles ask")
eq(foundBy.missing, nil, "something that is not here is still nil")

io.write("four defines do not throw each other away\n")
local keys = {}
for _, row in ipairs(defined or {}) do keys[#keys + 1] = row.key end
eq(table.concat(keys, ","),
   "sprint_enabled,menus_enabled,front_sprites,backdrops_enabled,ribbon",
   "the schema is the UNION of all four: `define` assigns rather than merges "
   .. "in the engine, so without accumulating here the last mod to load would "
   .. "erase the other three schemas and every default in them")
eq(mod.options:get("front_sprites"), false,
   "a default from the SECOND mod still resolves after the fourth has defined")
eq(mod.options:get("ribbon"), false, "and so does one from the last")
eq(mod.options:get("backdrops_enabled"), true, "and one from the third")

io.write("a key two mods both define is claimed once\n")
local count = 0
for _, k in ipairs(keys) do if k == "menus_enabled" then count = count + 1 end end
eq(count, 1,
   "MENU LAYOUT is in both bundles on purpose and they already share its "
   .. "storage id, so the key appears once -- first definition wins, which is "
   .. "the same rule claims.lua uses for who installs it")
eq(mod.options:get("menus_enabled"), true, "and a stored value still wins over both")

io.write("a broken payload does not take the others down\n")
PAYLOAD["gen1_wild_ui"] = "this is not lua("
ran, READS, FOUND = {}, {}, {}
RAN = ran
logged = {}
assert(loadfile(LOADER))(mod)
eq(#ran, 3, "the other three still install when one will not compile")
local said = false
for _, line in ipairs(logged) do if line:find("gen1_wild_ui") then said = true end end
ok(said, "and the one that failed is named in the log rather than swallowed")

io.write(("phosphor loader: %d passed, %d failed\n"):format(passed, failed))
os.exit(failed == 0 and 0 or 1)
