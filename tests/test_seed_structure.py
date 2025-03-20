import os
import json
import pytest

SEEDS_ROOT = "table_seeds"

def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# This helper gathers all JSON seed files recursively.
def get_seed_files():
    seed_files = []
    for root, _, files in os.walk(SEEDS_ROOT):
        for file in files:
            if file.endswith(".json"):
                seed_files.append(os.path.join(root, file))
    return seed_files

# Parametrized test for each JSON file.
@pytest.mark.parametrize("file_path", get_seed_files())
def test_seed_file_structure(file_path):
    data = load_json(file_path)
    
    # Check that the JSON file contains a list of records.
    assert isinstance(data, list), f"{file_path} does not contain a list of records."
    
    # If there are no records, skip further tests.
    if not data:
        pytest.skip(f"{file_path} is empty. Skipping key and duplicate id tests.")
    
    # Get the keys from the first record.
    base_keys = set(data[0].keys())
    
    # Prepare a set to check for duplicate IDs.
    ids = set()
    
    for index, record in enumerate(data):
        # Ensure every record has the same keys as the first one.
        assert set(record.keys()) == base_keys, (
            f"Record {index} in {file_path} has keys {set(record.keys())} "
            f"which differ from the first record's keys {base_keys}."
        )
        
        # Check that an 'id' key exists in the record.
        assert "id" in record, f"Record {index} in {file_path} is missing the 'id' key."
        
        # Check for duplicate 'id' values.
        rec_id = record["id"]
        assert rec_id not in ids, f"Duplicate id {rec_id} found in {file_path}."
        ids.add(rec_id)
