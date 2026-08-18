"""Field-level diff detection for dictionaries, including nested objects."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List


class ChangeType(str, Enum):
    """The kind of change detected for a field."""

    MODIFIED = "MODIFIED"
    ADDED = "ADDED"
    REMOVED = "REMOVED"


@dataclass(frozen=True)
class FieldChange:
    """A single field-level change between two objects."""

    fieldName: str
    oldValue: Any
    newValue: Any
    changeType: ChangeType


class DiffDetector:
    """Detect changes between dictionaries, including nested dictionaries.

    Nested field names use dot notation, for example ``address.city``.
    Lists and other non-dictionary values are compared as a single value.
    """

    def __init__(self, ignoreFields: List[str] | None = None) -> None:
        self.ignoreFields = frozenset(ignoreFields or ())

    def detectChanges(
        self, before: Dict[str, Any], after: Dict[str, Any]
    ) -> List[FieldChange]:
        if not isinstance(before, dict) or not isinstance(after, dict):
            raise TypeError("before and after must be dictionaries")

        return self._collect_changes(before, after, "")

    def _collect_changes(
        self,
        before: Dict[str, Any],
        after: Dict[str, Any],
        parent_path: str,
    ) -> List[FieldChange]:
        # Stable output makes audit records and tests reproducible.
        field_names = sorted(set(before) | set(after), key=repr)
        changes: List[FieldChange] = []

        for field_name in field_names:
            field_path = (
                f"{parent_path}.{field_name}" if parent_path else field_name
            )
            if self._is_ignored(field_name, field_path):
                continue

            in_before = field_name in before
            in_after = field_name in after

            if not in_before:
                changes.append(
                    FieldChange(
                        field_path, None, after[field_name], ChangeType.ADDED
                    )
                )
                continue
            elif not in_after:
                changes.append(
                    FieldChange(
                        field_path, before[field_name], None, ChangeType.REMOVED
                    )
                )
                continue

            before_value = before[field_name]
            after_value = after[field_name]
            if isinstance(before_value, dict) and isinstance(after_value, dict):
                changes.extend(
                    self._collect_changes(before_value, after_value, field_path)
                )
            elif before_value != after_value:
                changes.append(
                    FieldChange(
                        field_path,
                        before_value,
                        after_value,
                        ChangeType.MODIFIED,
                    )
                )

        return changes

    def _is_ignored(self, field_name: str, field_path: str) -> bool:
        """Support both global field names and exact nested paths."""

        return field_name in self.ignoreFields or field_path in self.ignoreFields


def detectChanges(
    before: Dict[str, Any],
    after: Dict[str, Any],
    ignoreFields: List[str] | None = None,
) -> List[FieldChange]:
    """Convenience function matching the assignment's original API."""

    return DiffDetector(ignoreFields).detectChanges(before, after)
