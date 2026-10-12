# mapgen: mockup → Porymap map pipeline

Tools for turning the planning mockups in `../orleans_maps/*.png` into real pokeemerald-expansion
maps without driving Porymap's GUI, plus the custom Orleans tilesets they use. Isle Marais
(`maps/isle_marais.json`) is the finished reference map: copy its patterns.

Run everything from the decomp root (`orleans_expansion/orleans_expansion`).

## The pipeline for a new map

1. **Extract the mockup** into a terrain grid:
   `python tools/mapgen/extract.py ../orleans_maps/<file>.png tools/mapgen/maps/<name>`
   → `<name>.grid.txt` (one char per tile) and `<name>.detected.json` (frame, buildings, markers).
   The mockup's map frame is the dark line `(91,83,70)`; grid lines are every 10 tiles (36 px per tile
   so far). Terrain is the dominant key colour per tile (see `TERRAIN` in extract.py). Markers/labels
   leave noise cells: fix them with `edits` in the spec, don't hand-edit the grid file.
2. **Make sure the map exists** in `data/maps/<Name>/map.json` and `data/layouts/layouts.json`
   (create it in Porymap or by hand). The builder updates layout size/tilesets and rewrites events.
3. **Write the spec** `maps/<name>.json` (copy isle_marais.json): `tileset`, `grid`, `edits`,
   `buildings` (prefabs), `objects`, `items`, `hidden_items`, `exits`.
4. **Preview** without writing: `python tools/mapgen/build.py tools/mapgen/maps/<name>.json --dry-run --preview out.png`
   and look at it (render at 2–3×, crop regions). Iterate on edits/positions.
5. **Write** (drop `--dry-run`), then **check**: `python tools/mapgen/check.py tools/mapgen/maps/<name>.json`.
   Target: 0 terrain seams above 20, 0 off-palette grass, 0 gameplay problems. It also writes
   `maps/<name>_compare.png` (mockup beside result) and `<name>_seams.png`.
6. Send the comparison image for review; repeat.

Spec details:
- `edits` are `[char, x, y, w, h]` rectangles applied **in order**: later edits win. When clearing
  an area and then painting groves/patches into it, put the clear first.
- Prefab rows may contain `null` (leave terrain), a name, or `{"var": name}` (variant chosen from the
  tile underneath; see piers). `door` is `[x,y]` or a list of them (double doors). `passable` cells
  get collision 0; everything else in a prefab blocks.
- Doors warp to themselves (`dest_map` = this map) until interiors exist.
- `signs` become bg sign events with generated `MSGBOX_SIGN` scripts. `surf_only` lists event cells
  reached by Surf later (check.py's walk test skips them).
- Item flags are repurposed `FLAG_UNUSED_*` entries in `include/constants/flags.h`; hidden items need
  a flag ≥ `FLAG_HIDDEN_ITEMS_START`.

## Interior mockups

`python tools/mapgen/interiors.py` draws planning mockups for every interior into
`../orleans_maps/interiors/` (plus `00_interiors_overview.png`). They use the same frame and 36 px
pitch as the outdoor mockups, and their key colours are registered in extract.py (`W` wall, `f`/`t`
floors, `C` counter, `b` bed, `s` shelf, `p` planter, `h` hedge, `E` exit...), so a reviewed interior
can be extracted and built like an outdoor map. Edit the `INTERIORS` table to change them.

## Tilesets: composing instead of using sources directly

HnS (Heart & Soul) Johto/Kanto and FRLG sets on disk use FireRed's 640-tile primary layout, which
`mapjson` skips in an Emerald build, and Team Aqua "Great Tileset Exchange" sets are triple-layer.
So we never use those directly: `compose.py` builds normal Emerald-format tilesets from picked
pieces, then registers them in `src/data/tilesets/{graphics,metatiles,headers}.h` (marked block).

`python tools/mapgen/compose.py tools/mapgen/tilesets/recipes/<recipe>.json [...] --register`
(`--register` always registers every recipe in `recipes/`.)

Current tilesets:
- `gTileset_OrleansGeneral` (primary): HnS Johto general minus its cliff block (Louisiana is flat),
  recoloured to the swamp greens. Paths, PC/Mart, fences, Johto water.
- `gTileset_OrleansBayou` (secondary): Ekat99 swamp sheet (water/marsh/mud corner sets, cypress,
  knees, weeds, stumps), Shady Forest houses, Moomoo Farm barn, Brick City church + sailboat,
  Olivine/Route 40 dock, Soul House headstones (recoloured grey), path inner corners.
- `gTileset_OrleansRoute` (secondary): the bayou set minus town buildings, plus Ekat tall grass on
  marsh, the Mesprit shrine stone and the Olivine dock as a horizontal landing (`dock_h`). Routes use
  builder config `tilesets/orleans_route.json`.
- `gTileset_OrleansTown` (secondary, Grand Oak): bayou terrain, Shady houses, vanilla Emerald Pokemon
  Center, Mart, own-art greenhouse gym, magnolias and planters, the red flower recoloured into five more colours,
  sugarcane and pepper beds. Demand-driven + palette v2 (361/512 tiles); see "Grand Oak" below.
- `gTileset_OrleansCity` (secondary): Brick City, for Crescent City. Not used on a map yet.

Limits per tileset: 512 metatiles, 512 tiles; palettes 6 (primary) / 7 (secondary) of 15 colours.
The bayou set is demand-driven with palette v2 (only Isle Marais uses it): ~421/512 tiles; the pieces its map doesn't place are
left out until a map asks for them (compose, then build again).

Recipe features (see compose.py docstring):
- Sources: `type: tileset` with `ranges` (keep 8-wide layout) or `ids`; `layout: frlg` for HnS
  640-tile primaries; `layers: 3` flattens triple-layer metatiles; `type: image` cuts 16×16 cells from a
  sheet (`bottom`, `top`, stacked cells, or `quads` built from quarter-cells); `pick_only_for_patches`
  makes a source available to patches without adding its metatiles.
- `recolor` (exact swaps, recipe-wide) and per-source `recolor`; `recolor_tolerance` also swaps near
  colours (**keep it small, ≤6**: at 14 it turned Ekat's water green).
- `keep_colors`: colours palette reduction must keep exactly (grass, water, headstone greys).
  Locking colours makes other colours squeeze harder; anything that shares a palette with a locked
  colour can get pulled toward it, so lock the important neighbours too.
- `rebase_ground` (per source): building tiles that contain the source's own grass get that grass
  cut away and are redrawn over `ekat:grass`, so grass texture is continuous up to walls.
- `patches`: `lower` + `upper` (put an object's upper layer on our water/grass/marsh), `behavior`
  override (doors!), `layer`, `hflip` (mirror a tile), `reseat` (cut listed ground colours away and
  draw over a base: trees on marsh/water), `inner` (path inner corners: a pixel becomes grass only
  where both edge pieces are grass there, with both layers merged first).
- `backdrop`: colour 0 of every palette = swamp grass, so holes in source tiles don't show black.

## Autotiling techniques (build.py)

- **Ekat corner sets (water, marsh, mud, churchyard)** are *corner/dual-grid* tiles: the bank runs
  through tile middles. Each drawn tile is chosen from its four corner cells (x,y),(x+1,y),(x,y+1),
  (x+1,y+1) (`CORNER_KEYS`). Ekat's octagon blocks provide 14/16 cases; the two diagonal "saddles"
  are assembled from quarter tiles. A tile with ≥2 water corners is water (surfable).
  - `alt_land`: water uses the water-on-mud or water-on-marsh bank pieces when its land side is
    mud/marsh, so terrains can meet cleanly. Order matters: marsh/mud passes run before water.
  - **Three terrains at one tile** (e.g. the end of a mud flat on a grass shore): Ekat has no art for
    this, so the builder asks for a generated *blend* tile: grass-bank and mud-bank pieces merged
    pixel by pixel along the mud patch's own soft edge (outline kept). Two-pass: `build.py` writes
    missing ones to `tilesets/orleans_bayou.blends.json` and says so; run `compose.py` on the bayou
    recipe, then build again.
  - Mud and marsh have no shared transition set: no single tile may have both mud and marsh
    corners (keep a grass column between them; check with the snippet in check.py's history or by
    scanning 2×2 cell blocks).
  - `neutral` cells (piers, boats) count as water only where they stand over water.
  - `smooth` removes one-tile spurs/notches before corner tiles are chosen.
- **Johto dirt paths** are cell-based 3×3 with generated inner corners at junctions. Paths should be
  ≥2 tiles wide (1-wide paths have no edge pieces). `connects` is only path chars.
- **Churchyard**: mud corner patch; headstones only on tiles whose four corners are all churchyard.
- **Tall grass** (`G`, routes) is a marsh-connected terrain with `interior_of`: the tall-grass tile is
  only placed where all four dual-grid corners are marsh/tall grass, so every patch gets a soft marsh
  rim and never meets water or grass with a hard edge. Expect the encounter area to be one tile
  smaller on the right/bottom than the mockup block.
- **Roads through marsh or water** need a one-tile grass corridor on each side (patch borders are
  drawn in the neighbouring cell, and a road cell would cover them). Route 1 is the example.
- **Overlay objects** (prefab cells `{"overlay": "custom:pirogue_00"}`): the art is composited over
  whatever terrain tile the builder finds underneath (mud, bank, water, blend), so an object can sit
  across a shoreline without a hard edge. Missing combinations go through the blends file like
  blends (two-pass). `{"overlay": "r40:3E8", "upper": true, "walk": true}` takes the art's upper layer
  and its behaviour: that's how boardwalks (`walk_hN`, `walk_vN` in the bayou config) cross shorelines
  and stay walkable over water. Our own art lives in `sources/orleans_custom/` with the script that draws it.
- **Water decor** is single-tile only (lily pads, leafy water plant), on fully open water. Multi-tile
  water objects are prefabs: `waterlog`, `snag_water` (top piece from Ekat's grass stump),
  `cypress_water`. Ekat's stump/tall-reed water cells and second knees row are cut off in the sheet:
  don't use them as single tiles.
- **Paths** are packed mud (primary recolour, applies to every bayou map).

## Placement rules learned the hard way

- A corner patch draws its **left/top border in the cell to its left/above**. Leave at least one
  grass cell between a prefab (building, ridge, path) and the left/top of a marsh/mud patch, or the
  border is covered and you get a hard straight edge.
- Trees in groves must be fully inside the marsh: tree cells x ≤ marsh_xmax−1 and y ≤ marsh_ymax−1
  (dual grid). Same idea for anything reseated on a patch base.
- Keep groves a tile away from buildings and from other patches (mud next to marsh seams).
- Every warp must sit on a door-behaviour tile or it never fires (most source door tiles were
  `MB_NORMAL`: give them `MB_NON_ANIMATED_DOOR` via a patch). Every door needs a walkable tile
  below it, and every door should get a ≥2-wide path to the street.
- Building backgrounds: always rebase/reseat onto `ekat:grass`/water/marsh; check.py flags misses.
- Mockup buildings are smaller than real prefabs: expect to nudge positions, then re-check events
  (items and NPCs end up inside buildings or water after moves).

## Asset sources

See `CREDITS.md` (must ship with the game). Source files are in `sources/`. Finding new pieces:
`survey.py` renders tilesets the way Porymap shows them; for modular sets with an example map,
recover building layouts by matching every metatile against the example screenshot (done for
Brick City; Shady Forest's example uses a different primary so it didn't match).
Research boards: `tileset_research_board.png` (on-disk sets), `web_tileset_research_board.png`.

## First passes of the rest of the world (`firstpass.py`)

`python tools/mapgen/firstpass.py [key ...]` (from the repo root) rebuilds the towns and Routes 2-25
from their mockups: extract (outdoor colours) -> normalise -> scale (towns) -> tidy paths -> bridges ->
docks -> planned buildings (towns) -> door paths and island joining -> verges/banks -> trees and
greenery -> build --no-blends -> check. Towns use `gTileset_OrleansHarbor`; their buildings, scale
and terrain fixes are hand-listed in `town_plans.py` (each building names the interior room it
leads to). Afterwards run `python tools/mapgen/build_interior.py`: it links each door to its room
by label and rebuilds the first-pass exteriors so the warps lead inside. Specs are regenerated on
every run, so hand edits belong in `town_plans.py`, not in `maps/<key>.json`.
`sheet.py <out.png> <title> <key>...` stacks compare images into a review sheet.

Natural paths (`natural.py`, called from `first_pass` for routes and generated towns, not the handmade cities or the
shrine): after the last path tidy, dirt roads get worn bevels inside elbows and junctions, uneven stair treads on
diagonal roads, the odd rounded outer corner, occasional one-cell bulges on alternating sides of straight runs, rare
lateral drifts on long clean stretches, and small doorstep aprons where a door's stub is long. Every edit is
scored with the path autotile's own rules (each cell in a 2x2 block, at most one inner-corner diagonal, no
1-tile grass slivers) and kept only if the drawing gets no worse. Nothing changes within 4 tiles of the map
edge (exits line up with the neighbours), on or beside prefabs, docks and bridges, or next to water, marsh and
mud. Everything is seeded from the map key, so reruns are stable.

## Crescent City (`crescent.py`, hand-designed)

Crescent City is not a first pass: `python -W ignore tools/mapgen/crescent.py` lays the whole city out in
code (districts, streets, water, props), regenerates the `orleans_crescent` tileset variant, builds in as many
passes as the overlay tiles need (build, compose, build), runs check.py and writes `maps/00_crescent_review.png`;
then run `build_interior.py` (or pass `--relink`) so the rooms' exits match the door warps. build.py rewrites
`data/layouts/layouts.json`: never run two tools that write it at once. The map is 104x66 (the mockup at 1.5x plus
14 columns on the west for City Park); the code works in design coordinates (x from -14). `--dry-run --preview out.png` skips writing the map. Edit `crescent.py`, never
`maps/crescent_city.json`. Room keys and prefab choices still come from `town_plans.PLANS["crescent_city"]`.

- Own art: `sources/orleans_custom/make_crescent_art.py` draws tombs, oven vaults, the oldest crypt, the Fifolet
  gym, iron fences and balconies, ruins, market stalls, fountain, hedges, flower beds, boardwalk planks, mailbox,
  bin, sign and generator onto one sheet per colour family (`crescent_<family>.png`, + `crescent.json`). Every
  piece is snapped to a family of <= 15 colours taken from the tileset's own palettes, so palettes don't squeeze.
- `crescent_tileset.py` (hooked into `make_town_tilesets.py`) trims what the city never uses (mud, small cypress,
  marsh-water set, Olivine dock, unused Ekat pieces), recolours the shared props/magnolia into the families and
  turns every art piece into a prefab. Overlay-only sources cost tiles only for the composites the map uses;
  opaque pieces (planks, flower beds) are plain metatiles (`*_raw` sheets) so they cost no ground copies.
- Tile budget is tight (~510/512): draw new art on the 8 px grid, mirror symmetric pieces, keep props on grass
  (a prop on primary paving copies the paving tile into the secondary), and reuse bases.

## Storm's Edge (`storms_edge.py`, hand-designed)

`python -W ignore tools/mapgen/storms_edge.py [--review] [--fresh]` lays out the port in code (50x38, the mockup at
1.25x), regenerates its art (`sources/orleans_custom/make_storms_art.py`) and the `orleans_port` recipe
(`make_town_tilesets.py orleans_port`, which applies `storms_tileset.py` as the variant's `addon`: still demand-driven,
palette v2), then builds / composes until no overlay is missing, and runs check.py and bridge_check.py. `--review`
writes `maps/00_storms_edge_review.png` (mockup | built, zoomed crops incl. the drawbridge raised). Edit
`storms_edge.py`, never `maps/storms_edge.json`; door warps keep the first pass's order, build_interior.py relinks by label.

- **Map states** (build.py): a spec's `"states": {name: [cells]}` lists cells a map script swaps in with `setmetatile`
  (`overlay` art drawn over the terrain beneath, `tile` a named piece or `"terrain"`, `collision`). build.py resolves
  them (so a demand tileset keeps the pieces) and writes `<Map>_EventScript_State<name>` into the generated script
  block with the current metatile ids. `setmetatile` keeps map.bin's elevation, so design the state around it.
- **The drawbridge**: map.bin has it lowered (surf-under, build.py's Bridge rules). `story/StormsEdge.inc` (spliced into
  scripts.inc by storms_edge.py, story.py's convention) runs `StormsEdge_EventScript_StateBridgeRaised` ON_LOAD
  unless `FLAG_STORMS_EDGE_GRID_RESTORED` (flags.h 0x39) is set: leaves up (blocking), the two middle columns plain
  water (their deck elevation 15 lets surfers through; walkers can't reach them), barriers across the deck stubs.
- **The gym is on the west bank** (user decision 9, 2026-10-12): the substation yard, the Center and the west houses are on the near
  side of the drawbridge, the Mart, lighthouse, east house and the Route 3 exit on the far side. `story_gates_check.py` flood-fills
  the raised-bridge state to prove the bridge is the only way across. `storms_edge.py` no longer rewrites `story/StormsEdge.inc`
  once it exists (the story pass owns it; `story_overlay.py` patches the people, `story.py` splices the scripts).
- **Flags**: story flags take a `FLAG_UNUSED_0x0NN` slot in flags.h's low Orleans block (named, with a comment);
  hidden items take the next `FLAG_HIDDEN_ITEMS_START + n` (replacing a `FLAG_UNUSED_0x26N` define); item balls get
  theirs from `firstpass.item_flag()` (item_flags.json).
- **Quay and pier**: own dark planks (`seq:` overlays, walkable over the water) on row 21 along the whole south shore;
  lanes run under the quay's edge row as path so the dirt meets the planks. Stilt houses are the Shady cabin over an
  own-art stilt row (`sst:`) standing in the water, its middle cell steps down to the quay.

## Lutin's Hollow (`hollow.py`, hand-designed)

`python -W ignore tools/mapgen/hollow.py [--review] [--fresh] [--no-build] [--ascii] [--bare]` (inside `buildlock.py acquire/release hollow`)
lays out the glade in code (50x38, tileset `orleans_hollow` + `hollow_tileset.py`, demand-driven, palette v2): a pond with a soft
organic loop path (brush strokes + majority smoothing + `natural.Shape` hill-climb), a spur to every door, the Route 13 lane in the
south-west, a dense ring of moss-draped trees (superellipse mask with a ragged edge, greedy packing of 3x3/2x2 trees then 1x1
thickets) with that one gap, glades with pepper plots and fairy rings, a reflecting pool beside each false Lutin, the Delphoxite
riddle stone (item ball, flag from item_flags.json) and layered undergrowth. No benches, marsh or tall grass. `--bare` builds terrain,
buildings and paths only (reads the terrain seams without stand-in noise). Edit `hollow.py`, never `maps/lutins_hollow.json`.
Art: `hollow_tileset.WANTED` lists every piece with its footprint; pieces without art use same-footprint stand-ins; art goes in
`sources/orleans_custom/hollow.png` + `hollow.json` (camp's format; request in `art_requests/lutins_hollow.md`).

## Isle Marais (`isle_marais_gen.py`, polish pass over the approved map)

Isle Marais is the one approved map that has a generator: `python -W ignore tools/mapgen/isle_marais_gen.py [--out DIR] [--proposal]
[--ascii]` (inside `buildlock.py acquire/release isle_marais`) rewrites `maps/isle_marais.json` + `.grid.txt` from the untouched
original (`maps/isle_marais.base.json` + `.base.grid.txt`): hand-drawn path spans (barn plaza, straight church path, street ends flush with the cabins, the
pier's foot), organic mud banks, the east marsh bulge with its grove, reeds and second lily pond, a reed bed beside the road. Paths are
checked with `natural.Shape` and may not cover a patch's left/top border (`wet()`); prefabs on patches are checked like check.py does. Buildings,
doors, NPCs, items, signs, triggers and the Route 1 exit are the original's, so no `build_interior.py` run is needed. Then build, compose
(orleans_bayou is demand-driven), build, check. `isle_marais_review.py` writes `maps/00_isle_marais_slice_review.png`
(before | after, 3x crops, the Route 1 join and mock-ups of the proposals). `joined.py` knows the Isle Marais / Route 1 join.

## Grand Oak (`grand_oak.py`, hand-designed; the slice polish of 2026-10-12)

`python -W ignore tools/mapgen/grand_oak.py [--review] [--fresh] [--no-build] [--ascii] [--preview out.png]` (inside
`buildlock.py acquire/release grand_oak`; `--preview`/`--review`/`--no-build` write nothing to `data/`). The fixed design (PC, Mart,
gym, fountain, planters, nursery, cabins and their order = the warp order) is the approved 2026-10-10 build; events, hidden items,
signs and the buildings' interior links are kept from the spec on disk. The generator writes `maps/grand_oak.json` + the grid
(edit `grand_oak.py`, never those), applies `grand_oak_tileset.py` (demand + palette v2, the flower colours, the signpost),
builds / composes until no overlay is missing, settles the palette with one more compose + build (v2 weighs colours by what the
built map shows; one pass is not always a fixed point: the grass in the path inner corners can come out off-palette) and runs check.py.
- Paths are a hand-drawn row table (`ROWS`, 'a-b,c-d' x spans per row), checked with `natural.total_bad` (0 = every cell drawable by
  the path autotile). A 2-wide path draws only ~1.3 tiles of dirt (the edge pieces keep a grass band), so streets are 3 wide, lanes
  2-4; a 1-row step needs 2 columns of overlap (3-wide road shifting by one) or the stair doesn't draw. Route 1's road (x 19-20) is kept
  straight and 2 wide from y 30 (the join). `joined.py out.png grand_oak:route_1` draws the join.
- Magnolias (`TREES`), lamps (`LAMPS`, 8, irregular) and flower beds (`BEDS`, colours assigned so neighbours differ) are explicit lists:
  adjust cells there. The loose flowers are the red Johto flower (primary 004) plus the same tile recoloured per source
  (`grand_oak_tileset.COLOURS`); `art_requests/grand_oak.md` asks for hand-drawn replacements.
- `maps/grand_oak_before.png` is the 2026-10-10 build rendered through the current tileset (for `--review`'s before | after).

## Land's End (`lands_end.py`, hand-designed)

`python -W ignore tools/mapgen/lands_end.py [--review] [--fresh] [--no-build] [--ascii]` (inside `buildlock.py acquire/release lands_end`)
lays the stilt town out in code (50x38, the mockup at 1.25x, tileset `orleans_harbor` + `lands_end_tileset.py`, demand-driven, palette v2):
the map is marsh (north), a mudflat (west) and open water, nothing else (no grass: no grass/water/marsh/mud triple joins; a two-row
water channel keeps marsh and mud apart). Narrow dark boardwalks (own planks, `plank_<h|v><edges>`; an edge letter means that side is
open water) follow the mockup: the main walk (2 wide) to the Route 20 boat exit at x = 0, the west/centre/east branches, the south loop
(open at its east end by a 3-cell channel so the water behind the Center and the shop stays surf-connected), the pavilion's wrap-around
deck and the Route 21 landing pier. Every dock is solid (elevation 3; a surfer goes round); build.py's bridge rules aren't used.
Pilings (`skirt`/`skirt_e`, `m` = in mud) go under every south face. Edit `lands_end.py`, never `maps/lands_end.json`.
Art: `sources/orleans_custom/make_lands_end_art.py` writes `lands_end_planks.png` (opaque planks, plain metatiles `lep:`),
`lands_end_art.png` (overlays `lea:`) and `lands_end.json`; every piece becomes a prefab of its name. The tileset sits at its 512-tile
limit (400/512 with all the art in): `lands_end_tileset.HOLD` (empty now) can hold pieces back as house-cut stand-ins; the shop and
the two trawlers (`trawler_a`, `trawler_b`, 6x3, moored with piles at x 11) are real art. `skirt_plain` fills the gaps between pilings (over
mud too), `pc_skirt_r` (cell 3 of pc_skirt) is the Center's footing at x 19, lanterns sit on the main walk's north rim at the junctions and
bollards on the west branch's rim beside the boats.
The Pokemon Center is the vanilla building reseated on water (`pcw_*` patches).

## The dry country (Routes 15, 16, 17, 23, 24: `dry_route_tileset.py`)

These five routes use `orleans_route_dry`, a third copy of the route set (`make_route_tilesets.py` + `dry_route_tileset.py`,
which reuses `redfield_tileset.dry_terrain`) with the shared dry-country art (`sources/orleans_custom/dry_country.*`, v2).
`town_plans.DRY_ROUTES` lists them (and their `TOWN_CFG` entries); `DRY_FADE` says where an edge meets a green map.
The generator runs as for any route on `.` ground, then `firstpass.dry_finish()` converts it. Terrain characters: `d` dry
ground (the dry-on-grass autotile "dry" draws its edges against `.`), `G` cane (walk-in encounter grass), `g` tall dry grass
(encounter grass), `q` pepper rows (blocking: the terrain / autotile key "collision": 1 in build.py), `Q` walk-in pepper
(encounter), `w` cane wall (blocking), `e` red earth, `v` gully, `s` salt flat (each of the four a v2 dual-grid set:
corners autotile, connects = its own character, apply_on = dry + that character), `.` meadow where the mockup draws short
grass or where the route meets a green map (Route 15 and 23's west edges fade over 11 cells). route_features.py keys:
"encounter" (G, g or Q), "share" (encounter growth), "walls" (Route 15), "base": "e" and "beds" (Route 16), "gully" and
"stones" (Route 23: the gully is the mockup's riverbed colour band, drawn 2 wide), "salt" (Route 24: the mockup's salt colour),
"rocks": "mix" | "wall" (dry_rocks; the tileset has no cliff piece, art_requests/dry_country_cliff.md).
Rules from the art: a road cell on dry ground has only sand edges, so every road gets a ring of dry ground, and every set
cell needs a dry cell between it and anything else (dry_finish ends by sending offenders back to `d`); a road cell with two
open diagonals draws one inner corner only, so the odd diagonal is filled. Field trees and rocks replace cypress and the
Cianwood boulder (`dry_features`, `DRY_PROPS`). The city approach on Route 23 ('%' paving in the green meadow, '&' its
break-up as dry road) leaves seams where the paving's grass-edged tiles meet the dry road set; the approach's own paving
breaking up has the same seams on every route (route_3, 5, 14).

## Route landmarks (`landmarks_tileset.py`, art `sources/orleans_custom/route_landmarks.*`)

The landmark art (power towers and wires, lookout, rail pieces, platforms, wrecks, pilings, temple gate, great oak ...; request
`art_requests/route_landmarks.md`, sheet `maps/00_route_landmarks_art.png`) is one overlay source `lmk` plus a prefab per piece in
the json. `make_route_tilesets.py` applies it to the shared route set (`tilesets/orleans_route.json` and its recipe, in place and
idempotently: `landmarks_tileset.apply`) and then copies that set into every variant, so any route tileset can place any piece;
tilesets are demand-driven, so a piece costs tiles only where a map places it. A placement in `route_features.py` asks for a piece by
name; `firstpass.with_placeholders` uses the real prefab as soon as the config has it, otherwise the `PLACEHOLDERS` stand-in
(still standing in: `fallen_line`, which wants dry ground Route 2's set has no terrain for; `landmarks_tileset.SKIP`).
`"spans": (tower, wire)` in a route's features lays wire_span_l / wire_span / wire_span_r along the towers' top row.

Route tilesets (each a copy of `orleans_route` made by `make_route_tilesets.py`; routes -> tileset in `town_plans.TOWN_CFG`):
`orleans_route` Routes 1-3, 5-13; `orleans_river` Route 4; `orleans_route_b` Route 14 and the Oldest Shrine; `orleans_gulf` Routes
18-22 and 25; `orleans_route_dry` Routes 15, 16, 17, 23, 24. A new variant has no uses files, so compose would keep everything and
overflow: first generate it with `BOOT=<variant> python tools/mapgen/make_route_tilesets.py` (no landmark art), compose it, build
its maps once (`firstpass.py --blends <keys>`), then regenerate without BOOT and compose again.

### Rock wall (Routes 23 and 24, `firstpass.dry_cliffs`)
`rock_wall` (v3 art: character `r`, blocking, a corners autotile with the fill list plus a "face" row: build.py `corners()` puts
the face extension piece under every south edge, `make_dry_country.face_cells` is the rule) replaces the old boulder grid.
route_features "rock_wall": the mockup's rock (holes filled, a cave box's floor included) is quantised to 2x2 blocks so every
step is 2+ cells, no diagonal touches, no thin spurs, nothing within 2 cells of a road or in the green meadow, so every south face
has its extension row and a plain row below; {"depth": (2, 4)} caps the wall's depth (Route 23's bluff), {"mouths": [(label, prefab,
(x, y))]} sets the mine mouth / Cianwood cave mouths into the nearest plain stretch of face (bottom row on the extension row), "scree"
is the share of loose rock / rock_l at the foot. dry_finish keeps every other set 3 cells off a wall. The farm routes (15, 16) are
`orleans_route_farm`: with the rock wall the dry set overflowed 512 tiles (new variant: copy the dry mapping to its mapping file, build
its routes once for their uses files, then compose).

## The Old Water (`old_water.py`, hand-polished)

`python -W ignore tools/mapgen/old_water.py [--ascii] [--dry-run] [--dev]` (inside `buildlock.py acquire/release old_water` unless `--dry-run`/`--dev`)
writes `maps/old_water.grid.txt` and the spec (huts, song house, shrine and rope walkways are read from the spec and never moved; cypress,
reeds, snags and the log are kept where they fit the terrain and nudged to the nearest spot that does). Islands are unions of discs with
bitten coves and bumps, each inside its own `ROOMS` box so they never touch; the huts keep their grass yards in marsh, as in the approved
design. There are no dirt paths (the user preferred the look without them; `paths()` is empty and the old track code, `paths_old`/`tidy`,
is only kept for reference). `verify()` checks on-foot reachability of every door, NPC and the item. The tileset (`orleans_village`, own
Rootkin art) is demand-driven with palette v2 (the only layout using it); after a layout change run build -> compose -> build until no
transition tiles are asked for. `joined.py old_water:route_1` draws the east join (a map connection with a row offset, `LINKS`).
Edit `old_water.py`, never the spec/grid.

## Route 1 (`route_1.py`, slice polish 2026-10-12)

`python -W ignore tools/mapgen/route_1.py [--out DIR] [--ascii]` (inside `buildlock.py acquire/release route_1`) rewrites `maps/route_1.json` +
`.grid.txt` from the untouched original (`route_1.base.*`); then build.py and check.py as usual. Edit `route_1.py`, never the spec/grid.
- Terrain is a literal row table (`terrain_rows()`): the original west edge (marsh and groves along x 0) and the shrine channel
  (rows 6-13, open to the west edge as the Surf exit to the Old Water) are as in the original; the south-west pond is its own pond.
  Rows 20-26 have marsh at x 0-1 (the Old Water has no tall-grass tile; tall grass starts at x 3, `tall_grass` keeps x <= 2 plain there). `old_water.py` reads `route_1.grid.txt`, so re-run it (then build.py) after changing Route 1's west column. The Old Water side carries the matching marsh shore at the seam (`joined.py old_water:route_1` draws it).
- The road is straight and 2 wide (x 14-15) with ONE 1-column shift to x 13-14 (`SHIFTS`, rows 22-23, two 3-wide rows: natural.total_bad 0); both
  exits are unchanged. (Three jogs were rejected by the adversarial review.) The channel keeps its water at x 13 beside the road, as in the original.
- Tall grass (`tall_grass`) covers the ground (370 cells; the old map had 482 on more land): a noise field cut at the verge, drifts and (less) the
  banks, blurred into rounded outlines. The NW marsh starts at row 1 (row 0 is lawn, matching Grand Oak's last row).
- South end: two bays narrow toward the causeway and the banks close before the Isle Marais seam (marsh at x 0 matches its marsh); the
  pirogue's mud bar is 3 rows higher (17,41), the west islet one row higher, Lafayette at (16,38) (`MOVED`).
- Rule learned: water, marsh and grass must never meet at one corner (that needs blend tiles), so marsh keeps a grass cell from water.
  The map needs no new tileset pieces (no compose, no rebuild of the other routes sharing `orleans_route`).
`route_1_review.py` writes `maps/00_route_1_slice_review.png`.

## World joins, phase 2 (`wedge.py`, `world_edges.json`, `world_edges_w.py`; 2026-10-12)

Edge work that makes two maps' borders meet (marsh banks carried across a basin, oyster flats running on, a channel through a shore)
lives in data, not in hand-edited specs: `world_edges.json` maps a route key to `edits` (grid rectangles painted over the generated grid),
`drop`/`dropped` (prefabs taken out, e.g. a tree whose marsh patch was cut), `add` (prefabs put in) and `exits` (spec exits the generator
doesn't list). `firstpass.py` merges it into every spec it writes (`wedge.apply_to_spec`), so a regeneration keeps the joins. Author with
`wedge.Grid(key)`: `pour` (bring the neighbour's shore in along one side: depth in runs of 2-4 cells, shallower beside a channel), `rim`
(no water/marsh/ground triple: ground cell becomes marsh), `moat` (marsh off mud), `keep_off` (flats off an island), `move`, `grove`,
then `g.auto_drop(); g.save()`. `world_edges_w.py [key ...]` is the water routes' script (re-runnable; it reads neighbours' edges from the
effective grid, so run a reference map's job first). Rules found: a path cell can't sit on the shore row; a marsh patch's border cells
may not touch paving (leave a grass cell, better two); a marsh/ground boundary reaching water needs a blend tile (avoid it on shared
tilesets); mud (`L`) never touches marsh. check.py: a spec exit with `"by_boat": true` is not walk-tested (Crescent's far bank).
build.py puts no water decor on the outer ring of a map (a plant on the seam reads as a cut across a join).

## World seams, phase 2 (land joins; Agent L, 2026-10-12)
Edge matching for the first-pass routes lives in `town_plans.py` and `firstpass.py`; `seamview.py <map_a> <map_b> <out.png> [depth] [scale]` draws one
join of `world.WORLD` from the built map.bin (plus the severity world_stitch gives it).
- `SEAM_ADOPT` (dry routes): the route's edge continues what the neighbour has at the border (`seam_adopt`: cane G, pepper q, wall w, red earth e, salt s
  painted a few cells in; plain ground clears the sets). `ROCK_KEEPOFF`: no rock wall near an edge. `DRY_FADE`'s two edge columns are always meadow.
- `EDGE_CLEAR` (green routes): marsh and tall grass off the last cells of an edge; `EDGE_PAINT`: rectangles painted last (trees and greenery keep off them;
  on dry routes they are applied before `dry_finish`). `route_features` `"terrain_edges"`: terrain rectangles that go in with `"terrain"`.
- All of the dry/route tilesets are demand-driven: after an edge change `build.py` may say "N transition tiles needed": compose that recipe, then build again; recompose =
  rebuild every map on the tileset (`orleans_route`: routes 1, 3, 5-13; `orleans_route_farm`: 15-17; `orleans_route_dry`: 23-24; `orleans_coast`: 2; `orleans_river`: 4).
- The approach paving break-up (`ap_` patches, routes 3, 4, 5, 14, 23) always shows as check.py seams: they are the designed break-up of the paving, not terrain cuts.
