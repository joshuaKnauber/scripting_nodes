# blender_visual_scripting_addon
Visual Scripting addon for blender with nodes


## Tasks
### Interface
- [X] Display Property Node
- [X] Generate Dynamic Enum Items Node (Fix imperative)
- [ ] Menu Nodes
- [X] Split Node
- [X] Button Node (Custom Operators)
- [ ] Interface Functions
- [X] If Interface (& Program with dropdown)
- [X] For Interface (& Program with dropdown)
- [X] Repeat Interface (& Program with dropdown)
- [X] Prop Search
- [X] UI List

### Blend Data
- [X] Get Data Node
- [X] Set Data Node
- [X] bpy.data Nodes
- [X] bpy.context Nodes
- [X] Consider missing blend data

### Program
- [X] Operator Node
- [X] Run Operator (Template from Button)
- [X] Functions
- [X] App Handlers
- [ ] On Keypress

### Variables
- [X] Figure out variables

### General
- [ ] Save Addon
- [ ] Reimplement Missing Nodes
- [ ] Implement missing export differences
- [ ] Complete ToDo's (in code)
- [ ] Fix known bugs
- [ ] Packages and Snippets
- [ ] New Demo version
- [X] Msgbus
- [ ] Proper error logging
- [X] Enum Flag enum returns
- [X] Path icons on startup
- [X] Generate dynamic enum items on startup
- [x] Property source and name split when there is brackets at the end
- [X] Undo is real fucking slow


- [ ] scene collections output on collections node

    
[X] blender property node needs output for value with right type
[X] you need to be able to add, remove and move items for collection easily
[X] test other display nodes
[X] reload with correct context
[X] run blender function on blend data
[X] get non property data (hide property output and only show value?)
[X] do filters in browser
[] add back blend data input nodes
[] fix property output not showing properly when selecting collection as prop (blend to?, maybe fine?)
[X] paste in object prop -> shows objects as input and can't find default
[] geo node like props / attributes in blender property node -> display
[] delete enum items button on properties
[] enum items on function parameter
[] enum items from operator to button/run operator
[X] property update
[] replace space data in paths with screen/area stuff
[] operator/preference properties
[] changing nodes order doesn't hard compile
[] add node buttons
[] find node buttons
[] function and return parameters unique names
[X] property exists node -> takes parts and does and boolean to return if parts of prop exist or not