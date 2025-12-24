import bpy
from .base_socket import ScriptingSocket


class SN_StringSocket(bpy.types.NodeSocket, ScriptingSocket):

    bl_idname = "SN_StringSocket"
    group = "DATA"
    bl_label = "String"

    default_python_value = "''"
    default_prop_value = ""

    string_repr_warning: bpy.props.BoolProperty(
        default=False,
        name="Potential Error Warning!",
        description="You're using two types of quotes in your string! Be aware that this will cause syntax errors if you don't change ' to \\'",
    )

    def _calc_string_repr_warning(self, raw: str) -> bool:
        """Pure computation: returns True if string contains both ' and \"."""
        return ("'" in raw) and ('"' in raw)

    def get_python_repr(self):
        # DO NOT write to self.string_repr_warning here (Blender 5.0 read-only context)
        value = getattr(self, self.subtype_attr)

        # normalize dir path trailing backslash for Windows
        if self.subtype == "DIR_PATH" and value and value[-1] == "\\":
            value = value[:-1]

        # Quote wrapping logic
        if "'" in value and not '"' in value:
            wrapped = f'"{value}"'
        elif '"' in value and not "'" in value:
            wrapped = f"'{value}'"
        else:
            # if both quotes exist, we still return single-quoted string as before
            wrapped = f"'{value}'"

        if self.subtype == "NONE":
            return wrapped
        return f"r{wrapped}"

    default_value: bpy.props.StringProperty(
        name="Value",
        description="Value of this socket",
        get=ScriptingSocket._get_value,
        set=ScriptingSocket._set_value,
    )

    def _get_file_path(self):
        """Returns the file path value stored on the parent node"""
        storage_key = self._get_socket_storage_key("_value_file_path")
        return self.node.get(storage_key, "")

    def _set_file_path(self, value):
        """Sets the file path value on the parent node"""
        new_path = bpy.path.abspath(value)
        if new_path and new_path[-1] == "\\":
            new_path = new_path[:-1]
        storage_key = self._get_socket_storage_key("_value_file_path")
        self.node[storage_key] = new_path
        self._update_value(None)

    def update_file_path(self, context):
        # The set callback handles the path normalization
        pass

    value_file_path: bpy.props.StringProperty(
        name="Value",
        description="Value of this socket",
        subtype="FILE_PATH",
        get=_get_file_path,
        set=_set_file_path,
        update=update_file_path,
    )

    def _get_dir_path(self):
        """Returns the directory path value stored on the parent node"""
        storage_key = self._get_socket_storage_key("_value_dir_path")
        return self.node.get(storage_key, "")

    def _set_dir_path(self, value):
        """Sets the directory path value on the parent node"""
        new_path = bpy.path.abspath(value)
        if new_path and new_path[-1] == "\\":
            new_path = new_path[:-1]
        storage_key = self._get_socket_storage_key("_value_dir_path")
        self.node[storage_key] = new_path
        self._update_value(None)

    def update_dir_path(self, context):
        # The set callback handles the path normalization
        pass

    value_dir_path: bpy.props.StringProperty(
        name="Value",
        description="Value of this socket",
        subtype="DIR_PATH",
        get=_get_dir_path,
        set=_set_dir_path,
        update=update_dir_path,
    )

    subtypes = ["NONE", "FILE_PATH", "DIR_PATH"]
    subtype_values = {
        "NONE": "default_value",
        "FILE_PATH": "value_file_path",
        "DIR_PATH": "value_dir_path",
    }

    def get_color(self, context, node):
        return (0.44, 0.7, 1)

    def draw_socket(self, context, layout, node, text, minimal=False):
        if self.is_output or self.is_linked:
            layout.label(text=text)
            return

        # Compute warning on the fly (no property write needed)
        raw = getattr(self, self.subtype_attr)
        warn = self._calc_string_repr_warning(raw)

        if warn:
            # draw an icon-only label; don't use a property toggle here
            layout.label(text="", icon="ERROR")

        layout.prop(self, self.subtype_attr, text=text)
