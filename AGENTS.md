# Serpens - Visual Scripting Addon for Blender

A node-based visual scripting addon for Blender that allows users to create full Blender addons without writing code. The addon compiles node graphs into Python code in real-time.

## Overview

- **Name**: Serpens
- **Authors**: Joshua Knauber, Finn Knauber
- **Blender Version**: 5.0.0+
- **Version**: 3.5.0
- **License**: GPL-3.0

## Blender Python API Reference

This addon generates Python code that uses the Blender Python API (`bpy`). When working on this codebase, you'll need to understand the Blender API.

### Official Documentation

**Main API Docs**: https://docs.blender.org/api/current/index.html

### Key Modules

| Module | Purpose | URL |
|--------|---------|-----|
| `bpy.types` | All Blender types (Operator, Panel, Node, NodeSocket, PropertyGroup, etc.) | [Types](https://docs.blender.org/api/current/bpy.types.html) |
| `bpy.props` | Property definitions (StringProperty, IntProperty, CollectionProperty, etc.) | [Props](https://docs.blender.org/api/current/bpy.props.html) |
| `bpy.ops` | Operators (all built-in Blender operations) | [Operators](https://docs.blender.org/api/current/bpy.ops.html) |
| `bpy.data` | Access to all Blender data (objects, meshes, materials, node_groups, etc.) | [Data](https://docs.blender.org/api/current/bpy.data.html) |
| `bpy.context` | Current context (active object, selected objects, area, etc.) | [Context](https://docs.blender.org/api/current/bpy.context.html) |
| `bpy.utils` | Utility functions (register_class, previews, etc.) | [Utils](https://docs.blender.org/api/current/bpy.utils.html) |
| `bpy.app.handlers` | Application event handlers (load_post, save_pre, depsgraph_update, etc.) | [Handlers](https://docs.blender.org/api/current/bpy.app.handlers.html) |

### Important Types for This Addon

| Type | Description | Used For |
|------|-------------|----------|
| `bpy.types.Node` | Base class for custom nodes | All Serpens nodes inherit from this |
| `bpy.types.NodeSocket` | Base class for node sockets | All socket types inherit from this |
| `bpy.types.NodeTree` | Base class for node trees | `ScriptingNodesTree` inherits from this |
| `bpy.types.Operator` | Base class for operators | Generated operator code |
| `bpy.types.Panel` | Base class for UI panels | Generated panel code |
| `bpy.types.Menu` | Base class for menus | Generated menu code |
| `bpy.types.PropertyGroup` | Base class for custom property groups | Addon properties, variables |
| `bpy.types.UILayout` | Layout for drawing UI elements | Interface node code generation |
| `bpy.types.AddonPreferences` | Addon preferences panel | `SN_AddonPreferences` |

### Searching the API

When you need to find specific API information:

1. **Search by type name**: Go to `https://docs.blender.org/api/current/bpy.types.{TypeName}.html`
   - Example: `bpy.types.Operator` → https://docs.blender.org/api/current/bpy.types.Operator.html

2. **Search by operator**: Go to `https://docs.blender.org/api/current/bpy.ops.{category}.html`
   - Example: `bpy.ops.object` → https://docs.blender.org/api/current/bpy.ops.object.html

3. **Property types**: All property definitions are in `bpy.props`:
   - `StringProperty`, `IntProperty`, `FloatProperty`, `BoolProperty`
   - `EnumProperty`, `PointerProperty`, `CollectionProperty`
   - `IntVectorProperty`, `FloatVectorProperty`, `BoolVectorProperty`

### Common API Patterns Used in Generated Code

```python
# Registering a class
bpy.utils.register_class(MyOperator)
bpy.utils.unregister_class(MyOperator)

# Adding scene properties
bpy.types.Scene.my_prop = bpy.props.StringProperty()
del bpy.types.Scene.my_prop

# Operators
class MY_OT_example(bpy.types.Operator):
    bl_idname = "my.example"
    bl_label = "Example"
    def execute(self, context):
        return {'FINISHED'}

# Panels
class MY_PT_panel(bpy.types.Panel):
    bl_label = "My Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "My Tab"
    def draw(self, context):
        self.layout.label(text="Hello")

# UI Layout methods
layout.label(text="Text")
layout.prop(data, "property_name")
layout.operator("operator.idname")
row = layout.row()
col = layout.column()
box = layout.box()
split = layout.split()
```

### Version Notes

- This addon targets **Blender 5.0.0+**
- Always check API compatibility when using newer features
- The API docs have version switcher - ensure you're viewing the correct version

## Architecture

### Core Systems

```
scripting_nodes/
├── __init__.py              # Main addon entry point, registers everything
├── auto_load.py             # Auto-discovers and registers all Blender classes
├── handlers.py              # Blender app handlers (load, save, undo, etc.)
├── msgbus.py                # Message bus for name change subscriptions
├── utils.py                 # General utilities (python name generation, indentation, etc.)
│
├── node_tree/               # Node tree and socket system
│   ├── graphs/              # Node tree types
│   │   └── node_tree.py     # ScriptingNodesTree - main node tree type
│   ├── sockets/             # Socket types for node connections
│   │   ├── base_socket.py   # ScriptingSocket - base class for all sockets
│   │   ├── conversions.py   # Type conversion logic between socket types
│   │   └── *.py             # Individual socket types (string, boolean, float, etc.)
│   └── node_categories.py   # Node menu organization
│
├── nodes/                   # All node implementations
│   ├── base_node.py         # SN_ScriptingBaseNode - base class for all nodes
│   ├── compiler.py          # Code compilation and export logic
│   └── [Category]/          # Node categories (Events, Input, Interface, etc.)
│
├── addon/                   # Addon management
│   ├── properties/          # User-defined property system
│   ├── variables/           # Variable system
│   ├── settings/            # Property settings (types: boolean, string, etc.)
│   └── assets/              # Asset management
│
├── interface/               # UI components
│   ├── header/              # Node editor header
│   ├── menus/               # Context menus and presets
│   └── panels/              # Side panel UIs
│
├── settings/                # Addon settings and preferences
│   ├── addon_preferences.py # User preferences
│   ├── addon_properties.py  # Scene properties (SN_AddonProperties)
│   └── data_properties.py   # Data block properties
│
└── keymaps/                 # Keyboard shortcuts
```

### Data Flow

1. **Node Graph → Python Code**: Each node generates Python code via its `evaluate()` method
2. **Real-time Compilation**: Changes trigger `compile_addon()` which regenerates and re-registers the code
3. **Export**: Can export as single file or multi-file addon structure

## Key Classes

### Base Node (`nodes/base_node.py`)

All nodes inherit from `SN_ScriptingBaseNode`. Key attributes:

```python
class SN_ScriptingBaseNode:
    is_sn = True                    # Identifies Serpens nodes
    is_trigger = False              # True for nodes that start execution (Operator, Panel, etc.)
    node_color = "DEFAULT"          # Node color preset
    
    # Code output properties (read via self.code, set triggers recompile)
    code: str                       # Main node code
    code_import: str                # Import statements
    code_imperative: str            # Top-level code
    code_register: str              # Registration code
    code_unregister: str            # Unregistration code
    
    # Key methods to override:
    def on_create(self, context)    # Called when node is created
    def evaluate(self, context)     # Generate code - SET code properties here
    def draw_node(self, context, layout)  # Draw node UI
```

### Socket System (`node_tree/sockets/base_socket.py`)

All sockets inherit from `ScriptingSocket`. Key attributes:

```python
class ScriptingSocket:
    is_sn = True
    is_program = False              # True for Execute/Interface sockets
    dynamic = False                 # Auto-creates new socket when connected
    
    python_value: str               # The generated Python code for this socket's value
    default_value                   # The socket's default value (type-specific)
    
    def get_python_repr(self)       # Returns Python representation of default value
    def from_socket()               # Returns connected output socket (for inputs)
    def to_sockets()                # Returns connected input sockets (for outputs)
```

### Socket Types

| Socket | bl_idname | Purpose |
|--------|-----------|---------|
| Execute | `SN_ExecuteSocket` | Program flow (like "do this, then that") |
| Interface | `SN_InterfaceSocket` | UI layout connections |
| String | `SN_StringSocket` | Text data |
| Boolean | `SN_BooleanSocket` | True/False data |
| Integer | `SN_IntegerSocket` | Whole number data |
| Float | `SN_FloatSocket` | Decimal number data |
| Float Vector | `SN_FloatVectorSocket` | 2D/3D/4D vectors |
| Data | `SN_DataSocket` | Blender data references (objects, meshes, etc.) |
| List | `SN_ListSocket` | Python lists |
| Enum | `SN_EnumSocket` | Enumeration selections |
| Icon | `SN_IconSocket` | Blender icon identifiers |
| Property | `SN_PropertySocket` | Property references |
| Collection Property | `SN_CollectionPropertySocket` | Collection property references |

### Node Tree (`node_tree/graphs/node_tree.py`)

```python
class ScriptingNodesTree(bpy.types.NodeTree):
    bl_idname = "ScriptingNodesTree"
    
    variables: CollectionProperty   # Node tree-local variables
    node_refs: CollectionProperty   # References to nodes by type (for UI lists)
```

### Compiler (`nodes/compiler.py`)

Key functions:

```python
def compile_addon()                 # Recompiles and re-registers the entire addon
def format_single_file()            # Generates single-file addon code
def format_multifile()              # Generates multi-file addon structure
def get_trigger_nodes()             # Returns all nodes with is_trigger=True
```

## Creating New Nodes

### Template

```python
import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_YourNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_YourNode"
    bl_label = "Node Display Name"
    node_color = "DEFAULT"  # DEFAULT, PROGRAM, INTERFACE, STRING, etc.
    
    # Set is_trigger = True for nodes that start execution chains
    # is_trigger = True
    
    # Properties (always use update=SN_ScriptingBaseNode._evaluate)
    my_prop: bpy.props.StringProperty(
        name="My Property",
        update=SN_ScriptingBaseNode._evaluate
    )

    def on_create(self, context):
        """Create sockets when node is added"""
        self.add_string_input("Input")
        self.add_string_output("Output")

    def evaluate(self, context):
        """Generate Python code. Called automatically on changes."""
        # Read input values
        input_value = self.inputs["Input"].python_value
        
        # Set output values
        self.outputs["Output"].python_value = f'"{input_value}"'
        
        # Set code (only for program nodes)
        # self.code = "# Python code here"
        # self.code_import = "import something"

    def draw_node(self, context, layout):
        """Draw node UI"""
        layout.prop(self, "my_prop")
```

### Socket Creation Methods

```python
# Execute/Interface (program flow)
self.add_execute_input("Execute")
self.add_execute_output("Execute")
self.add_interface_input("Interface")
self.add_interface_output("Interface")

# Data types
self.add_string_input("Text")
self.add_boolean_input("Enabled")
self.add_integer_input("Count")
self.add_float_input("Value")
self.add_float_vector_input("Position")
self.add_data_input("Object")
self.add_list_input("Items")
self.add_enum_input("Option")
self.add_icon_input("Icon")

# Dynamic sockets (auto-add when connected)
self.add_dynamic_string_input("Text")
self.add_dynamic_execute_output("Execute")
```

## Code Generation Pattern

### For Data Nodes (no program flow)

```python
def evaluate(self, context):
    # Just set output python_value
    value = self.inputs["Input"].python_value
    self.outputs["Output"].python_value = f"str({value})"
```

### For Program Nodes (with execute sockets)

```python
def evaluate(self, context):
    # Get the next program output's code
    next_code = self.outputs["Execute"].python_value
    
    self.code = f'''
if True:
    print("Doing something")
    {self.indent(next_code, 1)}
'''
```

### For Trigger Nodes (Operator, Panel, etc.)

```python
def evaluate(self, context):
    execute_code = self.outputs["Execute"].python_value
    
    self.code = f'''
class MY_OT_operator(bpy.types.Operator):
    bl_idname = "my.operator"
    bl_label = "My Operator"
    
    def execute(self, context):
        {self.indent(execute_code, 2)}
        return {{"FINISHED"}}
'''
    
    self.code_register = "bpy.utils.register_class(MY_OT_operator)"
    self.code_unregister = "bpy.utils.unregister_class(MY_OT_operator)"
```

## Node Categories

Nodes are organized in folders under `nodes/`:

| Category | Purpose |
|----------|---------|
| `Debug/` | Debugging utilities (Print, Timestamp, etc.) |
| `Events/` | Event handlers (On Load, On Save, Keypress, etc.) |
| `Input/` | Data inputs (Blend Data, Scene Context, etc.) |
| `Interface/` | UI elements (Button, Label, Row, Column, etc.) |
| `Layout/` | Layout utilities (Portal) |
| `Program/` | Program flow (Operator, Function, Modal, etc.) |
| `Properties/` | Property manipulation |
| `Python/` | Raw Python scripting |
| `Snippets/` | Reusable node snippets |
| `Utilities/` | Utility nodes (Math, Text manipulation, etc.) |
| `Variables/` | Variable operations |
| `templates/` | Base node templates for inheritance |

## Important Utilities

### `utils.py`

```python
def get_python_name(name, replacement="")    # Convert to valid Python identifier
def unique_collection_name(name, ...)        # Generate unique name in collection
def normalize_code(code)                     # Strip and dedent code
def indent_code(code, indents, start=1)      # Indent code block
```

### Node Methods

```python
self.indent(code_or_list, indents)           # Indent code for insertion
self._evaluate(context)                       # Trigger reevaluation
self.convert_socket(socket, new_idname)      # Convert socket type
self.root_nodes                               # Get connected trigger nodes
self.node_tree                                # Get parent node tree
self.collection                               # Get node reference collection
```

## Addon Properties (Scene-level)

Access via `bpy.context.scene.sn`:

```python
sn = bpy.context.scene.sn
sn.addon_name           # Export addon name
sn.author               # Export author
sn.description          # Export description
sn.version              # Export version tuple
sn.blender              # Minimum Blender version
sn.is_exporting         # True during export
sn.debug_code           # Show generated code
sn.pause_reregister     # Pause recompilation
```

## Debugging Tips

1. **View Generated Code**: Enable `debug_code` in addon preferences to see `serpens_code_log` text block
2. **Debug Node Code**: Enable `debug_python_nodes` to show code on nodes
3. **Debug Sockets**: Enable `debug_python_sockets` to show socket values
4. **Error Log**: Check `serpens_error` text block for compilation errors
5. **Compile Time**: Enable `debug_compile_time` to see timing info in console

## Common Patterns

### Accessing Connected Node Data

```python
# From input socket, get connected output
from_socket = self.inputs["Data"].from_socket()
if from_socket:
    value = from_socket.python_value

# From output socket, get all connected inputs
to_sockets = self.outputs["Execute"].to_sockets()
for socket in to_sockets:
    socket.node._evaluate(context)
```

### Dynamic Socket Management

```python
def on_dynamic_socket_add(self, socket):
    """Called when a dynamic socket connection adds a new socket"""
    pass

def on_dynamic_socket_remove(self, index, is_output):
    """Called when a previously-dynamic socket is removed"""
    pass
```

### Reference Tracking

```python
# For nodes that reference other nodes (like "Run Operator")
ref_SN_OperatorNode: bpy.props.StringProperty()  # Store reference by name

def on_ref_update(self, node, data=None):
    """Called when a referenced node changes"""
    if self.ref_SN_OperatorNode == node.name:
        self._evaluate(bpy.context)
```

## Testing Changes

1. Make code changes
2. Save in Blender or trigger graph change
3. Check console for errors
4. Check `serpens_code_log` for generated code
5. Test the generated addon functionality

## Export Workflow

The addon can be exported as:
- **Single File**: One `.py` file with all code
- **Multi-File**: Folder structure with `__init__.py` and per-node-tree files
- **Extension**: With `blender_manifest.toml` for Blender 4.2+ extensions
