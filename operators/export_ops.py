import bpy
import os
import json
from bpy_extras.io_utils import ExportHelper
from ..compile.compiler import compiler


class SN_OT_ExportAddon(bpy.types.Operator):
    bl_idname = "scripting_nodes.export_addon"
    bl_label = "Export Addon"
    bl_description = "Exports the active node tree as a python file"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    filepath: bpy.props.StringProperty(name="File Path", description="Filepath used for exporting the file", maxlen=1024, subtype='FILE_PATH')

    filename_ext = ".py"
    filter_glob: bpy.props.StringProperty(default='*.py', options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        name = context.space_data.node_tree.addon_name.lower().replace(" ","_") + ".py"
        self.filepath = os.path.join(self.filepath,name)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        text = compiler().get_export_file()
        with open(self.filepath, "w") as addon_file:
            addon_file.write(text.as_string())
        bpy.data.texts.remove(text)
        return {"FINISHED"}


class SN_OT_CopyCommand(bpy.types.Operator):
    bl_idname = "scripting_nodes.copy_command"
    bl_label = "Copy Command"
    bl_description = "Copies the command to post in the discord server"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    url: bpy.props.StringProperty(default="",options={"SKIP_SAVE"})
    price: bpy.props.StringProperty(default="Free",options={"SKIP_SAVE"})
    blender: bpy.props.BoolProperty(default=False,options={"SKIP_SAVE"})

    def execute(self, context):
        tree = context.space_data.node_tree

        addon_info = {
            "name": tree.addon_name,
            "description": tree.addon_description,
            "category": tree.addon_category,
            "author": tree.addon_author,
            "blender_version": list(tree.addon_blender),
            "addon_version": list(tree.addon_version),
            "url": self.url,
            "price": self.price,
            "blender": False
        }

        if self.url == "":
            addon_info["url"] = None
            addon_info["price"] = None

        bpy.context.window_manager.clipboard = json.dumps(addon_info)

        self.report({"INFO"},message="Copied successfully!")
        return {"FINISHED"}


class SN_OT_ExportToMarketplaceAddon(bpy.types.Operator):
    bl_idname = "scripting_nodes.export_to_marketplace"
    bl_label = "Export Addon To Marketplace"
    bl_description = "Exports the active node tree to the marketplace"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    url: bpy.props.StringProperty(default="",name="Addon URL",description="Enter the url to your addon here")
    price: bpy.props.StringProperty(default="Free",name="Addon Price",description="Enter the price of your addon here")
    blender: bpy.props.BoolProperty(default=False,options={"SKIP_SAVE"})

    upload_type: bpy.props.EnumProperty(name="Upload Type",items=[("DIRECT","Direct Upload","Upload the addon directly"),("URL","External Link","Provide an external url for your addon")])

    expand_1: bpy.props.BoolProperty(default=True,name="Expand")
    expand_2: bpy.props.BoolProperty(default=False,name="Expand")
    expand_3: bpy.props.BoolProperty(default=False,name="Expand")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return {"FINISHED"}
    
    def is_small_file(self):
        if bpy.data.filepath:
            if os.path.exists(bpy.data.filepath):
                return os.stat(bpy.data.filepath).st_size < 2000000
        return False

    def draw(self,context):
        box = self.layout.box()
        box.alert = True
        box.label(text="Please only upload your addon here if you think it could be interesting to others!",icon="ERROR")

        self.layout.separator()

        self.layout.prop(self,"upload_type",expand=True,text=" ")

        self.layout.separator()

        box = self.layout.box()
        box.prop(self,"expand_1",text="Step 1",emboss=False,toggle=True,icon="DISCLOSURE_TRI_DOWN" if self.expand_1 else "DISCLOSURE_TRI_RIGHT")
        if self.expand_1:
            col = box.column(align=True)
            col.label(text="    • Set your addons name, description, version, ...")
            col.label(text="    • If you want to update an addon use the same name")
            # if self.is_small_file():
            #     col.label(text="    • Select if you want to upload your node tree file as well")
            #     col.prop(self,"blender")
            # else:
            #     col.label(text="    • Reduce your file size to max. 2MB to upload the blend file as well")

        self.layout.separator()

        box = self.layout.box()
        box.prop(self,"expand_2",text="Step 2",emboss=False,toggle=True,icon="DISCLOSURE_TRI_DOWN" if self.expand_2 else "DISCLOSURE_TRI_RIGHT")
        if self.expand_2:
            col = box.column(align=False)

            if self.upload_type == "DIRECT":
                col.label(text="    • Go in the #addon-market channel on discord and post the following:")
                row = col.row(align=True)
                split = row.split(factor=0.03)
                split.label(text=" ")
                split.operator("scripting_nodes.copy_command",text="Click To Copy!",icon="COPYDOWN")
                row.operator("wm.url_open",text="",icon_value=bpy.context.scene.sn_icons[ "discord" ].icon_id).url = "https://discord.com/invite/NK6kyae"
                row.label(text=" ")
                col.separator()
                col.label(text="    • You will be asked to upload your addon. Export it and do so.")

            elif self.upload_type == "URL":
                row = col.row()
                row.label(text="    • Paste the link to your addon in here:")
                row.prop(self,"url", text="")
                col.separator()
                row = col.row()
                row.label(text="    • Enter the price of your addon here:")
                row.prop(self,"price", text="")

        if self.upload_type == "URL":
            self.layout.separator()

            box = self.layout.box()
            box.prop(self,"expand_3",text="Step 3",emboss=False,toggle=True,icon="DISCLOSURE_TRI_DOWN" if self.expand_3 else "DISCLOSURE_TRI_RIGHT")
            if self.expand_3:
                col = box.column(align=False)
                col.label(text="    • Go in the #addon-market channel on discord and post the following:")
                row = col.row(align=True)
                split = row.split(factor=0.03)
                split.label(text=" ")
                op = split.operator("scripting_nodes.copy_command",text="Click To Copy!",icon="COPYDOWN")
                op.url = self.url
                op.price = self.price
                row.operator("wm.url_open",text="",icon_value=bpy.context.scene.sn_icons[ "discord" ].icon_id).url = "https://discord.com/invite/NK6kyae"
                row.label(text=" ")


    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=500)
