from ..base_socket import ScriptingBaseSocket


class ScriptingListSocket(ScriptingBaseSocket):
    bl_idname = "ScriptingListSocket"
    bl_label = "List"
    socket_shape = "SQUARE"
    color = (0.8, 0.5, 0.2, 1)

    def literal(self):
        return "[]"
