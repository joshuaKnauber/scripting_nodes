"""
BlendDataIndex - Singleton index of all blend data properties with search.
"""

from typing import Dict, List, Tuple
from difflib import SequenceMatcher

from .property_info import PropertyInfo


class BlendDataIndex:
    """Singleton index of all blend data properties."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.properties: Dict[str, PropertyInfo] = {}  # key -> PropertyInfo
        self.is_indexed = False
        self.indexed_context: str = ""  # Description of context used for indexing
        # Search cache to avoid expensive recomputation on every redraw
        self._cached_query: str = ""
        self._cached_results: List[Tuple[PropertyInfo, float]] = []

    def clear(self):
        """Clear the index."""
        self.properties.clear()
        self.is_indexed = False
        self.indexed_context = ""
        self._cached_query = ""
        self._cached_results = []

    def add_property(self, prop_info: PropertyInfo, path: str):
        """Add or update a property in the index."""
        key = prop_info.unique_key
        if key in self.properties:
            self.properties[key].add_path(path)
        else:
            prop_info.add_path(path)
            self.properties[key] = prop_info

    def search(
        self, query: str, max_results: int = 25
    ) -> List[Tuple[PropertyInfo, float]]:
        """
        Search properties by name, identifier, type, and description.
        Supports multi-word queries like "object name" to find name property on Object.
        Returns list of (PropertyInfo, score) sorted by relevance.
        Results are cached to avoid expensive recomputation on every panel redraw.
        """
        # Return cached results if query hasn't changed
        if query == self._cached_query and self._cached_results:
            return self._cached_results[:max_results]

        if not query:
            # Return all properties sorted alphabetically
            results = [(p, 1.0) for p in self.properties.values()]
            results.sort(key=lambda x: x[0].name.lower())
            self._cached_query = query
            self._cached_results = results
            return results[:max_results]

        query_lower = query.lower().strip()
        query_words = query_lower.split()
        scored_results = []

        for prop in self.properties.values():
            score = self._calculate_match_score(prop, query_lower, query_words)
            if score > 0:
                scored_results.append((prop, score))

        # Sort by score descending, then by name
        scored_results.sort(key=lambda x: (-x[1], x[0].name.lower()))

        # Cache results
        self._cached_query = query
        self._cached_results = scored_results

        return scored_results[:max_results]

    def _calculate_match_score(
        self, prop: PropertyInfo, query_lower: str, query_words: List[str]
    ) -> float:
        """
        Calculate relevance score for a property against a query.

        Matching strategy:
        1. Exact/prefix matches on combined "Type Property" string
        2. All query words found across type, name, identifier
        3. Partial matches and fuzzy matching
        """
        name_lower = prop.name.lower()
        ident_lower = prop.identifier.lower()
        desc_lower = prop.description.lower()
        type_lower = prop.rna_type.lower()

        # Create searchable combinations
        combined_type_name = f"{type_lower} {name_lower}"
        combined_type_ident = f"{type_lower} {ident_lower}"

        # Also create space-separated version of camelCase/PascalCase type
        type_spaced = self._split_camel_case(prop.rna_type).lower()
        combined_spaced = f"{type_spaced} {name_lower}"

        # 1. Exact match on full query
        if query_lower == name_lower or query_lower == ident_lower:
            return 1.0

        if query_lower == combined_type_name or query_lower == combined_type_ident:
            return 1.0

        # 2. Combined string starts with query
        if combined_type_name.startswith(query_lower) or combined_type_ident.startswith(
            query_lower
        ):
            return 0.95

        if combined_spaced.startswith(query_lower):
            return 0.95

        # 3. Multi-word matching: all words must be found somewhere
        if len(query_words) > 1:
            searchable = (
                f"{type_lower} {type_spaced} {name_lower} {ident_lower} {desc_lower}"
            )
            words_found = sum(1 for word in query_words if word in searchable)

            if words_found == len(query_words):
                # All words found - high score
                # Bonus if words match type + property specifically
                type_match = any(
                    w in type_lower or w in type_spaced for w in query_words
                )
                prop_match = any(
                    w in name_lower or w in ident_lower for w in query_words
                )

                if type_match and prop_match:
                    return 0.9  # e.g., "object name" matching Object.name
                return 0.8
            elif words_found > 0:
                # Partial word match
                return 0.4 * (words_found / len(query_words))

        # 4. Single word or remaining matches
        # Name or identifier starts with query
        if name_lower.startswith(query_lower) or ident_lower.startswith(query_lower):
            return 0.85

        # Query is substring of name or identifier
        if query_lower in name_lower or query_lower in ident_lower:
            return 0.7

        # Query matches type name
        if query_lower in type_lower or query_lower in type_spaced:
            return 0.5

        # Query is in description
        if query_lower in desc_lower:
            return 0.4

        # Fuzzy match on name
        ratio = SequenceMatcher(None, query_lower, name_lower).ratio()
        if ratio > 0.6:
            return ratio * 0.35

        # Fuzzy match on combined
        ratio = SequenceMatcher(None, query_lower, combined_spaced).ratio()
        if ratio > 0.6:
            return ratio * 0.3

        return 0.0

    @staticmethod
    def _split_camel_case(text: str) -> str:
        """Split CamelCase or PascalCase into space-separated words."""
        result = []
        current_word = []

        for char in text:
            if char.isupper() and current_word:
                result.append("".join(current_word))
                current_word = [char]
            else:
                current_word.append(char)

        if current_word:
            result.append("".join(current_word))

        return " ".join(result)
