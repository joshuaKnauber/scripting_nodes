import bpy
import os


def watch_script_changes():
    bpy.app.timers.register(timer_script_update)


def unwatch_script_changes():
    if bpy.app.timers.is_registered(timer_script_update):
        bpy.app.timers.unregister(timer_script_update)


last_updates = {
    # '{static_uid;filename}': 'last_save_time' 
}

def update_script_nodes(update_blender_always=False):
    for ntree in bpy.data.node_groups:
        if ntree.bl_idname == "ScriptingNodesTree":
            for node in ntree.node_collection("SN_RunScriptNode").nodes:
                path = ""
                if node.source == "BLENDER":
                    if node.script and update_blender_always:
                        node._evaluate(bpy.context)
                    elif node.script and node.script.filepath:
                        path = node.script.filepath
                elif node.source == "EXTERNAL":
                    node_path = eval(node.inputs['Script Path'].python_value)
                    if node_path:
                        path = bpy.path.abspath(node_path)

                if path and os.path.exists(path):
                    key = f"{node.static_uid};{path}"
                    time = os.path.getmtime(path)
                    if not key in last_updates:
                        last_updates[key] = time
                        node._evaluate(bpy.context)
                    else:
                        if last_updates[key] != time:
                            last_updates[key] = time
                            node._evaluate(bpy.context)


def timer_script_update():
    update_script_nodes()
    return 2