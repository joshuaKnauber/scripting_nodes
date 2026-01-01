import os
import bpy


def ensure_default_files(addon_path):
    file_created = False
    addon_settings = bpy.context.scene.sna.addon

    # create init file
    init_file_path = os.path.join(addon_path, "__init__.py")
    if not os.path.exists(init_file_path):
        file_created = True
        with open(init_file_path, "w") as f:
            _write_init_file(f, addon_settings)

    # create auto load file
    autoload_file_path = os.path.join(addon_path, "auto_load.py")
    if not os.path.exists(autoload_file_path):
        file_created = True
        with open(autoload_file_path, "w") as f:
            _write_autoload_file(f)

    # create blender_manifest.toml for extension compatibility
    manifest_file_path = os.path.join(addon_path, "blender_manifest.toml")
    if not os.path.exists(manifest_file_path):
        file_created = True
        with open(manifest_file_path, "w") as f:
            _write_manifest_file(f, addon_settings)

    # create addon module init file
    addonmodule_init_file_path = os.path.join(addon_path, "addon", "__init__.py")
    if not os.path.exists(addonmodule_init_file_path):
        file_created = True
        with open(addonmodule_init_file_path, "w") as f:
            f.write("")

    return file_created


def _write_init_file(init_file, addon_settings):
    text = ""
    with open(os.path.join(os.path.dirname(__file__), "files", "init.txt")) as f:
        text = f.read()
    text = text.replace("$ADDON_NAME", addon_settings.addon_name)
    text = text.replace("$MODULE_NAME", addon_settings.module_name)
    init_file.write(text)


def _write_autoload_file(autoload_file):
    text = ""
    with open(os.path.join(os.path.dirname(__file__), "files", "auto_load.txt")) as f:
        text = f.read()
    autoload_file.write(text)


def _write_manifest_file(manifest_file, addon_settings):
    text = ""
    with open(
        os.path.join(os.path.dirname(__file__), "files", "blender_manifest.txt")
    ) as f:
        text = f.read()
    text = text.replace("$ADDON_NAME", addon_settings.addon_name)
    text = text.replace("$MODULE_NAME", addon_settings.module_name)
    manifest_file.write(text)
