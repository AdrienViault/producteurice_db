import os
import sys
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

# Build connection string (with SSL mode if needed)
connection_string = (
    f"postgresql+psycopg2://{encoded_user}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
)

# Create the SQLAlchemy engine
engine = create_engine(connection_string)

def get_tables(conn):
    """
    Retrieve all table names from the public schema.
    """
    query = text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    result = conn.execute(query)
    return [row[0] for row in result]

def get_columns(conn, table_name):
    """
    Retrieve columns for a given table.
    Returns a list of column names.
    """
    query = text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = :table_name
    """)
    result = conn.execute(query, {"table_name": table_name})
    return [row[0] for row in result]

def add_foreign_key(conn, source_table, column_name, target_table):
    """
    Adds a foreign key constraint to source_table for column_name referencing target_table(id).
    Constraint name is generated as fk_<source_table>_<column_name>
    """
    constraint_name = f"fk_{source_table}_{column_name}"
    alter_query = text(f"""
        ALTER TABLE {source_table} 
        ADD CONSTRAINT {constraint_name} 
        FOREIGN KEY ({column_name}) REFERENCES {target_table}(id)
        ON UPDATE CASCADE ON DELETE CASCADE
    """)
    try:
        conn.execute(alter_query)
        print(f"✅ Added foreign key constraint {constraint_name}: {source_table}.{column_name} -> {target_table}(id)")
    except SQLAlchemyError as e:
        print(f"Error adding foreign key on {source_table}.{column_name}: {e}")

def main():
    with engine.connect() as conn:
        all_tables = get_tables(conn)
        print("Tables in the public schema:")
        for t in all_tables:
            print(" -", t)
        
        print("\nProcessing foreign keys based on column names ending with '_id' ...")
        # Iterate over each table
        for source_table in all_tables:
            columns = get_columns(conn, source_table)
            # For each column ending with _id and not exactly 'id'
            for col in columns:
                if col == "id":
                    continue
                if col.endswith("_id"):
                    # Infer target table from column name.
                    # Example: "farm_id" -> target table "farm"
                    target_table = col[:-3]  # Remove "_id"
                    if target_table in all_tables:
                        print(f"Table '{source_table}': column '{col}' refers to table '{target_table}'.")
                        add_foreign_key(conn, source_table, col, target_table)
                    else:
                        print(f"Table '{source_table}': column '{col}' suggests target '{target_table}', but that table does not exist.")
    print("\n✅ Foreign key constraints processing complete.")

if __name__ == "__main__":
    main()
