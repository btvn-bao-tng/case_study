"""Field-level diff detection for flat mapping-like objects."""

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
    """Detect changes between two flat mappings."""

    def __init__(self, ignoreFields: List[str] | None = None) -> None:
        self.ignoreFields = frozenset(ignoreFields or ())

    def detectChanges(
        self, before: Dict[str, Any], after: Dict[str, Any]
    ) -> List[FieldChange]:
        if not isinstance(before, dict) or not isinstance(after, dict):
            raise TypeError("before and after must be dictionaries")

        # Stable output makes audit records and tests reproducible.
        field_names = sorted(set(before) | set(after), key=repr)
        changes: List[FieldChange] = []

        for field_name in field_names:
            if field_name in self.ignoreFields:
                continue
            

            in_before = field_name in before
            in_after = field_name in after

            if not in_before:
                changes.append(
                    FieldChange(
                        field_name, None, after[field_name], ChangeType.ADDED
                    )
                )
            elif not in_after:
                changes.append(
                    FieldChange(
                        field_name, before[field_name], None, ChangeType.REMOVED
                    )
                )
            elif before[field_name] != after[field_name]:
                changes.append(
                    FieldChange(
                        field_name,
                        before[field_name],
                        after[field_name],
                        ChangeType.MODIFIED,
                    )
                )

        return changes


def detectChanges(
    before: Dict[str, Any],
    after: Dict[str, Any],
    ignoreFields: List[str] | None = None,
) -> List[FieldChange]:
    """Convenience function matching the assignment's original API."""

    return DiffDetector(ignoreFields).detectChanges(before, after)
