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

    def test_nested_field_modified_uses_dot_path(self):
        result = detectChanges(
            {
                "customer": {
                    "name": "Alice",
                    "address": {"city": "HCM", "country": "VN"},
                }
            },
            {
                "customer": {
                    "name": "Alice",
                    "address": {"city": "Hanoi", "country": "VN"},
                }
            },
        )

        self.assertEqual(
            result,
            [FieldChange("customer.address.city", "HCM", "Hanoi", ChangeType.MODIFIED)],
        )

    def test_nested_fields_added_and_removed(self):
        result = detectChanges(
            {"profile": {"name": "Alice", "age": 20}},
            {"profile": {"name": "Alice", "phone": "123"}},
        )

        self.assertEqual(
            result,
            [
                FieldChange("profile.age", 20, None, ChangeType.REMOVED),
                FieldChange("profile.phone", None, "123", ChangeType.ADDED),
            ],
        )

    def test_nested_ignore_field_name(self):
        result = DiffDetector(["updatedAt"]).detectChanges(
            {"audit": {"updatedAt": "old", "version": 1}},
            {"audit": {"updatedAt": "new", "version": 2}},
        )

        self.assertEqual(
            result,
            [FieldChange("audit.version", 1, 2, ChangeType.MODIFIED)],
        )

    def test_nested_ignore_exact_path(self):
        result = DiffDetector(["billing.updatedAt"]).detectChanges(
            {
                "billing": {"updatedAt": "old", "status": "pending"},
                "shipping": {"updatedAt": "old"},
            },
            {
                "billing": {"updatedAt": "new", "status": "paid"},
                "shipping": {"updatedAt": "new"},
            },
        )

        self.assertEqual(
            result,
            [
                FieldChange("billing.status", "pending", "paid", ChangeType.MODIFIED),
                FieldChange("shipping.updatedAt", "old", "new", ChangeType.MODIFIED),
            ],
        )

    def test_object_to_scalar_is_modified_at_parent_path(self):
        result = detectChanges(
            {"address": {"city": "HCM"}},
            {"address": "Unknown"},
        )

        self.assertEqual(
            result,
            [FieldChange("address", {"city": "HCM"}, "Unknown", ChangeType.MODIFIED)],
        )

    def test_list_is_compared_as_one_value(self):
        result = detectChanges(
            {"items": [{"id": 1, "quantity": 1}]},
            {"items": [{"id": 1, "quantity": 2}]},
        )

        self.assertEqual(
            result,
            [
                FieldChange(
                    "items",
                    [{"id": 1, "quantity": 1}],
                    [{"id": 1, "quantity": 2}],
                    ChangeType.MODIFIED,
                )
            ],
        )


if __name__ == "__main__":
    unittest.main()
