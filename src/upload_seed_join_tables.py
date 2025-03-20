import os
import sys
import json
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()  # For local development; in CI, use environment variables directly

# PostgreSQL credentials
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

if not all([DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD]):
    print("Missing one or more database credentials in environment variables.")
    sys.exit(1)

# URL-encode username and password
encoded_user = quote_plus(DB_USER)
encoded_password = quote_plus(DB_PASSWORD)

# Build SQLAlchemy connection string (with SSL mode if needed)
connection_string = (
    f"postgresql+psycopg2://{encoded_user}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
)

# Create the SQLAlchemy engine
engine = create_engine(connection_string)

# Folder containing join table seed files
JOIN_SEEDS_ROOT = "join_table_seeds"

def get_join_seed_files():
    """
    Recursively gather all JSON join table seed files in the JOIN_SEEDS_ROOT.
    """
    seed_files = []
    for root, _, files in os.walk(JOIN_SEEDS_ROOT):
        for file in files:
            if file.endswith(".json"):
                seed_files.append(os.path.join(root, file))
    return seed_files

def table_exists(conn, table_name):
    """
    Check if a table exists in the database using the connection.
    """
    return conn.dialect.has_table(conn, table_name)

def infer_join_table_schema(join_seed):
    """
    Given a parsed join seed JSON (dictionary), infer the join table schema.
    Assumes that the "content" key is a list with at least one element.
    Returns:
       - columns: a list of column names (from the first row in "content")
       - schema_sql: a string with the column definitions (all as INTEGER)
       - fk_constraints: a list of SQL fragments for foreign key constraints,
         built using the "references" object.
    """
    content = join_seed.get("content", [])
    if not content:
        return None, None, None

    # Use the first record to get the column names.
    first_record = content[0]
    if not isinstance(first_record, dict):
        return None, None, None
    columns = list(first_record.keys())
    
    # Define each column as INTEGER
    schema_sql = ", ".join(f"{col} INTEGER" for col in columns)
    
    # Build foreign key constraints from the "references" dictionary.
    refs = join_seed.get("references", {})
    fk_constraints = []
    # Expecting keys: "column_1_reference_table", "column_2_reference_table",
    # "column_1_reference_key", "column_2_reference_key"
    if len(columns) >= 2:
        col1 = columns[0]
        col2 = columns[1]
        ref_table1 = refs.get("column_1_reference_table")
        ref_key1 = refs.get("column_1_reference_key")
        ref_table2 = refs.get("column_2_reference_table")
        ref_key2 = refs.get("column_2_reference_key")
        print(f"Debug: For join table, inferred references: {ref_table1}({ref_key1}), {ref_table2}({ref_key2})")
        if ref_table1 and ref_key1:
            fk_constraints.append(f"FOREIGN KEY ({col1}) REFERENCES {ref_table1}({ref_key1}) ON DELETE CASCADE")
        if ref_table2 and ref_key2:
            fk_constraints.append(f"FOREIGN KEY ({col2}) REFERENCES {ref_table2}({ref_key2}) ON DELETE CASCADE")
    
    return columns, schema_sql, fk_constraints

def create_join_table(conn, table_name, schema_sql, fk_constraints, columns):
    """
    Create the join table with the given table name.
    The table will include the provided column definitions, a composite primary key,
    and the foreign key constraints.
    """
    pk = ", ".join(columns)
    fk_sql = ", ".join(fk_constraints) if fk_constraints else ""
    create_statement = f"CREATE TABLE {table_name} ({schema_sql}, PRIMARY KEY ({pk})"
    if fk_sql:
        create_statement += f", {fk_sql}"
    create_statement += ")"
    try:
        conn.execute(text(create_statement))
        print(f"Created join table '{table_name}' with schema: {create_statement}")
    except SQLAlchemyError as e:
        print(f"Error creating join table '{table_name}': {e}")

def print_current_join_table_info(conn, table_name):
    """
    Print information about an existing join table: row count.
    """
    if table_exists(conn, table_name):
        try:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = result.scalar()
            print(f"Join table '{table_name}' exists and currently contains {count} row(s).")
        except SQLAlchemyError as e:
            print(f"Error fetching row count for join table '{table_name}': {e}")
    else:
        print(f"Join table '{table_name}' does not exist.")

def process_join_seed_file(seed_file):
    """
    Process a single join table seed file:
      - Parse JSON
      - Determine join table name (from filename)
      - Print current content info
      - If table does not exist, create it using inferred schema from the JSON file
      - Delete existing data (after consent)
      - Insert the rows from "content"
    """
    table_name = os.path.splitext(os.path.basename(seed_file))[0]
    print(f"\nProcessing join seed file for table '{table_name}' from {seed_file} ...")
    
    # Load the JSON
    try:
        with open(seed_file, "r", encoding="utf-8") as f:
            join_seed = json.load(f)
    except Exception as e:
        print(f"Error reading JSON from {seed_file}: {e}")
        return
    
    # Print current join table info
    with engine.connect() as conn:
        print_current_join_table_info(conn, table_name)
    
    # Infer join table schema from the JSON content
    columns, schema_sql, fk_constraints = infer_join_table_schema(join_seed)
    if not columns:
        print(f"Could not infer schema for join table from {seed_file}. Skipping.")
        return
    
    # Ask for confirmation before deleting existing content and/or creating table
    confirm = input(f"\nWARNING: This will DELETE all existing data in join table '{table_name}' (and create it if it doesn't exist). Type 'yes' to confirm: ")
    if confirm.lower() != "yes":
        print("Operation aborted for this join seed file.")
        return
    
    # Process join table in its own transaction
    with engine.begin() as conn:
        # Create the join table if it doesn't exist
        if not table_exists(conn, table_name):
            create_join_table(conn, table_name, schema_sql, fk_constraints, columns)
        
        # Delete existing data from the join table
        try:
            result = conn.execute(text(f"DELETE FROM {table_name}"))
            deleted_count = result.rowcount
            if deleted_count == 0:
                print(f"Info: Join table '{table_name}' was already empty.")
            else:
                print(f"Deleted {deleted_count} row(s) from join table '{table_name}'.")
        except SQLAlchemyError as e:
            print(f"Error deleting data from join table '{table_name}': {e}")
            return
        
        # Insert new join records
        content = join_seed.get("content", [])
        if not isinstance(content, list):
            print(f"Join seed file {seed_file} has invalid 'content' format. Skipping.")
            return
        
        for record in content:
            if not isinstance(record, dict):
                print(f"Skipping invalid join record in {seed_file}: {record}")
                continue
            # Build insert query dynamically (assume all keys in record are join columns)
            cols = ", ".join(record.keys())
            placeholders = ", ".join(f":{col}" for col in record.keys())
            query = text(f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})")
            print(f"Inserting into '{table_name}': {record}")
            print(f"Using query: INSERT INTO {table_name} ({cols}) VALUES ({placeholders})")
            try:
                # Pass the record as a dictionary directly (do not use unpacking)
                conn.execute(query, record)
            except SQLAlchemyError as e:
                print(f"Error inserting join record into '{table_name}': {e}")
                print(f"Failed join record: {record}")

def main():
    join_seed_files = get_join_seed_files()
    if not join_seed_files:
        print("No join seed files found in the folder:", JOIN_SEEDS_ROOT)
        sys.exit(0)
    
    print("The following join tables will be reinitialized with seed data:")
    for seed_file in join_seed_files:
        table_name = os.path.splitext(os.path.basename(seed_file))[0]
        with engine.connect() as conn:
            print(" -", table_name)
            print_current_join_table_info(conn, table_name)
    
    # Process each join seed file individually
    for seed_file in join_seed_files:
        try:
            process_join_seed_file(seed_file)
        except Exception as e:
            print(f"Error processing join seed file {seed_file}: {e}\nRolling back and continuing with the next file.")
    
    print("\n✅ Join table seed data loaded successfully into the remote database.")

if __name__ == "__main__":
    main()
