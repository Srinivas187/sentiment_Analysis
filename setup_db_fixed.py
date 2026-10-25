import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import mysql.connector
from backend.config import DB_CONFIG

def fix_db():
    config = DB_CONFIG.copy()
    config.pop('database', None)
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    
    with open('database/schema.sql', 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    for result in cursor.execute(schema_sql, multi=True):
        if result.with_rows:
            result.fetchall()
            
    conn.commit()
    cursor.execute("USE sentiment_analysis_db")
    cursor.execute("SHOW TABLES")
    print("Tables:", cursor.fetchall())
    conn.close()

if __name__ == "__main__":
    fix_db()
