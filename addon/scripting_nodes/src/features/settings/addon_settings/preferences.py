import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, EnumProperty


def _get_addon_name():
    """Get the addon name for bl_idname.
    
    For extensions: bl_ext.<repo>.<name> -> bl_ext.<repo>.<name>
    For legacy addons: scripting_nodes.src... -> scripting_nodes
    """
    parts = __package__.split(".")
    if parts[0] == "bl_ext" and len(parts) >= 3:
        # Extension format: bl_ext.<repo>.<name>
        return ".".join(parts[:3])
    else:
        # Legacy addon format
        return parts[0]


_addon_name = _get_addon_name()


class SNA_AddonPreferences(AddonPreferences):
    """Scripting Nodes addon preferences"""
    
    # Must match the addon's package name
    bl_idname = _addon_name
    
    # AI Integration settings
    ai_provider: EnumProperty(
        name="AI Provider",
        description="Select the AI provider to use",
        items=[
            ("OPENAI", "OpenAI", "Use OpenAI API"),
            ("ANTHROPIC", "Anthropic", "Use Anthropic API"),
            ("OPENROUTER", "OpenRouter", "Use OpenRouter API"),
        ],
        default="OPENAI",
    )
    
    ai_api_key: StringProperty(
        name="API Key",
        description="API key for the selected AI provider",
        subtype="PASSWORD",
        default="",
    )
    
    def draw(self, context):
        layout = self.layout
        
        # AI Integration section
        box = layout.box()
        box.label(text="AI Integration", icon="EVENT_A")
        
        box.prop(self, "ai_provider")
        box.prop(self, "ai_api_key")


def get_preferences() -> SNA_AddonPreferences:
    """Get the addon preferences"""
    return bpy.context.preferences.addons[_addon_name].preferences
