import bpy
import re


def get_python_name(name, replacement="", separator="_", lower=True):
    """Returns the given name as a valid python represention to use as variable names in scripts"""
    # format string
    name = name.replace(" ", separator)
    if lower:
        name = name.lower()

    # Remove invalid characters
    name = re.sub("[^0-9a-zA-Z_]", "", name)

    # Remove leading characters until we find a letter or underscore
    name = re.sub("^[^a-zA-Z]+", "", name)

    # return string
    if not name:
        return replacement
    return name


def unique_collection_name(name, default, name_list, separator="", includes_name=False):
    """Returns a unique name based for the given list of names"""
    if not name:
        name = default

    if name in name_list and includes_name:
        name_list.remove(name)

    if name in name_list:
        number = 1
        if len(name) > 3 and name[-3:].isdigit() and name[-4] == separator:
            name = name[:-4]
        while f"{name}{separator}{str(number).zfill(3)}" in name_list:
            number += 1

        name = f"{name}{separator}{str(number).zfill(3)}"
    return name
