"""
Blend Data indexing and search functionality.

This module provides tools for indexing and searching Blender's RNA properties.
"""

from .property_info import PropertyInfo
from .index import BlendDataIndex
from .indexer import (
    index_rna_properties,
    build_blend_data_index,
    get_area_contexts,
)
from .constants import AREA_NAMES

__all__ = [
    "PropertyInfo",
    "BlendDataIndex",
    "index_rna_properties",
    "build_blend_data_index",
    "get_area_contexts",
    "AREA_NAMES",
]
