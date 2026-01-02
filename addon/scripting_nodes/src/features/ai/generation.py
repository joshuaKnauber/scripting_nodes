"""AI generation module for Scripting Nodes.

Uses httpx directly to call OpenAI-compatible APIs with tool support.
Uses threading to avoid blocking the Blender UI.
"""

import json
import threading
import queue
import bpy
import httpx

from ..settings.addon_settings.preferences import get_preferences


# Global state for generation
_generation_state = {
    "is_generating": False,
    "should_stop": False,
    "current_node_id": None,
    "current_node": None,
    "response_queue": None,
    "thread": None,
}


def is_generating() -> bool:
    """Check if generation is currently in progress."""
    return _generation_state["is_generating"]


def get_generating_node_id() -> str | None:
    """Get the node ID currently being generated for."""
    return _generation_state["current_node_id"]


def request_stop():
    """Request the current generation to stop."""
    _generation_state["should_stop"] = True


def get_next_response() -> tuple[str | None, bool]:
    """Get the next response chunk from the queue.

    Returns:
        tuple: (response_text, is_done) - response_text is None if no data available
    """
    if _generation_state["response_queue"] is None:
        return None, True

    try:
        item = _generation_state["response_queue"].get_nowait()
        if item is None:
            # None signals completion
            return None, True
        return item, False
    except queue.Empty:
        return None, False


def _get_api_config():
    """Get the API configuration based on user preferences."""
    prefs = get_preferences()
    provider = prefs.ai_provider
    api_key = prefs.ai_api_key
    model_override = prefs.ai_model_override.strip()

    if provider == "OPENROUTER":
        config = {
            "base_url": "https://openrouter.ai/api/v1",
            "model": "anthropic/claude-sonnet-4",
            "api_key": api_key,
        }
    elif provider == "OPENAI":
        config = {
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-4o",
            "api_key": api_key,
        }
    elif provider == "ANTHROPIC":
        config = {
            "base_url": "https://api.anthropic.com/v1",
            "model": "claude-sonnet-4-5-20250514",
            "api_key": api_key,
        }
    else:
        raise ValueError(f"Unknown provider: {provider}")

    # Apply model override if set
    if model_override:
        config["model"] = model_override

    return config


def _get_script_content(node) -> str:
    """Get the current script content from a node."""
    if node.source_type == "INTERNAL":
        if node.text_block:
            return node.text_block.as_string()
    else:
        if node.filepath:
            import os

            filepath = bpy.path.abspath(node.filepath)
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    return f.read()
    return ""


def _set_script_content(node, content: str):
    """Set the script content for a node."""
    if node.source_type == "INTERNAL":
        if node.text_block:
            node.text_block.clear()
            node.text_block.write(content)
    else:
        if node.filepath:
            import os

            filepath = bpy.path.abspath(node.filepath)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)


# Tool definitions for the API
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "write_script",
            "description": "Write the complete script content, replacing everything in the file. Use this when you need to write a new script or completely rewrite an existing one.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The complete Python script content to write",
                    }
                },
                "required": ["content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "replace_in_script",
            "description": "Replace specific text in the script. Use this for making targeted changes without rewriting everything. The old_text must match exactly.",
            "parameters": {
                "type": "object",
                "properties": {
                    "old_text": {
                        "type": "string",
                        "description": "The exact text to find and replace",
                    },
                    "new_text": {
                        "type": "string",
                        "description": "The text to replace it with",
                    },
                },
                "required": ["old_text", "new_text"],
            },
        },
    },
]


def _execute_tool(tool_name: str, arguments: dict, node) -> str:
    """Execute a tool and return the result."""
    if node is None:
        return "Error: No node context available"

    if tool_name == "write_script":
        content = arguments.get("content", "")
        _set_script_content(node, content)
        return f"Script written successfully. New content:\n```python\n{content}\n```"

    elif tool_name == "replace_in_script":
        old_text = arguments.get("old_text", "")
        new_text = arguments.get("new_text", "")

        current_content = _get_script_content(node)
        if old_text not in current_content:
            return f"Error: Could not find the text to replace. Make sure old_text matches exactly."

        new_content = current_content.replace(old_text, new_text, 1)
        _set_script_content(node, new_content)
        return f"Text replaced successfully. New script content:\n```python\n{new_content}\n```"

    else:
        return f"Error: Unknown tool '{tool_name}'"


SYSTEM_PROMPT = """You are an expert Blender Python (bpy) script writer and assistant working within the Scripting Nodes addon.

## About Scripting Nodes
Scripting Nodes (formerly known as Serpens) is a visual scripting addon for Blender that allows users to build Blender addons using a node-based system. Instead of writing Python code from scratch, users connect nodes together to create functionality. The node system then generates Python code that becomes a working Blender addon.

## Your Context
You are helping the user write code inside a **Script Node**. The Script Node allows users to write custom Python code that integrates with the visual node system.

## CRITICAL: What You Can Write
Your script runs INSIDE an operator, panel, or other Blender construct created by the node system. You can ONLY write:
- **Functions** (def my_function():)
- **Imperative code** (direct bpy calls, loops, conditionals)
- **Variables and data structures**

## NEVER Write These (the node system creates them):
- Operators (class ... bpy.types.Operator)
- Panels (class ... bpy.types.Panel)
- Property groups
- Menus
- Any bpy.types subclass
- register() / unregister() functions
- bl_info dictionaries
- if __name__ == "__main__" blocks
- bpy.utils.register_class() calls

## Access to bpy
The `bpy` module is always available. Import other standard library modules as needed at the top of your script.

## Tools Available
You have tools to directly edit the user's script file:
- write_script: Write a complete new script, replacing everything in the file
- replace_in_script: Replace specific text in the script (old_text must match exactly)

## Response Style
- Be **concise**. Keep explanations short (1-2 sentences max).
- Focus on what you did, not lengthy explanations of how the code works.
- The user can read the code - don't repeat what's obvious from reading it.
- Skip unnecessary pleasantries or filler text.

## Guidelines
1. Analyze the current script content provided
2. Use the appropriate tool to make changes directly to the file
3. Briefly state what you did (e.g., "Added an operator that creates a cube")

IMPORTANT: Always use the tools to make changes. Do not just show code - actually write it using the tools."""


def _generation_thread(
    node, user_message: str, script_content: str, response_queue: queue.Queue
):
    """Background thread that handles the API calls."""
    try:
        # Build conversation history
        messages = node.get_ai_messages()

        # Build the messages list for the API
        api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add conversation history (excluding the current message)
        for msg in messages[:-1]:
            api_messages.append({"role": msg["role"], "content": msg["content"]})

        # Add current context to the user message
        context_message = f"""Current script content:
```python
{script_content if script_content else "# Empty script"}
```

User request: {user_message}"""

        api_messages.append({"role": "user", "content": context_message})

        # Get API config
        config = _get_api_config()

        full_response = ""
        max_iterations = 10  # Prevent infinite loops

        for iteration in range(max_iterations):
            if _generation_state["should_stop"]:
                full_response += "\n\n[Generation stopped by user]"
                response_queue.put(full_response)
                break

            headers = {
                "Authorization": f"Bearer {config['api_key']}",
                "Content-Type": "application/json",
            }

            payload = {
                "model": config["model"],
                "messages": api_messages,
                "tools": TOOLS,
                "stream": True,
            }

            with httpx.Client(timeout=120.0) as client:
                with client.stream(
                    "POST",
                    f"{config['base_url']}/chat/completions",
                    headers=headers,
                    json=payload,
                ) as response:
                    response.raise_for_status()

                    # Collect the streamed response
                    current_content = ""
                    tool_calls_data = {}

                    for line in response.iter_lines():
                        if _generation_state["should_stop"]:
                            full_response += "\n\n[Generation stopped by user]"
                            response_queue.put(full_response)
                            return

                        if not line or not line.startswith("data: "):
                            continue

                        data = line[6:]  # Remove "data: " prefix

                        if data == "[DONE]":
                            break

                        try:
                            chunk = json.loads(data)
                            choice = chunk.get("choices", [{}])[0]
                            delta = choice.get("delta", {})

                            # Handle text content
                            if delta.get("content"):
                                current_content += delta["content"]
                                # Show accumulated content so far
                                response_queue.put(full_response + current_content)

                            # Handle tool calls
                            if delta.get("tool_calls"):
                                for tc in delta["tool_calls"]:
                                    idx = tc.get("index", 0)
                                    if idx not in tool_calls_data:
                                        tool_calls_data[idx] = {
                                            "id": tc.get("id", ""),
                                            "function": {"name": "", "arguments": ""},
                                        }
                                    if tc.get("id"):
                                        tool_calls_data[idx]["id"] = tc["id"]
                                    if tc.get("function", {}).get("name"):
                                        tool_calls_data[idx]["function"]["name"] = tc[
                                            "function"
                                        ]["name"]
                                    if tc.get("function", {}).get("arguments"):
                                        tool_calls_data[idx]["function"][
                                            "arguments"
                                        ] += tc["function"]["arguments"]

                        except json.JSONDecodeError:
                            continue

            # Add streamed content to full_response
            full_response += current_content

            # Check if there are tool calls to process
            if tool_calls_data:
                # Build the assistant message with tool calls
                tool_calls_list = []
                for idx in sorted(tool_calls_data.keys()):
                    tc = tool_calls_data[idx]
                    tool_calls_list.append(
                        {
                            "id": tc["id"],
                            "type": "function",
                            "function": tc["function"],
                        }
                    )

                assistant_msg = {
                    "role": "assistant",
                    "content": current_content or None,
                    "tool_calls": tool_calls_list,
                }
                api_messages.append(assistant_msg)

                # Process each tool call
                for tc in tool_calls_list:
                    tool_name = tc["function"]["name"]
                    try:
                        arguments = json.loads(tc["function"]["arguments"])
                    except json.JSONDecodeError:
                        arguments = {}

                    # Show tool usage in response
                    if tool_name == "write_script":
                        full_response += "\n\n📝 Writing script...\n"
                    elif tool_name == "replace_in_script":
                        full_response += "\n\n✏️ Replacing text in script...\n"
                    response_queue.put(full_response)

                    # Execute the tool
                    tool_result = _execute_tool(tool_name, arguments, node)

                    # Add tool result to messages
                    api_messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc["id"],
                            "content": tool_result,
                        }
                    )

                    full_response += "✓ Done\n"
                    response_queue.put(full_response)

                # Continue to get the final response after tool execution
                continue

            else:
                # No tool calls, we're done
                break

        response_queue.put(full_response)

    except httpx.HTTPStatusError as e:
        response_queue.put(f"API Error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        response_queue.put(f"Error: {str(e)}")
    finally:
        # Signal completion
        response_queue.put(None)
        _generation_state["is_generating"] = False
        _generation_state["should_stop"] = False
        _generation_state["current_node_id"] = None
        _generation_state["current_node"] = None


def start_generation(node, user_message: str):
    """Start AI generation in a background thread.

    Args:
        node: The script node to work with
        user_message: The user's message
    """
    global _generation_state

    # Get script content before starting thread (must be done from main thread)
    script_content = _get_script_content(node)

    _generation_state["is_generating"] = True
    _generation_state["should_stop"] = False
    _generation_state["current_node_id"] = node.id
    _generation_state["current_node"] = node
    _generation_state["response_queue"] = queue.Queue()

    # Start background thread
    thread = threading.Thread(
        target=_generation_thread,
        args=(node, user_message, script_content, _generation_state["response_queue"]),
        daemon=True,
    )
    _generation_state["thread"] = thread
    thread.start()
