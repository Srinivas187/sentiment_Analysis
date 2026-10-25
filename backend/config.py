"""
Configuration file for backend application
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '12345'),
    'database': os.getenv('DB_NAME', 'sentiment_analysis_db'),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

# JWT Configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours

# Application Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# Paths
MODEL_DIR = BASE_DIR / 'models'
DATA_DIR = BASE_DIR / 'data'
FASTTEXT_MODEL_PATH = MODEL_DIR / 'fasttext_model.bin'
SENTIMENT_MODEL_PATH = MODEL_DIR / 'sentiment_model.h5'
REVIEWS_CSV_PATH = DATA_DIR / 'reviews_dataset.csv'

# Ensure directories exist
MODEL_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ML Configuration
MAX_SEQUENCE_LENGTH = 200
EMBEDDING_DIM = 300
VOCAB_SIZE = 10000
NUM_CLASSES = 3  # positive, negative, neutral

# Auto-Training Configuration
TRAINING_THRESHOLD = 500  # Number of new reviews before retraining
BATCH_SIZE = 32
EPOCHS = 10
VALIDATION_SPLIT = 0.2

# Sentiment Labels
SENTIMENT_LABELS = {
    0: 'negative',
    1: 'neutral',
    2: 'positive'
}

SENTIMENT_TO_LABEL = {v: k for k, v in SENTIMENT_LABELS.items()}
