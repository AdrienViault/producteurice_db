import os
import sys
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Load environment variables from .env (for local development; in CI use environment variables)
load_dotenv()

# PostgreSQL credentials
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

if not all([DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD]):
    print("Missing one or more database credentials in environment variables.")
    sys.exit(1)

# URL-encode username and password (to handle special characters)
encoded_user = quote_plus(DB_USER)
encoded_password = quote_plus(DB_PASSWORD)

# Build SQLAlchemy connection string (with SSL mode if needed)
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
    try:
        result = conn.execute(query)
        return [row[0] for row in result]
    except SQLAlchemyError as e:
        print("Error retrieving table list:", e)
        return []

def get_row_count(conn, table_name):
    """
    Retrieve the number of rows in a given table.
    """
    query = text(f"SELECT COUNT(*) FROM {table_name}")
    try:
        result = conn.execute(query)
        return result.scalar()
    except SQLAlchemyError as e:
        print(f"Error retrieving row count for table '{table_name}':", e)
        return None

def get_columns_info(conn, table_name):
    """
    Retrieve column information (name and data type) for a given table from information_schema.
    """
    query = text("""
        SELECT column_name, data_type, character_maximum_length
        FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = :table_name
        ORDER BY ordinal_position
    """)
    try:
        result = conn.execute(query, {"table_name": table_name})
        columns = []
        for row in result:
            col_name, data_type, char_max_length = row
            if char_max_length:
                data_type += f"({char_max_length})"
            columns.append((col_name, data_type))
        return columns
    except SQLAlchemyError as e:
        print(f"Error retrieving columns for table '{table_name}':", e)
        return None

def sample_table(conn, table_name, limit=5):
    """
    Retrieve a small sample of rows from the given table.
    """
    query = text(f"SELECT * FROM {table_name} LIMIT {limit}")
    try:
        result = conn.execute(query)
        return result.fetchall()
    except SQLAlchemyError as e:
        print(f"Error querying table '{table_name}':", e)
        return None

def main():
    with engine.connect() as conn:
        tables = get_tables(conn)
        if not tables:
            print("No tables found in the public schema.")
            sys.exit(0)
        print("Tables found in the database:")
        for table in tables:
            print(f"\nTable: {table}")
            count = get_row_count(conn, table)
            if count is not None:
                print(f"  Row count: {count}")
            columns_info = get_columns_info(conn, table)
            if columns_info:
                print("  Columns:")
                for col_name, data_type in columns_info:
                    print(f"    - {col_name}: {data_type}")
            sample = sample_table(conn, table, limit=5)
            if sample is None:
                print("  (Error retrieving sample data)")
            elif not sample:
                print("  (No data)")
            else:
                print("  Sample rows:")
                for row in sample:
                    print("    ", row)

if __name__ == "__main__":
    main()
