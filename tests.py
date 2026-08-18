import unittest

from main import ChangeType, DiffDetector, FieldChange, detectChanges


class DetectChangesTests(unittest.TestCase):
    def test_modified_field_only(self):
        result = detectChanges(
            {"name": "Product A", "price": 50000, "status": "active"},
            {"name": "Product A", "price": 65000, "status": "active"},
        )

        self.assertEqual(
            result,
            [FieldChange("price", 50000, 65000, ChangeType.MODIFIED)],
        )

    def test_added_and_removed_fields(self):
        result = detectChanges(
            {"name": "Order 1", "channel": "Lazada"},
            {"name": "Order 1", "priority": "HIGH"},
        )

        self.assertEqual(
            result,
            [
                FieldChange("channel", "Lazada", None, ChangeType.REMOVED),
                FieldChange("priority", None, "HIGH", ChangeType.ADDED),
            ],
        )
    
    def test_added_and_removed_fields_v2(self):
            result = detectChanges(
                {"name": "Order 1", "priority": "HIGH"},
                {"name": "Order 1", "channel": "Lazada"},
            )
            print(result)
    
            self.assertEqual(
                result,
                second=[
                    FieldChange("channel", None, "Lazada", ChangeType.ADDED),
                    FieldChange("priority", "HIGH", None, ChangeType.REMOVED),
                ],
            )
            

    def test_ignored_fields_are_not_reported(self):
        result = DiffDetector(["updatedAt", "version"]).detectChanges(
            {
                "name": "Product A",
                "price": 50000,
                "updatedAt": "2026-01-01",
                "version": 1,
            },
            {
                "name": "Product A",
                "price": 65000,
                "updatedAt": "2026-08-06",
                "version": 2,
            },
        )

        self.assertEqual(
            result,
            [FieldChange("price", 50000, 65000, ChangeType.MODIFIED)],
        )

    def test_equal_objects_return_empty_list(self):
        self.assertEqual(detectChanges({"a": 1}, {"a": 1}), [])

    def test_none_is_distinct_from_a_missing_field(self):
        self.assertEqual(
            detectChanges({}, {"value": None}),
            [FieldChange("value", None, None, ChangeType.ADDED)],
        )
        self.assertEqual(
            detectChanges({"value": None}, {}),
            [FieldChange("value", None, None, ChangeType.REMOVED)],
        )

    def test_inputs_are_not_mutated(self):
        before = {"a": 1}
        after = {"a": 2}
        detectChanges(before, after)
        self.assertEqual(before, {"a": 1})
        self.assertEqual(after, {"a": 2})

    def test_invalid_inputs_raise_type_error(self):
        with self.assertRaises(TypeError):
            detectChanges([], {})


if __name__ == "__main__":
    unittest.main()
