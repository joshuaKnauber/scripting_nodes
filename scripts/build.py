import os
import shutil


def build(version: str):
    # builds folder
    builds_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "builds")
    if not os.path.exists(builds_path):
        os.makedirs(builds_path)

    # build folder
    build_name = f"scripting_nodes_{version}"
    build_path = os.path.join(builds_path, build_name)

    if os.path.exists(build_path):
        shutil.rmtree(build_path)
    os.makedirs(build_path)

    # copy files
    src_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "addon", "scripting_nodes"
    )
    shutil.copytree(src_path, os.path.join(build_path, "scripting_nodes"))

    # zip
    zip_path = os.path.join(builds_path, f"{build_name}.zip")
    if os.path.exists(zip_path):
        os.remove(zip_path)

    shutil.make_archive(build_path, "zip", build_path)

    # remove build folder
    shutil.rmtree(build_path)


if __name__ == "__main__":
    version = input("Build Version: ")
    build(version)
