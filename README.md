# blender_visual_scripting_addon
Visual Scripting addon for blender with nodes


TODO
- You can't access nested blend data !!!
- You can't access some blender properties (is that ok? improve get data scriptline instead?)

- could get blend data from realtime stuff and then freeze nodes. you can only access things that exist right now and can then abstract for addon


## Tasks
### Interface
- [X] Display Property Node
- [X] Generate Dynamic Enum Items Node (Fix imperative)
- [ ] Menu Nodes
- [X] Split Node
- [ ] Button Node (Custom Operators)
- [ ] Interface Functions
- [X] If Interface (& Program with dropdown)
- [X] For Interface (& Program with dropdown)
- [X] Repeat Interface (& Program with dropdown)
- [X] Prop Search
- [X] UI List

### Blend Data
- [ ] Get Data Node
- [ ] Set Data Node
- [ ] bpy.data Nodes
- [ ] bpy.context Nodes
- [ ] Consider missing blend data

### Program
- [ ] Operator Node
- [ ] Run Operator (Template from Button)
- [X] Functions
- [ ] App Handlers
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
- [ ] Property source and name split when there is brackets at the end


read items in blend file node