"""
Operator for indexing blend data properties.
"""

import bpy

from ...blend_data import (
    BlendDataIndex,
    build_blend_data_index,
    AREA_NAMES,
)


class SNA_OT_IndexBlendData(bpy.types.Operator):
    bl_idname = "sna.index_blend_data"
    bl_label = "Index Blend Data"
    bl_description = "Scan and index all blend data properties for searching"
    bl_options = {"REGISTER"}

    max_depth: bpy.props.IntProperty(
        name="Max Depth",
        description="Maximum depth to recurse into nested properties",
        default=4,
        min=1,
        max=10,
    )

    def get_context_items(self, context):
        items = [("CURRENT", "Current Context", "Use the current context")]

        if context is None or context.window is None:
            return items

        seen_types = set()
        for i, area in enumerate(context.window.screen.areas):
            area_type = area.type
            if area_type in seen_types:
                continue
            seen_types.add(area_type)

            name = AREA_NAMES.get(area_type, area_type.replace("_", " ").title())
            items.append((f"AREA_{i}", name, f"Index from {name} context"))

        return items

    context_source: bpy.props.EnumProperty(
        name="Context Source",
        description="Which area context to index from",
        items=get_context_items,
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=250)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "context_source", text="Context")

    def execute(self, context):
        import time

        start = time.time()

        context_override = None
        context_description = "Current Context"

        if self.context_source.startswith("AREA_"):
            try:
                area_index = int(self.context_source.replace("AREA_", ""))
                area = context.screen.areas[area_index]
                region = None
                for r in area.regions:
                    if r.type == "WINDOW":
                        region = r
                        break
                if region is None:
                    region = area.regions[0]

                context_override = {
                    "window": context.window,
                    "screen": context.screen,
                    "area": area,
                    "region": region,
                }

                context_description = AREA_NAMES.get(area.type, area.type)
            except (ValueError, IndexError):
                pass

        index = build_blend_data_index(
            self.max_depth, context_override, context_description
        )

        elapsed = time.time() - start
        self.report(
            {"INFO"},
            f"Indexed {len(index.properties)} properties from {context_description} in {elapsed:.2f}s",
        )

        # Force panel redraw
        for area in context.screen.areas:
            if area.type == "NODE_EDITOR":
                area.tag_redraw()

        return {"FINISHED"}
