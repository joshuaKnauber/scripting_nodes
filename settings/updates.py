import bpy
import os
import requests
import json
from datetime import date


message = []

class SN_OT_MessageUpdate(bpy.types.Operator):
    bl_idname = "sn.update_message"
    bl_label = "-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -"
    bl_description = "Update Message"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    def execute(self, context): 
        with open(os.path.join(os.path.dirname(__file__),"update_log.json"),"w") as update_log:
            update_log.write(json.dumps({"last_check":str(date.today())},indent=4))       
        return {"FINISHED"}
    
    def draw(self,context):
        global message
        layout = self.layout

        layout.label(text="Serpens Update available!",icon="FUND")
        layout.label(text="A free update is out.")
        layout.label(text="You can go and download it right now!")
        
        if message:
            layout.label(text="This update includes:")
            for m in message:
                layout.label(text="  • " + m)
        layout.label(text="-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -")
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)



def should_update():
    should_update = False
    with open(os.path.join(os.path.dirname(__file__),"update_log.json"),"r") as update_log:
        update_log = json.loads(update_log.read())
        if not update_log["last_check"] == str(date.today()):
            should_update = True
    return should_update

        
        
def exists_newer_version(version,current):
    needs_update = False
    if version[0] > current[0]:
        needs_update = True
    elif version[0] == current[0]:
        if version[1] > current[1]:
            needs_update = True
        elif version[1] == current[1]:
            if version[2] > current[2]:
                needs_update = True
    return needs_update


def check_serpens_updates(current_version):
    global message
    if should_update():
        url = "https://raw.githubusercontent.com/joshuaKnauber/serpens_addon_market/main/version.json"

        try:
            content = requests.get(url).json()
            version = tuple(content["version"])
            if exists_newer_version(version, current_version):
                message = content["content"]
                bpy.ops.sn.update_message("INVOKE_DEFAULT")

        except ValueError:
            print("Couldn't check for Serpens updates!")