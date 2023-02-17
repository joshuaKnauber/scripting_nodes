import bpy


def live_variable_debug():
    try:
        for a in bpy.context.screen.areas:
            if a.type == "NODE_EDITOR":
                a.tag_redraw()
    except:
        pass
    return .1


def start_live_variable_debug():
    bpy.app.timers.register(live_variable_debug, persistent=False)

def stop_live_variable_debug():
    if bpy.app.timers.is_registered(live_variable_debug):
        bpy.app.timers.unregister(live_variable_debug)