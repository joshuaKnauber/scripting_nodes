"""
Prototype: per-module reload in Blender.

Tests whether we can reload a SINGLE module of a fake "addon" without
disable/enable of the whole addon. This is the core technique we'd use
to replace dev mode with smart reloads.

To run: open this file in Blender's Text Editor and click Run Script.
Watch the System Console for output.

What it checks:
  1. After modifying tree_a.py and reloading only tree_a:
     - tree_a's class (Panel) gets re-registered with the new bl_label
     - tree_a's function returns the new value
  2. tree_b imports `from . import tree_a` and uses tree_a.get_message():
     - tree_b's reference to tree_a points to the NEW module
     - tree_b sees the new value (cross-module dependency tracked)
  3. tree_c does `from .tree_a import get_message` (top-level binding):
     - tree_c's `get_message` gets rebound to the new function

If all the "[verify]" lines show the v2 values, the approach works.
"""
import bpy
import sys
import os
import shutil
import importlib
import tempfile
import types

PROTO_DIR = os.path.join(tempfile.gettempdir(), "sn_reload_proto")
PKG_NAME = "sn_reload_proto"


def write_file(rel_path, content):
    full = os.path.join(PROTO_DIR, rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)


def setup_initial_files():
    """Create the test package on disk."""
    if os.path.exists(PROTO_DIR):
        shutil.rmtree(PROTO_DIR)
    os.makedirs(PROTO_DIR)

    write_file("__init__.py", "")

    write_file("tree_a.py", '''
import bpy

VERSION = "v1"

def get_message():
    return f"hello from tree_a {VERSION}"

class SN_PROTO_PT_TreeA(bpy.types.Panel):
    bl_idname = "SN_PROTO_PT_TreeA"
    bl_label = "Proto Tree A [v1]"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    def draw(self, context):
        self.layout.label(text=get_message())

def register():
    bpy.utils.register_class(SN_PROTO_PT_TreeA)

def unregister():
    bpy.utils.unregister_class(SN_PROTO_PT_TreeA)
''')

    # tree_b: module-reference style (`from . import tree_a`)
    write_file("tree_b.py", '''
import bpy
from . import tree_a

class SN_PROTO_PT_TreeB(bpy.types.Panel):
    bl_idname = "SN_PROTO_PT_TreeB"
    bl_label = "Proto Tree B"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    def draw(self, context):
        self.layout.label(text=f"B sees: {tree_a.get_message()}")

def register():
    bpy.utils.register_class(SN_PROTO_PT_TreeB)

def unregister():
    bpy.utils.unregister_class(SN_PROTO_PT_TreeB)
''')

    # tree_c: top-level binding style (`from .tree_a import get_message`)
    write_file("tree_c.py", '''
import bpy
from .tree_a import get_message

class SN_PROTO_PT_TreeC(bpy.types.Panel):
    bl_idname = "SN_PROTO_PT_TreeC"
    bl_label = "Proto Tree C"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    def draw(self, context):
        self.layout.label(text=f"C sees: {get_message()}")

def register():
    bpy.utils.register_class(SN_PROTO_PT_TreeC)

def unregister():
    bpy.utils.unregister_class(SN_PROTO_PT_TreeC)
''')


def initial_load():
    parent = os.path.dirname(PROTO_DIR)
    if parent not in sys.path:
        sys.path.insert(0, parent)

    importlib.import_module(PKG_NAME)
    tree_a = importlib.import_module(f"{PKG_NAME}.tree_a")
    tree_b = importlib.import_module(f"{PKG_NAME}.tree_b")
    tree_c = importlib.import_module(f"{PKG_NAME}.tree_c")

    tree_a.register()
    tree_b.register()
    tree_c.register()
    print("[setup] loaded + registered tree_a, tree_b, tree_c")


def cleanup():
    """Unregister everything and clear sys.modules."""
    for mod_name in [
        f"{PKG_NAME}.tree_c",
        f"{PKG_NAME}.tree_b",
        f"{PKG_NAME}.tree_a",
    ]:
        mod = sys.modules.get(mod_name)
        if mod and hasattr(mod, "unregister"):
            try:
                mod.unregister()
            except Exception as e:
                print(f"  cleanup unregister failed for {mod_name}: {e}")
    for name in list(sys.modules.keys()):
        if name == PKG_NAME or name.startswith(PKG_NAME + "."):
            del sys.modules[name]


def reload_module(module_name):
    """Per-module reload: unregister, re-import, register, rebind dependents."""
    full_name = f"{PKG_NAME}.{module_name}"
    old_mod = sys.modules.get(full_name)
    if old_mod is None:
        print(f"[reload] {full_name} not loaded")
        return None

    # 1. Run unregister on the old module
    if hasattr(old_mod, "unregister"):
        try:
            old_mod.unregister()
            print(f"[reload] unregistered {module_name}")
        except Exception as e:
            print(f"[reload] unregister failed: {e}")

    # 2. Snapshot old public attrs (excluding sub-modules like bpy)
    old_attrs = {
        k: v
        for k, v in vars(old_mod).items()
        if not k.startswith("_") and not isinstance(v, types.ModuleType)
    }

    # 3. Invalidate import caches and delete pyc so Python re-reads source
    pycache_dir = os.path.join(PROTO_DIR, "__pycache__")
    if os.path.isdir(pycache_dir):
        for f in os.listdir(pycache_dir):
            if f.startswith(f"{module_name}.cpython"):
                try:
                    os.remove(os.path.join(pycache_dir, f))
                except OSError:
                    pass
    importlib.invalidate_caches()

    # 4. Drop from sys.modules and re-import
    del sys.modules[full_name]
    new_mod = importlib.import_module(full_name)

    # 5. Re-register
    if hasattr(new_mod, "register"):
        try:
            new_mod.register()
            print(f"[reload] re-registered {module_name}")
        except Exception as e:
            print(f"[reload] register failed: {e}")

    # 6. Rebind dependent modules' references
    for dep_name, dep_mod in list(sys.modules.items()):
        if dep_mod is None or dep_mod is new_mod:
            continue
        if not dep_name.startswith(PKG_NAME + "."):
            continue
        for attr_name in list(vars(dep_mod).keys()):
            current = getattr(dep_mod, attr_name, None)
            # Case A: `from . import tree_a` -> dep_mod.tree_a is the old module
            if current is old_mod:
                setattr(dep_mod, attr_name, new_mod)
                print(f"[reload] rebound {dep_name}.{attr_name} = new module")
                continue
            # Case B: `from .tree_a import X` -> dep_mod.X is an old attribute
            if attr_name in old_attrs and current is old_attrs[attr_name]:
                new_val = getattr(new_mod, attr_name, None)
                if new_val is not None:
                    setattr(dep_mod, attr_name, new_val)
                    print(f"[reload] rebound {dep_name}.{attr_name} -> new {module_name}.{attr_name}")

    return new_mod


def modify_tree_a(version):
    write_file("tree_a.py", f'''
import bpy

VERSION = "{version}"

def get_message():
    return f"hello from tree_a {{VERSION}}"

class SN_PROTO_PT_TreeA(bpy.types.Panel):
    bl_idname = "SN_PROTO_PT_TreeA"
    bl_label = "Proto Tree A [{version}]"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    def draw(self, context):
        self.layout.label(text=get_message())

def register():
    bpy.utils.register_class(SN_PROTO_PT_TreeA)

def unregister():
    bpy.utils.unregister_class(SN_PROTO_PT_TreeA)
''')


def run_test():
    print("\n=== prototype: per-module reload ===\n")
    cleanup()
    setup_initial_files()
    initial_load()

    tree_a = sys.modules[f"{PKG_NAME}.tree_a"]
    tree_b = sys.modules[f"{PKG_NAME}.tree_b"]
    tree_c = sys.modules[f"{PKG_NAME}.tree_c"]

    print(f"\n[verify v1] tree_a.get_message()  = {tree_a.get_message()!r}")
    print(f"[verify v1] tree_b sees:           {tree_b.tree_a.get_message()!r}")
    print(f"[verify v1] tree_c sees:           {tree_c.get_message()!r}")
    print(f"[verify v1] Panel A bl_label       = {bpy.types.SN_PROTO_PT_TreeA.bl_label!r}")

    print("\n--- modifying tree_a.py to v2 on disk ---")
    modify_tree_a("v2")

    print("\n--- reloading ONLY tree_a ---")
    new_tree_a = reload_module("tree_a")

    print("\n=== results ===")
    print(f"[verify v2] tree_a.get_message()  = {new_tree_a.get_message()!r}")
    tree_b = sys.modules[f"{PKG_NAME}.tree_b"]
    tree_c = sys.modules[f"{PKG_NAME}.tree_c"]
    print(f"[verify v2] tree_b sees:           {tree_b.tree_a.get_message()!r}")
    print(f"[verify v2] tree_c sees:           {tree_c.get_message()!r}")
    print(f"[verify v2] Panel A bl_label       = {bpy.types.SN_PROTO_PT_TreeA.bl_label!r}")
    print(f"[verify v2] tree_b.tree_a is new?  {tree_b.tree_a is new_tree_a}")

    print("\n=== expected ===")
    print("All [verify v2] lines should show 'v2' values.")
    print("If yes, per-module reload + cross-module rebinding works.")
    print("\n(Panels are registered in Render properties of the Properties editor.)")


run_test()
