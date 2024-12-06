import sqlite3
import json
import os
from typing import List, Dict
import json

def init_db():
    """Initialize the database by creating the necessary table."""
    conn = sqlite3.connect('computer_specs.db')
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS computer_specs")
    cursor.execute("""
    CREATE TABLE computer_specs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_name TEXT NOT NULL,
        max_memory TEXT,
        processor_info TEXT,
        storage_capacity TEXT,
        ports TEXT,
        operating_system TEXT,
        additional_features TEXT
    )
    """)
    
    conn.commit()
    conn.close()

def load_json_files(json_dir: str) -> List[Dict]:
    """Load all JSON files from the specified directory."""
    specs_list = []
    for filename in os.listdir(json_dir):
        if filename.endswith('.json'):
            with open(os.path.join(json_dir, filename), 'r', encoding='utf-8') as f:
                specs_list.append(json.load(f))
    return specs_list

def insert_specs(specs_list: List[Dict]):
    """Insert computer specifications into the database."""
    conn = sqlite3.connect('computer_specs.db')
    cursor = conn.cursor()
    
    for specs in specs_list:
        # Convert lists to JSON strings for storage
        ports_json = json.dumps(specs['ports'])
        additional_features_json = json.dumps(specs.get('additional_features', []))
        
        cursor.execute("""
        INSERT INTO computer_specs (
            model_name,
            max_memory,
            processor_info,
            storage_capacity,
            ports,
            operating_system,
            additional_features
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            specs['model_name'],
            specs['max_memory'],
            specs['processor_info'],
            specs['storage_capacity'],
            ports_json,
            specs.get('operating_system'),
            additional_features_json
        ))
    
    conn.commit()
    conn.close()

def display_database_contents():
    """Display all records in the computer_specs database."""
    conn = sqlite3.connect('computer_specs.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM computer_specs")
    rows = cursor.fetchall()
    
    # Get column names
    cursor.execute("PRAGMA table_info(computer_specs)")
    columns = [col[1] for col in cursor.fetchall()]
    
    print("\nDatabase Contents:")
    print("-" * 80)
    
    for row in rows:
        print("\nRecord:")
        for col_name, value in zip(columns, row):
            # For JSON fields, pretty print them
            if col_name in ['ports', 'additional_features']:
                try:
                    value = json.loads(value)
                    print(f"{col_name}: {json.dumps(value, indent=2)}")
                except:
                    print(f"{col_name}: {value}")
            else:
                print(f"{col_name}: {value}")
        print("-" * 80)
    
    conn.close()

def main():
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_dir = os.path.join(current_dir, "manuales json")
    
    # Initialize the database
    print("Initializing database...")
    init_db()
    
    # Load JSON files
    print("Loading JSON files...")
    specs_list = load_json_files(json_dir)
    
    # Insert data into database
    print("Inserting data into database...")
    insert_specs(specs_list)
    
    print("Database population completed successfully!")
    
    # Display the contents of the database
    print("\nDisplaying database contents...")
    display_database_contents()

if __name__ == "__main__":
    main()
