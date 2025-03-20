# Join Table Seeds Structure

This document describes the format and expected content for JSON files used to seed join tables.

## Structure

A join table seed file should include two main keys:

-   **references:** Describes the relationship between tables.
-   **content:** An array of join records.

### Example Format

```json
{
	"references": {
		"column_1_reference_table": "product",
		"column_2_reference_table": "product",
		"column_1_reference_key": "id",
		"column_2_reference_key": "id"
	},
	"content": [
		{
			"product_id": 2,
			"subproduct_id": 1
		},
		{
			"product_id": 3,
			"subproduct_id": 2
		},
		{
			"product_id": 6,
			"subproduct_id": 5
		},
		{
			"product_id": 8,
			"subproduct_id": 7
		},
		{
			"product_id": 9,
			"subproduct_id": 7
		},
		{
			"product_id": 10,
			"subproduct_id": 7
		}
	]
}
```

**Key Points:**

-   The references object should clearly state which tables and columns are involved in the join.
-   The content array holds the records where each record maps foreign keys (e.g., `product_id` and `subproduct_id`) that should correspond to valid IDs in the referenced tables.
-   Validations should be in place (for example via tests) to ensure referential integrity.

This structure enables clear and consistent seeding of relational data between tables.
