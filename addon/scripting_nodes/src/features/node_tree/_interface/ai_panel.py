import bpy
from ....lib.editor.editor import is_sn_editor
from ...settings.addon_settings.preferences import get_preferences
from ...ai.generation import is_generating, get_generating_node_id


def draw_warning(layout, title, message, operator=None, op_text=None, op_icon="NONE"):
    """Draw a consistent warning box."""
    box = layout.box()
    col = box.column(align=True)
    col.label(text=title, icon="ERROR")
    col.label(text=message)
    if operator:
        col.separator()
        return col.operator(operator, text=op_text, icon=op_icon)
    return None


def draw_info(layout, message):
    """Draw a consistent info message."""
    box = layout.box()
    box.label(text=message, icon="INFO")


class SNA_PT_AI(bpy.types.Panel):
    bl_idname = "SNA_PT_AI"
    bl_label = "Assistant"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 5

    @classmethod
    def poll(cls, context):
        return is_sn_editor(context)

    def draw(self, context):
        layout = self.layout
        prefs = get_preferences()

        if not prefs.ai_api_key:
            op = draw_warning(
                layout,
                "API key not configured",
                "Set it in addon preferences",
                operator="preferences.addon_show",
                op_text="Open Preferences",
                op_icon="PREFERENCES",
            )
            if op:
                op.module = prefs.bl_idname
            return

        # Get the active node if it's a Script node
        node = context.active_node
        if node and node.bl_idname == "SNA_Node_Script":
            # Check if a text file is selected
            has_script = (
                node.source_type == "INTERNAL" and node.text_block is not None
            ) or (node.source_type == "EXTERNAL" and node.filepath)

            if not has_script:
                draw_warning(
                    layout,
                    "No script selected",
                    "Add a text file to the Script node",
                )
                return

            # Check if currently generating for this node
            currently_generating = (
                is_generating() and get_generating_node_id() == node.id
            )

            # Message input at the top
            if currently_generating:
                # Show stop button when generating
                row = layout.row(align=True)
                row.enabled = False
                row.prop(node, "ai_message_input", text="")
                layout.operator(
                    "sna.script_stop_generation", text="Stop", icon="CANCEL"
                )
            else:
                # Message input with submit button
                row = layout.row(align=True)
                row.prop(node, "ai_message_input", text="")
                op = row.operator("sna.script_send_message", text="", icon="PLAY")
                op.node_id = node.id

            # Show messages for the active script node (newest first)
            messages = node.get_ai_messages()
            if messages:
                if not currently_generating:
                    op = layout.operator(
                        "sna.script_clear_messages", text="Clear Chat", icon="X"
                    )
                    op.node_id = node.id

                box = layout.box()
                # Reverse to show newest messages first, limit to 3
                reversed_messages = list(reversed(messages))
                visible_messages = reversed_messages[:3]
                hidden_count = len(reversed_messages) - 3

                for msg in visible_messages:
                    msg_box = box.box()
                    # Header row with icon
                    header = msg_box.row()
                    icon = "USER" if msg["role"] == "user" else "SCRIPT"
                    header.label(
                        text="You" if msg["role"] == "user" else "AI", icon=icon
                    )

                    # Wrap text to multiple lines, respecting line breaks
                    content = msg["content"].strip()
                    col = msg_box.column(align=True)
                    # Approximate characters per line in the panel
                    chars_per_line = 40

                    # Split by line breaks first
                    for line in content.split("\n"):
                        if not line.strip():
                            # Skip empty lines
                            continue
                        # Then wrap each line by words
                        words = line.split()
                        current_line = ""
                        for word in words:
                            if len(current_line) + len(word) + 1 <= chars_per_line:
                                current_line += (" " if current_line else "") + word
                            else:
                                if current_line:
                                    col.label(text=current_line)
                                current_line = word
                        if current_line:
                            col.label(text=current_line)

                # Show hidden message count
                if hidden_count > 0:
                    row = box.row()
                    row.alignment = "CENTER"
                    row.label(
                        text=f"{hidden_count} more message{'s' if hidden_count > 1 else ''}..."
                    )
            else:
                # Hint when no messages
                box = layout.box()
                col = box.column(align=True)
                col.label(text="Ask the AI to help you write code:", icon="INFO")
                col.label(text="• 'Add a cube at the 3D cursor'")
                col.label(text="• 'Loop through selected objects'")
                col.label(text="• 'Fix the error in my script'")
        else:
            draw_info(layout, "Select a Script node")
