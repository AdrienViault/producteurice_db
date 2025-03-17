import os
import json
from urllib.parse import quote_plus
from sqlalchemy import Column, Integer, String, create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()

# PostgreSQL credentials
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# URL-encode username and password in case of special characters
encoded_user = quote_plus(DB_USER)
encoded_password = quote_plus(DB_PASSWORD)

# Build SQLAlchemy connection string (with SSL mode required by Azure)
connection_string = (
    f"postgresql+psycopg2://{encoded_user}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
)

# Create the SQLAlchemy engine
engine = create_engine(connection_string)

# --- Test PostgreSQL Connection ---
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("DB connection test result:", result.scalar())
except Exception as e:
    print("Failed to connect to PostgreSQL using SQLAlchemy:", e)
    exit(1)

# --- Define the SQLAlchemy Base and Models ---
Base = declarative_base()

class Label(Base):
    __tablename__ = 'label'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)  # Optional description field
    vector_image_path = Column(String, nullable=False)

class UnofficialLabel(Base):
    __tablename__ = 'unofficial_label'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)  # Optional description field
    vector_image_path = Column(String, nullable=False)

# --- Create Tables if They Don't Exist ---
try:
    Base.metadata.create_all(engine)
    print("Ensured all distinction seed tables exist.")
except Exception as e:
    print("Error creating tables:", e)
    exit(1)

# --- Set up the Session ---
Session = sessionmaker(bind=engine)
session = Session()

# --- Mapping of Seed Files to Models ---
seed_files = {
    "label": "database_seeds/distinction_tables/label.json",
    "unofficial_label": "database_seeds/distinction_tables/unofficial_label.json",
}

model_mapping = {
    "label": Label,
    "unofficial_label": UnofficialLabel,
}

# --- Insert/Merge Seed Data for All Distinction Tables ---
for table_name, file_path in seed_files.items():
    try:
        with open(file_path, "r") as f:
            records = json.load(f)
        model = model_mapping[table_name]
        for rec in records:
            # session.merge() ensures that if a record with the same primary key exists, it will be updated instead of duplicated.
            session.merge(model(**rec))
        print(f"Seed data processed for table: {table_name}")
    except Exception as e:
        print(f"Error processing seed data for {table_name} from {file_path}: {e}")

# --- Commit the Session ---
try:
    session.commit()
    print("All distinction seed data inserted successfully.")
except Exception as e:
    session.rollback()
    print("Error committing seed data:", e)
finally:
    session.close()
