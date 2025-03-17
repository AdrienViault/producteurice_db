import os
import pytest
from sqlalchemy import create_engine, text, inspect
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Fixture to create a SQLAlchemy engine using your environment variables
@pytest.fixture(scope="module")
def engine():
    load_dotenv()
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    
    # URL encode credentials in case of special characters
    encoded_user = quote_plus(DB_USER)
    encoded_password = quote_plus(DB_PASSWORD)
    
    connection_string = (
        f"postgresql+psycopg2://{encoded_user}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
    )
    eng = create_engine(connection_string)
    yield eng
    eng.dispose()

# Define the expected distinction tables and their expected minimum row counts.
EXPECTED_TABLES = {
    "label": {"min_rows": 1},
    "unofficial_label": {"min_rows": 1},
}

def test_tables_and_contents(engine):
    inspector = inspect(engine)
    actual_tables = inspector.get_table_names()
    print("Tables in DB:", actual_tables)
    
    # Loop through each expected table, verify existence, count rows and print first row.
    for table_name, props in EXPECTED_TABLES.items():
        assert table_name in actual_tables, f"Expected table '{table_name}' not found in database."
        
        with engine.connect() as conn:
            # Count rows in the table
            count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = count_result.scalar()
            
            # Retrieve first row ordered by primary key (assuming 'id' exists)
            row_result = conn.execute(text(f"SELECT * FROM {table_name} ORDER BY id LIMIT 1"))
            first_row = row_result.fetchone()
            
            print(f"Table: {table_name}")
            print("  Number of rows:", count)
            print("  First row:", first_row)
            
            # Check that the table has at least the expected minimum number of rows
            assert count >= props["min_rows"], (
                f"Expected at least {props['min_rows']} row(s) in '{table_name}', found {count}."
            )
