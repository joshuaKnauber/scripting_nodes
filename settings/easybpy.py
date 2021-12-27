import bpy
import sys
import os



def check_easy_bpy_install():
    bpy.context.scene.sn.easy_bpy_path = ""
    for path in sys.path:
        if os.path.exists(path):
            for filename in os.listdir(path):
                if filename == "easybpy.py":
                    bpy.context.scene.sn.easy_bpy_path = os.path.join(path, filename)