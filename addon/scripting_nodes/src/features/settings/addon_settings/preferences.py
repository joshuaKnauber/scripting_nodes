import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, EnumProperty, BoolProperty


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

    # Subpanel toggles
    show_ai_integration: BoolProperty(
        name="AI Integration",
        description="Show AI Integration settings",
        default=True,
    )

    # AI Integration settings
    ai_provider: EnumProperty(
        name="AI Provider",
        description="Select the AI provider to use",
        items=[
            ("OPENROUTER", "OpenRouter", "Use OpenRouter API"),
            ("OPENAI", "OpenAI", "Use OpenAI API"),
            ("ANTHROPIC", "Anthropic", "Use Anthropic API"),
        ],
        default="OPENROUTER",
    )

    ai_api_key: StringProperty(
        name="API Key",
        description="API key for the selected AI provider",
        subtype="PASSWORD",
        default="",
    )

    ai_model_override: StringProperty(
        name="Model Override",
        description="Optional: Override the default model ID (e.g., 'gpt-4o', 'anthropic/claude-sonnet-4'). Leave empty to use defaults",
        default="",
    )

    def draw(self, context):
        layout = self.layout

        # AI Integration subpanel
        row = layout.row()
        row.prop(
            self,
            "show_ai_integration",
            icon="TRIA_DOWN" if self.show_ai_integration else "TRIA_RIGHT",
            emboss=False,
        )

        if self.show_ai_integration:
            col = layout.column(align=True)
            col.prop(self, "ai_provider")
            col.prop(self, "ai_api_key")
            col.prop(self, "ai_model_override", text="Model (optional)")


def get_preferences() -> SNA_AddonPreferences:
    """Get the addon preferences"""
    return bpy.context.preferences.addons[_addon_name].preferences
