# Seeds JSON Structure

This document outlines the expected JSON format and folder organization for seed data.

## Folder Organization

The seed files are organized into two main directories:

-   **table_seeds:** Contains JSON files that populate individual tables.

    -   **address:**
        -   `address.json`
    -   **category:**
        -   `animal_category.json`
        -   `crop_category.json`
        -   `market_category.json`
        -   `photo_category.json`
        -   `product_category.json`
        -   `season_category.json`
        -   `seller_category.json`
        -   `workload_category.json`
    -   **distinction:**
        -   `label.json`
        -   `unofficial_label.json`
    -   **documentary:**
        -   `documentary.json`
    -   **farm:**
        -   `farm.json`
    -   **farmer:**
        -   `farmer.json`
    -   **herovideo:**
        -   `herovideo.json`
    -   **photo:**
        -   `photo.json`
    -   **product:**
        -   `product.json`
    -   **resource_tables:**
        -   `animal.json`
        -   `crop.json`
    -   **workload:**
        -   `workload.json`

-   **join_table_seeds:** Contains JSON files for join tables.
    -   Example: `product_subproducts.json`

## Expected JSON Format

Each JSON seed file (in `table_seeds`) should follow a consistent structure. For example, a seed file might look like:

```json
[
	{
		"id": 1,
		"name": "Example Name",
		"description": "Sample description",
		"created_at": "2025-03-20T12:00:00Z"
	},
	{
		"id": 2,
		"name": "Another Example",
		"description": "Another sample description",
		"created_at": "2025-03-20T12:05:00Z"
	}
]
```

**Notes**

-   The JSON file should contain an array (list) of objects.
-   Each record must include an `id` key and maintain consistent keys across all records.
-   Timestamps should be in `ISO 8601` format.

A test file (e.g., `test_seed_structure.py`) verifies these conventions by checking for a consistent key set and duplicate IDs.
