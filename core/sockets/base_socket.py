import json

import bpy

from ...utils.code import indent_code, minimize_indents
from ..utils import sockets
from .data.convert import convert_types
from ..builder import builder


class ScriptingSocket:
    is_sn_socket = True
    initialized: bpy.props.BoolProperty(default=False)

    ### Socket Properties ###

    dynamic: bpy.props.BoolProperty(
        default=False,
        name="Dynamic",
        description="Enable or disable this socket",
    )

    @property
    def index(self):
        for i, sock in enumerate(
            self.node.outputs if self.is_output else self.node.inputs
        ):
            if sock == self:
                return i
        return -1

    @property
    def function_input_name(self):
        return f"inp_{self.index}"

    ### SOCKET LIFE CYCLE ###

    def init(self):
        self.on_create(bpy.context)

    # callback for when the socket is created
    def on_create(self, context):
        return

    def __init__(self):
        if not self.initialized:
            self.init()
            self.initialized = True

    ### HIDE SOCKET ###

    editable: bpy.props.BoolProperty(
        default=True,
        name="Enabled",
        description="Enable or disable this socket",
        update=lambda self, _: self.node.mark_dirty(),
    )
    show_editable: bpy.props.BoolProperty(
        default=False, name="Show Enabled", description="Show the enable icon"
    )

    def make_disabled(self):
        self.show_editable = True
        self.editable = False

    def make_enabled(self):
        self.show_editable = True
        self.editable = True

    ### SOCKET CONNECTIONS ###

    def has_next(self) -> bool:
        """Returns a boolean saying if the node is connected to other valid sockets"""
        return len(sockets.get_next_sockets(self)) > 0

    def get_next(self) -> list[bpy.types.NodeSocket]:
        """Returns a list of all valid connected sockets"""
        return sockets.get_next_sockets(self)

    ### SOCKET CODE ###

    def _python_value(self):
        raise NotImplementedError

    code: bpy.props.StringProperty(
        default="", name="Code", description="The code returned by this socket"
    )

    def _get_program_code(
        self, indent: int = 0, fallback: str = "", only_current: bool = False
    ):
        """Returns the code for a program output including potential dynamic outputs with the same name"""
        # get dynamic socket code
        if self.dynamic and not only_current:
            code = []
            # get individual socket code
            for out in self.node.outputs:
                if out.dynamic and out.name == self.name:
                    out_code = out._get_program_code(indent, "", True)
                    if out_code:
                        code.append(out_code)
            if len(code) == 0:
                return fallback
            return "\n".join(code)
        # get this sockets code
        else:
            if not self.has_next():
                return fallback
            ntree = (
                self.node.node_tree
                if getattr(self.node, "is_sn_node", False)
                else self.get_next()[0].node.node_tree
            )
            if not builder.IS_PROD_BUILD:
                return f"bpy.context.scene.sna._execute_node('{getattr(ntree, 'id', '')}', '{getattr(self.get_next()[0].node, 'id', '')}', locals(), globals())\n"
            return indent_code(
                minimize_indents(self.get_next()[0].node.get_code()), indent
            )

    def get_code(self, indent: int = 0, fallback: str = ""):
        if self.is_output:
            if getattr(self, "is_program", False):
                return self._get_program_code(indent, fallback)
            else:
                return self._python_value()
        elif not getattr(self, "is_program", False):
            if self.has_next():
                from_socket = self.get_next()[0]
                # Use function input name for group inputs, otherwise use the socket pythonified value
                value = (
                    from_socket._python_value()
                    if not from_socket.node.bl_idname == "NodeGroupInput"
                    else from_socket.function_input_name
                )
                return convert_types(value, from_socket, self)
            return self._python_value()
        return fallback

    meta: bpy.props.StringProperty(
        default="{}",
        name="Metadata",
        description="Stringified JSON metadata passed along by this socket",
    )

    def reset_meta(self):
        self.meta = "{}"

    def set_meta(self, key: str, value):
        meta = json.loads(self.meta)
        meta[key] = value
        # set meta on all dynamic outputs with the same name
        if self.dynamic:
            for out in self.node.outputs:
                if out.dynamic and out.name == self.name:
                    out.meta = json.dumps(meta)
        # set meta on this socket
        else:
            self.meta = json.dumps(meta)

    def get_meta(self, key: str, fallback, only_current: bool = False):
        if not only_current and not self.is_output and self.has_next():
            return self.get_next()[0].get_meta(key, fallback)
        meta = json.loads(self.meta)
        if key in meta:
            return meta[key]
        # Return socket function input name for group inputs
        print(self.node)
        if self.node.bl_idname == "NodeGroupInput":
            print("getting it")
            return self.function_input_name
        return fallback

    ### SOCKET UI ###

    def draw(self, context, layout, node, text):
        row = layout.row(align=False)
        row.alignment = "EXPAND" if not self.is_output else "RIGHT"
        # draw socket code
        if context.scene.sna.show_socket_code and self.node.select:
            row.label(text=self.get_code())
        # draw socket interface
        else:
            # draw main output interface
            if self.is_output:
                self.draw_socket(context, row, node, text)
            # draw dynamic interface
            if self.dynamic:
                subrow = row.row(align=True)
                op = subrow.operator(
                    "sna.add_dynamic_socket", text="", emboss=False, icon="ADD"
                )
                op.node = node.id
                op.is_output = self.is_output
                op.index = self.index
                if not sockets.is_only_with_name(self.node, self):
                    op = subrow.operator(
                        "sna.remove_socket", text="", emboss=False, icon="REMOVE"
                    )
                    op.node = node.id
                    op.is_output = self.is_output
                    op.index = self.index
            # draw hide/show interface
            if not self.is_output:
                if self.show_editable:
                    row.prop(
                        self,
                        "editable",
                        text="",
                        icon="HIDE_OFF" if self.editable else "HIDE_ON",
                        emboss=False,
                    )
                    if self.editable and not self.is_linked:
                        # draw main input interface
                        self.draw_socket(context, row, node, text)
                    else:
                        row.label(text=text)
                else:
                    self.draw_socket(context, row, node, text)

    # callback for drawing the socket
    def draw_socket(self, context, layout, node, text):
        raise NotImplementedError

    @classmethod
    def draw_color_simple(cls):
        return cls.get_color(None, None, None)

    def draw_color(self, context: bpy.types.Context, node: bpy.types.Node):
        col = self.get_color(context, node)
        enabled = self.editable or not self.show_editable
        color = [col[0], col[1], col[2], 1.0 if enabled else 0.5]
        return color

    def get_color(self, context, node):
        raise NotImplementedError
