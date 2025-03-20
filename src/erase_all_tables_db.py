import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# PostgreSQL credentials from environment
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

if not all([DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD]):
    print("Missing database credentials in environment variables.")
    exit(1)

# URL-encode username and password in case of special characters
encoded_user = quote_plus(DB_USER)
encoded_password = quote_plus(DB_PASSWORD)

# Build SQLAlchemy connection string (with SSL mode if needed)
connection_string = (
    f"postgresql+psycopg2://{encoded_user}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
)

# Create the SQLAlchemy engine
engine = create_engine(connection_string)

with engine.connect() as conn:
    # Query to list all tables in the public schema
    result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
    tables = [row[0] for row in result]
    
if tables:
    print("Existing tables in the public schema:")
    for table in tables:
        print(" -", table)
else:
    print("No tables found in the public schema.")

# Ask for manual confirmation
confirm = input("Are you sure you want to delete all tables from the database? This operation cannot be undone. Type 'yes' to confirm: ")
if confirm.lower() == "yes":
    with engine.connect() as conn:
        # Drop the public schema and recreate it. This deletes all tables.
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        conn.commit()
    print("✅ All tables have been deleted.")
else:
    print("Operation aborted.")
