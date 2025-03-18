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

class AnimalCategory(Base):
    __tablename__ = 'animal_category'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    vector_image_path = Column(String, nullable=False)

class CropCategory(Base):
    __tablename__ = 'crop_category'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    vector_image_path = Column(String, nullable=False)

class ProductCategory(Base):
    __tablename__ = 'product_category'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    vector_image_path = Column(String, nullable=False)

class SellerCategory(Base):
    __tablename__ = 'seller_category'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    vector_image_path = Column(String, nullable=False)

class PhotoCategory(Base):
    __tablename__ = 'photo_category'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    vector_image_path = Column(String, nullable=False)


# --- Create Tables if They Don't Exist ---
try:
    Base.metadata.create_all(engine)
    print("Ensured all seed tables exist.")
except Exception as e:
    print("Error creating tables:", e)
    exit(1)

# --- Set up the Session ---
Session = sessionmaker(bind=engine)
session = Session()

# --- Mapping of Seed Files to Models ---
seed_files = {
    "animal_category": "database_seeds/category_tables/animal_category.json",
    "crop_category": "database_seeds/category_tables/crop_category.json",
    "product_category": "database_seeds/category_tables/product_category.json",
    "seller_category": "database_seeds/category_tables/seller_category.json",
    "photo_category": "database_seeds/category_tables/photo_category.json",

}

model_mapping = {
    "animal_category": AnimalCategory,
    "crop_category": CropCategory,
    "product_category": ProductCategory,
    "seller_category": SellerCategory,
    "photo_category": PhotoCategory

}

# --- Insert/Merge Seed Data for All Tables ---
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
    print("All seed data inserted successfully.")
except Exception as e:
    session.rollback()
    print("Error committing seed data:", e)
finally:
    session.close()
