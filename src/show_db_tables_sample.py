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
            sample = sample_table(conn, table, limit=5)
            if sample is None:
                print("  (Error retrieving data)")
            elif not sample:
                print("  (No data)")
            else:
                for row in sample:
                    print("  ", row)

if __name__ == "__main__":
    main()
