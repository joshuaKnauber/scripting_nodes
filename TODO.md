# V4 Feature Parity TODO

Tracking what's missing in `v4` compared to `main` branch. The v4 branch has a reorganized codebase structure (`addon/scripting_nodes/src/`) but is missing many node types and features.

## Legend
- [ ] Not started
- [x] Done in v4

---

## Nodes

### Events (entire category missing)
- [ ] After Render
- [ ] Before Exit
- [ ] Before Render
- [ ] Depsgraph Update
- [ ] Frame Change
- [ ] On Keypress (+ keypress_ops)
- [ ] On Load
- [ ] On Save
- [ ] Redo Event
- [ ] Undo Event

### Input — Blend Data (partially done)
- [x] Blend Data
- [x] Scene
- [ ] Blender Data (full data browser)
- [ ] Collections
- [ ] Meshes
- [ ] Objects

### Input — Data
- [x] Boolean, Color, Float, Integer, None, String, Vector
- [ ] Boolean Vector
- [ ] Float Vector
- [ ] Integer Vector
- [ ] List (standalone — v4 has List Operations under Data/List)

### Input — Geometry (entire subcategory missing)
- [ ] BMesh Data
- [ ] BMesh Edge Data
- [ ] BMesh Face Data
- [ ] BMesh Vertex Data
- [ ] Create Line Locations
- [ ] Create Quad Locations
- [ ] Create Triangle Locations
- [ ] Faces To Vertex Locations
- [ ] Mesh To BMesh
- [ ] Ngon To Triangle Locations
- [ ] Triangulate BMesh

### Input — Areas (entire subcategory missing)
- [ ] 2D View Zoom
- [ ] Area By Type
- [ ] Area Locations

### Input — Misc (missing)
- [ ] Addon Info
- [ ] Asset
- [ ] Get Edit Select Mode
- [ ] Icon
- [ ] Is Export
- [ ] Is In Mode
- [ ] Is Node Idname
- [ ] Is Object Type
- [ ] Named Icon
- [ ] Node Idname
- [ ] Random Color
- [ ] Random Number
- [ ] Scene Context
- [ ] Time

### Interface — Display Nodes (missing)
- [ ] Button (+ button_ops)
- [ ] Display Collection List
- [ ] Display Enum Item
- [ ] Display Icon
- [ ] Display Preview
- [ ] Display Property
- [ ] Display Search
- [ ] Display Serpens Shortcut
- [ ] Enum Map
- [ ] Icon Gallery
- [ ] Progress

### Interface — Layouts (partially done)
- [x] Panel
- [x] Subpanel
- [x] Box, Column, Row
- [x] Layout Reset, Layout Scale, Layout State
- [x] Property Layout
- [x] Label, Separator
- [x] Checkbox, Enum Menu, Number Field, Pointer Field, Textfield, Vector Field
- [ ] Menu
- [ ] Pie Menu
- [ ] Preferences
- [ ] Interface Function / Interface Function Run
- [ ] Add To Menu
- [ ] Add To Panel

### Interface — Sublayouts (missing)
- [ ] Copy Menu
- [ ] CopyPanel
- [ ] IfElse (interface)
- [ ] Layout Grid
- [ ] Layout Split
- [ ] Loop For (interface)
- [ ] Loop Repeat (interface)
- [ ] Popover
- [ ] Submenu

### Interface — Legacy Nodes
- [ ] All legacy compatibility nodes (low priority — may not be needed in v4)

### Layout
- [ ] Portal (+ portal_ops)

### Program (partially done)
- [x] If/Else
- [x] Print
- [x] Script
- [ ] Operator
- [ ] Run Operator

### Program — Drawing (entire subcategory missing)
- [ ] Start Drawing
- [ ] End Drawing
- [ ] Draw Circle
- [ ] Draw Line
- [ ] Draw Point
- [ ] Draw Quad
- [ ] Draw Text
- [ ] Draw Triangle

### Program — File Operations (missing)
- [ ] Append From File
- [ ] Create Folder
- [ ] Read Text File
- [ ] Write Text File

### Program — Functions (missing)
- [ ] Function
- [ ] Function Run
- [ ] Function Return

### Program — Modal (missing)
- [ ] Modal Operator
- [ ] Modal Event
- [ ] Modal Shortcut Pressed
- [ ] Modal Viewport Moved
- [ ] Return Modal
- [ ] Set Modal Cursor
- [ ] Text Size

### Program — Operations (mostly missing)
- [x] IfElse
- [ ] Break
- [ ] Enum Map
- [ ] Loop For
- [ ] Loop Repeat
- [ ] Open Menu
- [ ] Open Panel
- [ ] Open Pie Menu
- [ ] Operator From Shortcut
- [ ] Override Context
- [ ] Refresh View
- [ ] Report
- [ ] Set Edit Select
- [ ] Set Header Text
- [ ] Set Status Text

### Program — Timer (missing)
- [ ] Run In Intervals
- [ ] Run Multiple Times
- [ ] Run With Delay

### Properties (partially done)
- [x] Bool, Collection, Enum, Float, Float Vector, Int, Pointer, String properties
- [x] Get Property, Set Property
- [ ] Blender Property (generic)
- [ ] Serpens Property
- [ ] On Property Update
- [ ] Property Exists
- [ ] Run Property Function

### Properties — Collections (missing)
- [ ] Add Collection Item
- [ ] Collection Length
- [ ] Index Collection Property
- [ ] Is Index In Collection
- [ ] Move Collection Item
- [ ] Remove Collection Item

### Properties — Custom Properties (missing)
- [ ] Get Custom Property
- [ ] Has Custom Property
- [ ] Set Custom Property

### Properties — Enum (missing)
- [ ] Generate Dynamic Enum Items

### Python (entire category missing)
- [ ] Script
- [ ] Script Line
- [ ] Interface Script
- [ ] Interface Scriptline
- [ ] Run Script
- [ ] Get Data Scriptline
- [ ] Get Property Scriptline
- [ ] Get Attribute
- [ ] Has Attribute
- [ ] Set Attribute

### Snippets (missing)
- [ ] Snippet node (+ snippet_ops)

### Utilities (entire category missing — some equivalent nodes exist elsewhere in v4)
- [ ] Boolean Math (v4 has in Data/Boolean)
- [ ] Invert Boolean (v4 has in Data/Boolean)
- [ ] Compare (v4 has in Data)
- [ ] Switch Data (v4 has in Data)
- [ ] Switch Icons

### Utilities — Converter (missing)
- [ ] 3D Location To 2D
- [ ] Combine Vector
- [ ] Data To Icon
- [ ] Define Data Type
- [ ] Enum Set To List
- [ ] Radians Degrees
- [ ] Region To View
- [ ] Split Vector
- [ ] View To Region

### Utilities — Files (missing)
- [ ] Join Path
- [ ] List Blend Content
- [ ] List Directory Files
- [ ] Make Path Absolute
- [ ] Path Info

### Utilities — Text (partially covered)
- [x] Combine Strings (in Data/String)
- [x] Substring/Slice (in Data/String)
- [ ] Decode String
- [ ] Encode String
- [ ] Is In String
- [ ] Join Strings
- [ ] Map Strings (+ string_map_ops)
- [ ] Pad String
- [ ] Replace String
- [ ] Split String
- [ ] String Length
- [ ] Strip String

### Utilities — Math
- [x] Math, Clamp, Round, Vector Math (in Math category)
- [ ] Lofi (Special)

### Variables (partially done)
- [x] Get Variable, Set Variable, Local Variable, Global Variable
- [ ] Change Variable By
- [ ] Reset Variable
- [ ] Toggle Variable

### Variables — List Operations (missing)
- [ ] Add To List
- [ ] Index List
- [ ] Index Of Element
- [ ] Is In List
- [ ] List Length
- [ ] Remove From List
- [ ] Sort List

---

## Sockets (missing types)
- [x] Boolean, Float, Integer, String, List, Data, BlendData, Color, Vector
- [x] Execute (as Program), Interface, Logic
- [ ] Boolean Vector
- [ ] Float Vector
- [ ] Integer Vector
- [ ] Enum
- [ ] Enum Set (+ enum_ops)
- [ ] Collection Property
- [ ] Property
- [ ] Icon
- [ ] Reroute
- [ ] Socket ops (socket_ops)

---

## Features / Infrastructure

### Node Infrastructure
- [ ] Compiler (nodes/compiler.py — main's code generation approach)
- [ ] Node templates (PropertyNode, VariableReferenceNode, PropertyReferenceNode, data_ops)
- [ ] Node categories definition (node_tree/node_categories.py)
- [ ] Tutorial system (nodes/tutorial.py)

### Properties System (addon/properties/ in main)
- [ ] Property compiler (compiler_properties)
- [ ] Property basic/category/ops/utils
- [ ] Property settings types (boolean, collection, enum, float, group, integer, pointer, string)

### Variables System (addon/variables/ in main)
- [ ] Variable compiler (compiler_variables)
- [ ] Variable ops

### Assets System (addon/assets/ in main)
- [ ] Asset management (assets, asset_ops)

### Extensions / Marketplace
- [ ] Package ops (extensions/package_ops)
- [ ] Snippet ops (extensions/snippet_ops)
- [ ] Marketplace ops (node_tree/graphs/marketplace_ops)
- [ ] Graph exports (node_tree/graphs/export_ops)
- [ ] Graph category ops

### Interface / Panels
- [ ] Header (interface/header/) — console ops, header UI
- [ ] Menus — presets, right-click menu, snippets menu
- [ ] Panels — addon info, addon settings, assets, data search, explorer, graph panels, packages, properties panel, variables panel
- [ ] UI lists (asset, graph, property, variable)

### Settings
- [ ] Global search
- [ ] Updates checker
- [ ] Preset data
- [ ] EasyBPY integration
- [ ] Handle script changes
- [ ] Load markets

### Graph System
- [ ] Graph operations (node_tree/graphs/)
- [ ] Node references (node_tree/graphs/node_refs)
- [ ] Reference ops

### Keymaps
- [ ] Keymap ops (keymaps/keymap_ops)

---

## Notes
- The v4 branch has a completely restructured codebase. Nodes from main need to be adapted to the new architecture (relative imports, new base classes, new socket system, new code gen pipeline).
- Legacy nodes from main may not need porting — decide on backward compatibility strategy.
- Some main nodes may map to different v4 categories (e.g., main's Utilities/Boolean → v4's Data/Boolean).
- The v4 branch already has features not in main: AI integration, blend data indexer with fuzzy search.
