"""
Quick Start Script for the Project
Run this to initialize and start the application
"""

import os
import sys
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'flask', 'tensorflow', 'numpy', 'pandas', 
        'nltk', 'mysql', 'gensim'
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'mysql':
                __import__('mysql.connector')
            else:
                __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("[X] Missing packages:", ", ".join(missing))
        print("Please install: pip install -r requirements.txt")
        return False
    return True

def check_database():
    """Check database connection"""
    try:
        from backend.config import DB_CONFIG
        import mysql.connector
        
        config = DB_CONFIG.copy()
        config.pop('database', None)
        conn = mysql.connector.connect(**config)
        conn.close()
        print("[OK] Database connection successful")
        return True
    except Exception as e:
        print(f"[X] Database connection failed: {e}")
        print("Please check your database configuration in backend/config.py")
        return False

def initialize_database():
    """Initialize database"""
    try:
        print("\nInitializing database...")
        from database.init_db import create_database_and_tables
        if create_database_and_tables():
            print("[OK] Database initialized successfully")
            return True
        return False
    except Exception as e:
        print(f"[X] Database initialization failed: {e}")
        return False

def check_model():
    """Check if model exists"""
    from backend.config import MODEL_DIR
    model_path = MODEL_DIR / 'best_model.h5'
    vocab_path = MODEL_DIR / 'vocab.pkl'
    
    if model_path.exists() and vocab_path.exists():
        print("[OK] Model files found")
        return True
    else:
        print("[!] Model not found. Please train the model first:")
        print("   python ml/train_model.py")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("Product Review Sentiment Classification System")
    print("=" * 60)
    
    # Check dependencies
    print("\n1. Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("[OK] All dependencies installed")
    
    # Check database
    print("\n2. Checking database connection...")
    if not check_database():
        print("Attempting to initialize database...")
        if not initialize_database():
            sys.exit(1)
    
    # Check model
    print("\n3. Checking model files...")
    has_model = check_model()
    
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    
    if not has_model:
        print("\n[!] IMPORTANT: Train the model first:")
        print("   python ml/train_model.py")
        print("\nThen start the backend server:")
    else:
        print("\n[OK] Ready to start! Run:")
    
    print("   python backend/app.py")
    print("\nThen open frontend/index.html in your browser")
    print("=" * 60)

if __name__ == "__main__":
    main()
