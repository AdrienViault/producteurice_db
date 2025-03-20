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

# URL-encode username and password in case of special characters
encoded_user = quote_plus(DB_USER)
encoded_password = quote_plus(DB_PASSWORD)

# Build SQLAlchemy connection string (with SSL mode required by Azure)
connection_string = (
    f"postgresql+psycopg2://{encoded_user}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
)

# Create the SQLAlchemy engine
engine = create_engine(connection_string)

# Folder containing seed files
SEEDS_ROOT = "table_seeds"

def get_seed_files():
    """
    Recursively gather all JSON seed files in the SEEDS_ROOT.
    """
    seed_files = []
    for root, _, files in os.walk(SEEDS_ROOT):
        for file in files:
            if file.endswith(".json"):
                seed_files.append(os.path.join(root, file))
    return seed_files

def table_exists(conn, table_name):
    """
    Check if a table exists in the database using the connection.
    """
    return conn.dialect.has_table(conn, table_name)

def infer_sql_type(key, value):
    """
    Infer an SQL type for a column based on the key name and value.
    Rules:
      - If key is "id": INTEGER PRIMARY KEY.
      - If key ends with "_id": INTEGER.
      - If key contains "latitude" or "longitude" (case-insensitive): DECIMAL(9,6).
      - If value is a list, store it as an INTEGER[] (assuming a list of integers).
      - If value is int: INTEGER.
      - If value is float: FLOAT.
      - If value is str: TEXT.
      - Else: TEXT.
    """
    lower_key = key.lower()
    if key == "id":
        return "INTEGER PRIMARY KEY"
    elif key.endswith("_id"):
        return "INTEGER"
    elif "latitude" in lower_key or "longitude" in lower_key:
        return "DECIMAL(9,6)"
    else:
        if isinstance(value, int):
            return "INTEGER"
        elif isinstance(value, float):
            return "FLOAT"
        elif isinstance(value, str):
            return "TEXT"
        else:
            return "TEXT"

def infer_table_schema(seed_file):
    """
    Reads the first record from the seed file and infers a schema.
    Returns a dict mapping column names to SQL type definitions.
    """
    try:
        with open(seed_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON from {seed_file}: {e}")
        return {}
    
    # Get a representative record
    if isinstance(data, list) and data:
        record = data[0]
    elif isinstance(data, dict):
        record = data
    else:
        return {}
    
    if not isinstance(record, dict):
        return {}
    
    schema = {}
    for key, value in record.items():
        schema[key] = infer_sql_type(key, value)
    return schema

def print_current_table_info(conn, table_name, seed_file):
    """
    Print whether the table exists; if it does, print its row count.
    If it doesn't, print the inferred schema from the seed file.
    """
    if table_exists(conn, table_name):
        try:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = result.scalar()
            print(f"Table '{table_name}' exists and currently contains {count} row(s).")
        except SQLAlchemyError as e:
            print(f"Error fetching row count for table '{table_name}': {e}")
    else:
        print(f"Table '{table_name}' does not exist.")
        inferred_schema = infer_table_schema(seed_file)
        if inferred_schema:
            cols = ", ".join(f"{col} {col_type}" for col, col_type in inferred_schema.items())
            print(f"  It will be created with the following schema: {cols}")
        else:
            print("  Could not infer schema from seed file.")

def create_table(conn, table_name, schema):
    """
    Create a table with the given table name and schema.
    Schema is a dict mapping column names to SQL types.
    """
    cols = ", ".join(f"{col} {col_type}" for col, col_type in schema.items())
    create_query = text(f"CREATE TABLE {table_name} ({cols})")
    try:
        conn.execute(create_query)
        print(f"Created table '{table_name}' with schema: {cols}")
    except SQLAlchemyError as e:
        print(f"Error creating table '{table_name}': {e}")

def main():
    seed_files = get_seed_files()
    if not seed_files:
        print("No seed files found in the folder:", SEEDS_ROOT)
        sys.exit(1)
    
    # Determine target table names from the seed files (e.g., 'address.json' -> 'address')
    table_names = sorted({os.path.splitext(os.path.basename(f))[0] for f in seed_files})
    
    print("The following tables will be reinitialized with seed data:")
    with engine.connect() as conn:
        for seed_file in seed_files:
            table_name = os.path.splitext(os.path.basename(seed_file))[0]
            print(" -", table_name)
            print_current_table_info(conn, table_name, seed_file)
    
    # Prompt for manual confirmation to proceed
    confirm = input("\nWARNING: This will DELETE all existing data in these tables (and create them if they don't exist). Type 'yes' to confirm: ")
    if confirm.lower() != "yes":
        print("Operation aborted.")
        sys.exit(0)
    
    # Begin transaction to process all seed files
    with engine.begin() as conn:
        for seed_file in seed_files:
            table_name = os.path.splitext(os.path.basename(seed_file))[0]
            
            # Check if the table exists; if not, create it using inferred schema.
            if not table_exists(conn, table_name):
                schema = infer_table_schema(seed_file)
                if not schema:
                    print(f"Could not infer schema for table '{table_name}' from {seed_file}. Skipping.")
                    continue
                create_table(conn, table_name, schema)
            
            print(f"\nProcessing seed file for table '{table_name}'...")
            
            # Delete existing data (if any)
            try:
                result = conn.execute(text(f"DELETE FROM {table_name}"))
                deleted_count = result.rowcount
                if deleted_count == 0:
                    print(f"Info: Table '{table_name}' was already empty.")
                else:
                    print(f"Deleted {deleted_count} row(s) from table '{table_name}'.")
            except SQLAlchemyError as e:
                print(f"Error deleting data from table '{table_name}': {e}")
                continue
            
            # Load seed data from JSON file
            try:
                with open(seed_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                print(f"Error reading JSON from {seed_file}: {e}")
                continue
            
            # Insert seed data into the table
            # Insert seed data into the table
            if isinstance(data, list):
                for record in data:
                    if not isinstance(record, dict):
                        print(f"Skipping invalid record in {seed_file}: {record}")
                        continue
                    columns = record.keys()
                    col_names = ", ".join(columns)
                    placeholders = ", ".join(f":{col}" for col in columns)
                    query = text(f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})")
                    
                    # Debug prints
                    print(f"Inserting into '{table_name}': {record}")
                    print(f"Using query: INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})")
                    
                    try:
                        conn.execute(query, record)  # Pass the record dictionary directly
                    except SQLAlchemyError as e:
                        print(f"Error inserting record into table '{table_name}': {e}")
                        print(f"Failed record: {record}")
            elif isinstance(data, dict):
                columns = data.keys()
                col_names = ", ".join(columns)
                placeholders = ", ".join(f":{col}" for col in columns)
                query = text(f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})")
                
                print(f"Inserting into '{table_name}': {data}")
                print(f"Using query: INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})")
                
                try:
                    conn.execute(query, data)
                except SQLAlchemyError as e:
                    print(f"Error inserting data into table '{table_name}': {e}")
                    print(f"Failed record: {data}")

                print(f"Unsupported data format in {seed_file}. Skipping.")
    
    print("\n✅ Seed data loaded successfully into the remote database.")

if __name__ == "__main__":
    main()
