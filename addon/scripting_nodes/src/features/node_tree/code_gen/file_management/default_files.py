import os


def ensure_default_files(addon_path):
    # create init file
    init_file_path = os.path.join(addon_path, "__init__.py")
    if not os.path.exists(init_file_path):
        with open(init_file_path, "w") as f:
            _write_init_file(f)


def _write_init_file(init_file):
    init_file.write("# init file")
