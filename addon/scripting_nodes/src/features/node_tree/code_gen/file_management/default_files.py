import os
import bpy


def ensure_default_files(addon_path):
    # create init file
    init_file_path = os.path.join(addon_path, "__init__.py")
    if not os.path.exists(init_file_path):
        with open(init_file_path, "w") as f:
            _write_init_file(f)

    # create auto load file
    autoload_file_path = os.path.join(addon_path, "auto_load.py")
    if not os.path.exists(autoload_file_path):
        with open(autoload_file_path, "w") as f:
            _write_autoload_file(f)

    # create addon module init file
    addonmodule_init_file_path = os.path.join(addon_path, "addon", "__init__.py")
    if not os.path.exists(addonmodule_init_file_path):
        with open(addonmodule_init_file_path, "w") as f:
            f.write("")


def _write_init_file(init_file):
    text = ""
    with open(os.path.join(os.path.dirname(__file__), "files", "init.txt")) as f:
        text = f.read()
    text = text.replace("$ADDON_NAME", bpy.context.scene.sna.addon.addon_name)
    init_file.write(text)


def _write_autoload_file(autoload_file):
    text = ""
    with open(os.path.join(os.path.dirname(__file__), "files", "auto_load.txt")) as f:
        text = f.read()
    autoload_file.write(text)
