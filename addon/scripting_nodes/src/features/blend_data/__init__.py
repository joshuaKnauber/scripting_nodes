"""
Blend Data indexing and search functionality.

This module provides tools for indexing and searching Blender's RNA properties.
"""

from scripting_nodes.src.features.blend_data.property_info import PropertyInfo
from scripting_nodes.src.features.blend_data.index import BlendDataIndex
from scripting_nodes.src.features.blend_data.indexer import (
    index_rna_properties,
    build_blend_data_index,
    get_area_contexts,
)
from scripting_nodes.src.features.blend_data.constants import AREA_NAMES

__all__ = [
    "PropertyInfo",
    "BlendDataIndex",
    "index_rna_properties",
    "build_blend_data_index",
    "get_area_contexts",
    "AREA_NAMES",
]
