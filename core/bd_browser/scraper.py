import bpy
import json
import os
import threading
import sys

BLENDER_DATA = {}  # stored scraped blender data
BLENDER_OPERATORS = {}  # stored scraped blender operators


def _debug_to_json(data, convert_paths=True):
    if convert_paths:
        for key, value in data.items():
            data[key]["paths"] = list(value["paths"])
    path = os.path.join(os.path.dirname(__file__), "debug.json")
    with open(path, "w") as write_file:
        json.dump(data, write_file, indent=2)


def start_threaded():
    # thread = threading.Thread(target=store_blender_data)
    # thread.start()
    store_blender_data()


def store_blender_data():
    global BLENDER_DATA
    global BLENDER_OPERATORS

    BLENDER_DATA = scrape_properties()
    BLENDER_OPERATORS = scrape_operators()


def scrape_properties():
    scraped = {}
    max_depth = 10
    max_indexed = 1  # TODO index one max and allow to scrape specific one?
    blocklist = ["bl_rna", "rna_type", "original", "depsgraph", "blend_data"]

    def scrape_data(data, path, depth=0):
        if not data:
            return

        # add data to scraped
        def add_data(identifier, name, description, path, type, last_value):
            if identifier not in scraped:
                # TODO data types, default values, subtypes, enum options
                scraped[identifier] = {
                    "name": name,
                    "description": description,
                    "paths": set(),
                    "type": type,
                    "last_value": str(last_value),
                }
            if path not in scraped[identifier]["paths"]:
                scraped[identifier]["paths"].add(path)

        data_id = str(data.bl_rna.as_pointer())
        add_data(
            data_id,
            data.bl_rna.name,
            data.bl_rna.description,
            path,
            "COLLECTION" if hasattr(data, "__iter__") else "POINTER",
            data,
        )

        # stop at max depth
        if depth >= max_depth:
            return

        # add properties to scraped
        for prop in data.bl_rna.properties:
            if not prop.identifier in blocklist:
                add_data(
                    data_id + str(prop.as_pointer()),
                    prop.name,
                    prop.description,
                    f"{path}.{prop.identifier}",
                    prop.type,
                    getattr(data, prop.identifier),
                )

        # add bl_rna children to scraped
        for attr in dir(data):
            if hasattr(data, attr) and attr not in blocklist:
                attr_data = getattr(data, attr)
                if hasattr(attr_data, "bl_rna"):
                    scrape_data(attr_data, f"{path}.{attr}", depth + 1)

        # add indexed children to scraped
        if hasattr(data, "__iter__") and getattr(data, "__iter__", False):
            for i, item in enumerate(data):
                if i >= max_indexed:
                    break
                scrape_data(item, f"{path}[{i}]", depth + 1)

        # TODO functions

    # scrape
    scrape_data(bpy.data, "bpy.data")
    scrape_data(bpy.context, "bpy.context")

    _debug_to_json(scraped)
    return scraped


def scrape_operators():
    operators = {}
    for category in dir(bpy.ops):
        for op in dir(getattr(bpy.ops, category)):
            operator = getattr(getattr(bpy.ops, category), op)
            if hasattr(operator, "get_rna_type"):
                operator = operator.get_rna_type()
                operators[f"{category}.{op}"] = {
                    "name": (
                        operator.name if operator.name else op.replace("_", " ").title()
                    ),
                    "description": operator.description,
                }
    # _debug_to_json(operators, convert_paths=False)
    return operators
