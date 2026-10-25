"""
Auto-Training Module
Handles automatic model retraining when threshold is reached
"""

import os
import sys
import pandas as pd
from pathlib import Path
import subprocess
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.db_utils import (
    get_reviews_for_training, 
    get_new_reviews_count_since_training,
    get_latest_model_version,
    log_model_training
)
from backend.config import TRAINING_THRESHOLD, DATA_DIR, MODEL_DIR

logger = logging.getLogger(__name__)


def sync_db_to_csv():
    """
    Full sync: overwrite CSV with ALL reviews from database (with sentiment).
    CSV becomes exact copy of DB for training. Call after upload or before training.
    """
    try:
        reviews = get_reviews_for_training()
        csv_path = DATA_DIR / 'reviews_dataset.csv'
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        if not reviews:
            logger.info("No reviews with sentiment in database; CSV unchanged or empty.")
            if csv_path.exists():
                return True
            # Create empty CSV with headers
            pd.DataFrame(columns=['review_text', 'sentiment', 'rating']).to_csv(csv_path, index=False)
            return True

        df = pd.DataFrame(reviews)
        if 'sentiment' not in df.columns:
            logger.warning("No sentiment in reviews; skipping sync.")
            return False

        df = df[['review_text', 'sentiment', 'rating']].copy()
        df.to_csv(csv_path, index=False)
        logger.info(f"Synced {len(df)} reviews from DB to CSV.")
        return True
    except Exception as e:
        logger.error(f"Error in sync_db_to_csv: {e}")
        import traceback
        traceback.print_exc()
        return False


def update_csv_from_database():
    """
    Update CSV file with new reviews from database
    Automatically appends new reviews to existing CSV
    """
    try:
        # Get all reviews from database
        reviews = get_reviews_for_training()
        
        if not reviews:
            logger.info("No reviews found in database")
            return False
        
        # Create DataFrame
        df = pd.DataFrame(reviews)
        
        # Ensure sentiment column exists
        if 'sentiment' not in df.columns:
            logger.warning("No sentiment column in database reviews")
            return False
        
        # Read existing CSV if it exists
        csv_path = DATA_DIR / 'reviews_dataset.csv'
        existing_review_texts = set()
        
        if csv_path.exists():
            try:
                existing_df = pd.read_csv(csv_path)
                existing_review_texts = set(existing_df['review_text'].astype(str))
                logger.info(f"Existing CSV has {len(existing_review_texts)} reviews")
            except Exception as e:
                logger.warning(f"Error reading existing CSV: {e}")
        
        # Filter new reviews (not in existing CSV)
        if existing_review_texts:
            df['review_text_str'] = df['review_text'].astype(str)
            new_df = df[~df['review_text_str'].isin(existing_review_texts)].copy()
            new_df = new_df.drop(columns=['review_text_str'])
        else:
            new_df = df.copy()
        
        if len(new_df) == 0:
            logger.info("No new reviews to add to CSV")
            return True
        
        # Append new reviews to CSV
        if csv_path.exists():
            new_df.to_csv(csv_path, mode='a', header=False, index=False)
            logger.info(f"Appended {len(new_df)} new reviews to CSV")
        else:
            new_df.to_csv(csv_path, index=False)
            logger.info(f"Created CSV with {len(new_df)} reviews")
        
        return True
    
    except Exception as e:
        logger.error(f"Error updating CSV: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_training_threshold():
    """
    Check if training threshold is reached
    """
    try:
        # Get latest model version
        latest_model = get_latest_model_version()
        model_version = latest_model['model_version'] if latest_model else None
        
        # Get count of new reviews
        new_count = get_new_reviews_count_since_training(model_version)
        
        logger.info(f"New reviews since last training: {new_count}/{TRAINING_THRESHOLD}")
        
        return new_count >= TRAINING_THRESHOLD
    
    except Exception as e:
        logger.error(f"Error checking training threshold: {e}")
        return False


def trigger_auto_training():
    """
    Trigger automatic model retraining
    """
    try:
        logger.info("=" * 60)
        logger.info("Starting Auto-Training")
        logger.info("=" * 60)
        
        # Update CSV from database
        if not update_csv_from_database():
            logger.warning("Failed to update CSV from database")
            return False
        
        # Check threshold
        if not check_training_threshold():
            logger.info(f"Training threshold not reached. Need {TRAINING_THRESHOLD} new reviews.")
            return False
        
        # Run training script
        training_script = Path(__file__).parent.parent / 'ml' / 'train_model.py'
        
        logger.info("Running training script...")
        result = subprocess.run(
            [sys.executable, str(training_script)],
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )
        
        if result.returncode == 0:
            logger.info("Auto-training completed successfully")
            logger.info(result.stdout)
            return True
        else:
            logger.error(f"Auto-training failed: {result.stderr}")
            return False
    
    except subprocess.TimeoutExpired:
        logger.error("Training script timed out")
        return False
    except Exception as e:
        logger.error(f"Error in auto-training: {e}")
        import traceback
        traceback.print_exc()
        return False


def trigger_manual_training():
    """
    Manual training: sync DB -> CSV, run training script (no threshold).
    Returns True if training succeeded.
    """
    try:
        logger.info("Starting manual training (sync DB -> CSV, then train)...")
        if not sync_db_to_csv():
            logger.warning("Sync DB to CSV failed.")
            return False
        training_script = Path(__file__).parent.parent / 'ml' / 'train_model.py'
        result = subprocess.run(
            [sys.executable, str(training_script)],
            capture_output=True,
            text=True,
            timeout=3600,
            cwd=str(Path(__file__).parent.parent)
        )
        if result.returncode == 0:
            logger.info("Manual training completed successfully.")
            return True
        logger.error(f"Manual training failed: {result.stderr}")
        return False
    except subprocess.TimeoutExpired:
        logger.error("Training script timed out.")
        return False
    except Exception as e:
        logger.error(f"Error in manual training: {e}")
        import traceback
        traceback.print_exc()
        return False


def schedule_auto_training():
    """
    Schedule auto-training (called periodically)
    """
    try:
        if check_training_threshold():
            return trigger_auto_training()
        return False
    except Exception as e:
        logger.error(f"Error scheduling auto-training: {e}")
        return False
