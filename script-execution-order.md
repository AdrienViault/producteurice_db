# Script Execution Order

This document explains the required order for executing scripts to properly initialize the database tables and their relationships.

## Order to Initiate the Database

1. **upload_seed_tables.py**

    - **Purpose:** Create and populate the base tables using seed files from the `table_seeds` directory.
    - **Note:** Run this script first to ensure all primary data is available.

2. **add_foreign_keys.py**

    - **Purpose:** Alter the tables to add foreign key constraints that define the relationships between tables.
    - **Note:** This step is essential to enforce data integrity before inserting join data.

3. **upload_seed_join_tables.py**
    - **Purpose:** Populate the join tables using seed files from the `join_table_seeds` directory.
    - **Note:** This step should be executed after all primary tables and constraints are in place.

**Why This Order?**

-   **Base Table Population:**  
    Uploading seed tables first guarantees that all individual records exist before any relationships are established.

-   **Constraint Enforcement:**  
    Adding foreign keys after populating base tables ensures that the relationships can be properly enforced without errors due to missing data.

-   **Join Data Insertion:**  
    Inserting join table data last ensures that all referenced records are present, avoiding violations of foreign key constraints.

Following this order helps prevent data integrity issues during the database initialization process.
