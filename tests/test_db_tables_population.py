import os
import pytest
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables (locally via .env; in CI these should come from the environment)
load_dotenv()

# PostgreSQL credentials
if os.path.exists('.env'):
    load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# URL-encode username and password (to handle special characters)
encoded_user = quote_plus(DB_USER)
encoded_password = quote_plus(DB_PASSWORD)

# Build SQLAlchemy connection string (SSL mode required by Azure)
connection_string = (
    f"postgresql+psycopg2://{encoded_user}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
)

# Create the SQLAlchemy engine
engine = create_engine(connection_string)

# List of tables expected to be populated (matching your seed structure)
TABLES = [
    "addresses",
    "animal_categories",
    "crop_categories",
    "market_categories",
    "photo_categories",
    "product_categories",
    "season_categories",
    "seller_categories",
    "workload_categories",
    "labels",
    "unofficial_labels",
    "documentaries",
    "farms",
    "farmers",
    "herovideos",
    "photos",
    "products",
    "animals",   # from resource_tables/animals.json
    "crops",     # from resource_tables/crops.json
    "workloads"
]

@pytest.mark.parametrize("table_name", TABLES)
def test_table_population(table_name):
    """
    Verify that each table in the remote database contains at least one row.
    """
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        count = result.scalar()
        assert count > 0, f"Table '{table_name}' is empty (found {count} rows)."
