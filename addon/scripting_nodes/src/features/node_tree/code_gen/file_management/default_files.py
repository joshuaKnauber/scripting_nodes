import os


def create_default_files(addon_path):
    # create init file
    with open(os.path.join(addon_path, "__init__.py"), "w") as f:
        _write_init_file(f)


def _write_init_file(init_file):
    init_file.write("# init file")
