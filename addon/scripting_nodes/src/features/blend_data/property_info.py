"""
PropertyInfo dataclass for representing indexed properties.
"""

from typing import List
from dataclasses import dataclass, field


@dataclass
class PropertyInfo:
    """Represents a unique property with its metadata and access paths."""

    identifier: str  # Python attribute name
    name: str  # Human-readable display name
    description: str
    type_name: str  # e.g., "FloatProperty", "PointerProperty", etc.
    rna_type: str  # The RNA type that owns this property
    access_paths: List[str] = field(default_factory=list)

    def add_path(self, path: str):
        """Add an access path if not already present."""
        if path not in self.access_paths:
            self.access_paths.append(path)

    @property
    def unique_key(self) -> str:
        """Unique identifier based on owning type and property identifier."""
        return f"{self.rna_type}.{self.identifier}"
