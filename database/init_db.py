"""
Database initialization script
Creates database and tables if they don't exist
"""

import mysql.connector
from mysql.connector import Error
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import DB_CONFIG


def create_database_and_tables():
    """Create database and all required tables"""
    connection = None
    try:
        # Connect without database first
        temp_config = DB_CONFIG.copy()
        temp_config.pop('database', None)
        
        connection = mysql.connector.connect(**temp_config)
        cursor = connection.cursor()
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        print(f"OK Database '{DB_CONFIG['database']}' created or already exists")
        
        # Use the database
        cursor.execute(f"USE {DB_CONFIG['database']}")
        
        # Read and execute schema
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Split by semicolon and execute each statement
        for statement in schema_sql.split(';'):
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                except Error as e:
                    if 'already exists' not in str(e).lower():
                        print(f"Warning: {e}")
        
        connection.commit()
        print("OK All tables created successfully")
        
        # Verify tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"OK Database initialized with {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
    except Error as e:
        print(f"Error: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("OK Database connection closed")
    
    return True


if __name__ == "__main__":
    print("Initializing database...")
    if create_database_and_tables():
        print("\nDatabase initialization completed successfully!")
    else:
        print("\nDatabase initialization failed!")
        sys.exit(1)
