import bpy


from . import addon_errors, addon_info, addon_prints, addon_settings, graph_panels, snippets


classes = [addon_errors.SN_OT_SelectNode,
            addon_errors.SN_PT_AddonErrorPanel,
            addon_info.SN_PT_AddonInfoPanel,
            addon_prints.SN_OT_RemovePrint,
            addon_prints.SN_PT_AddonPrintPanel,
            addon_settings.SN_PT_AddonSettingsPanel,
            graph_panels.SN_OT_GetPythonName,
            graph_panels.SN_OT_QuestionMarkName,
            graph_panels.SN_PT_GraphPanel,
            graph_panels.SN_PT_VariablePanel,
            graph_panels.SN_PT_PropertyPanel,
            graph_panels.SN_PT_IconPanel,
            graph_panels.SN_PT_AssetsPanel,
            snippets.SN_PT_SnippetPanel]


def register():
    global classes
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    global classes
    for cls in classes:
        bpy.utils.unregister_class(cls)