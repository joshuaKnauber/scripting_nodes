import bpy
from ...lib.utils.node_tree.scripting_node_trees import node_by_id
from .generation import (
    start_generation,
    is_generating,
    request_stop,
    get_generating_node_id,
    get_next_response,
)


class SNA_OT_ScriptSendMessage(bpy.types.Operator):
    """Send a message to the AI for this script node"""

    bl_idname = "sna.script_send_message"
    bl_label = "Send Message"
    bl_options = {"REGISTER", "INTERNAL"}

    node_id: bpy.props.StringProperty()

    _timer = None
    _node = None
    _current_response = ""

    def execute(self, context):
        node = node_by_id(self.node_id)
        if not node:
            return {"CANCELLED"}

        # Check if already generating
        if is_generating():
            self.report({"WARNING"}, "Already generating a response")
            return {"CANCELLED"}

        message_text = node.ai_message_input.strip()
        if not message_text:
            self.report({"WARNING"}, "Please enter a message")
            return {"CANCELLED"}

        # Add the user message to the list
        messages = node.get_ai_messages()
        messages.append({"role": "user", "content": message_text})
        node.set_ai_messages(messages)

        # Clear the input
        node.ai_message_input = ""

        # Store references
        self._node = node
        self._current_response = ""

        # Add an empty assistant message that we'll update
        messages = node.get_ai_messages()
        messages.append({"role": "assistant", "content": "..."})
        node.set_ai_messages(messages)

        # Start generation in background thread
        start_generation(node, message_text)

        # Start modal timer
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.05, window=context.window)
        wm.modal_handler_add(self)

        # Force UI redraw
        for area in context.screen.areas:
            area.tag_redraw()

        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if event.type == "TIMER":
            # Check for new response data from the queue
            response, is_done = get_next_response()

            if response is not None:
                self._current_response = response
                # Update the last message with the response
                messages = self._node.get_ai_messages()
                if messages and messages[-1]["role"] == "assistant":
                    messages[-1]["content"] = response
                    self._node.set_ai_messages(messages)

                # Force UI redraw
                for area in context.screen.areas:
                    area.tag_redraw()

            if is_done:
                # Generation complete
                self._cleanup(context)
                return {"FINISHED"}

            return {"RUNNING_MODAL"}

        elif event.type == "ESC":
            # User pressed escape - stop generation
            request_stop()
            return {"RUNNING_MODAL"}

        return {"PASS_THROUGH"}

    def _cleanup(self, context):
        """Clean up timer and state."""
        if self._timer:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None
        self._node = None
        self._current_response = ""

        # Force UI redraw
        for area in context.screen.areas:
            area.tag_redraw()

    def cancel(self, context):
        """Handle operator cancellation."""
        request_stop()
        self._cleanup(context)


class SNA_OT_ScriptStopGeneration(bpy.types.Operator):
    """Stop the current AI generation"""

    bl_idname = "sna.script_stop_generation"
    bl_label = "Stop Generation"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        request_stop()
        return {"FINISHED"}


class SNA_OT_ScriptClearMessages(bpy.types.Operator):
    """Clear all AI messages for this script node"""

    bl_idname = "sna.script_clear_messages"
    bl_label = "Clear Messages"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_id: bpy.props.StringProperty()

    def execute(self, context):
        node = node_by_id(self.node_id)
        if not node:
            return {"CANCELLED"}

        node.set_ai_messages([])
        return {"FINISHED"}
