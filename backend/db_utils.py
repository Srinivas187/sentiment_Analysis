"""
Database utility functions
Falls back to a local JSON file store when MySQL is unavailable.
"""

import os
import sys
import json
import time
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.config import DB_CONFIG, BASE_DIR

logger = logging.getLogger(__name__)

# ── Local JSON fallback store ────────────────────────────────────────────────
STORE_PATH = BASE_DIR / 'data' / 'local_store.json'

def _load_store():
    if STORE_PATH.exists():
        try:
            with open(STORE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {'users': [], 'reviews': [], 'predictions': [], 'explanations': [], 'model_logs': []}

def _save_store(store):
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STORE_PATH, 'w', encoding='utf-8') as f:
        json.dump(store, f, indent=2, default=str)

# ── MySQL helpers ────────────────────────────────────────────────────────────
_mysql_available = None  # None = not yet tested

def _try_mysql():
    global _mysql_available
    if _mysql_available is False:
        return None
    try:
        import mysql.connector
        from mysql.connector import Error
        conn = mysql.connector.connect(**DB_CONFIG)
        _mysql_available = True
        return conn
    except Exception as e:
        if _mysql_available is None:
            logger.warning(f"MySQL unavailable, using local JSON store: {e}")
        _mysql_available = False
        return None


def get_db_connection():
    """Get database connection (MySQL or None)"""
    return _try_mysql()


def execute_query(query, params=None, fetch=False):
    """Execute SQL query; returns None if MySQL is down."""
    connection = _try_mysql()
    if connection is None:
        return None
    try:
        import mysql.connector
        from mysql.connector import Error
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        if fetch:
            result = cursor.fetchall()
        else:
            connection.commit()
            result = cursor.rowcount
        cursor.close()
        return result
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        try:
            connection.rollback()
        except Exception:
            pass
        return None
    finally:
        try:
            if connection and connection.is_connected():
                connection.close()
        except Exception:
            pass


# ── User functions ───────────────────────────────────────────────────────────

def get_user_by_email(email):
    result = execute_query("SELECT * FROM users WHERE email = %s", (email,), fetch=True)
    if result is not None:
        return result[0] if result else None
    # fallback
    store = _load_store()
    for u in store['users']:
        if u['email'] == email:
            return u
    return None


def get_user_by_id(user_id):
    result = execute_query(
        "SELECT user_id, name, email, role FROM users WHERE user_id = %s",
        (user_id,), fetch=True
    )
    if result is not None:
        return result[0] if result else None
    # fallback
    store = _load_store()
    for u in store['users']:
        if u['user_id'] == user_id:
            return {k: u[k] for k in ('user_id', 'name', 'email', 'role') if k in u}
    return None


def create_user(name, email, password_hash, role='user'):
    result = execute_query(
        "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
        (name, email, password_hash, role)
    )
    if result is not None:
        return result > 0
    # fallback
    store = _load_store()
    new_id = max((u['user_id'] for u in store['users']), default=0) + 1
    store['users'].append({
        'user_id': new_id,
        'name': name,
        'email': email,
        'password_hash': password_hash,
        'role': role,
        'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
    })
    _save_store(store)
    return True


# ── Review / Prediction / Explanation functions ──────────────────────────────

def create_review(user_id, review_text, rating=None, sentiment=None, confidence=None):
    result = execute_query(
        "INSERT INTO reviews (user_id, review_text, rating, sentiment, confidence) VALUES (%s, %s, %s, %s, %s)",
        (user_id, review_text, rating, sentiment, confidence)
    )
    if result is not None:
        conn = _try_mysql()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT LAST_INSERT_ID()")
                rid = cur.fetchone()[0]
                cur.close()
                conn.close()
                return rid
            except Exception:
                pass
    # fallback
    store = _load_store()
    new_id = max((r['review_id'] for r in store['reviews']), default=0) + 1
    store['reviews'].append({
        'review_id': new_id, 'user_id': user_id, 'review_text': review_text,
        'rating': rating, 'sentiment': sentiment, 'confidence': confidence,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    })
    _save_store(store)
    return new_id


def create_prediction(review_id, sentiment, confidence, model_version):
    result = execute_query(
        "INSERT INTO predictions (review_id, sentiment, confidence, model_version) VALUES (%s, %s, %s, %s)",
        (review_id, sentiment, confidence, model_version)
    )
    if result is not None:
        conn = _try_mysql()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT LAST_INSERT_ID()")
                pid = cur.fetchone()[0]
                cur.close()
                conn.close()
                return pid
            except Exception:
                pass
    # fallback
    store = _load_store()
    new_id = max((p['prediction_id'] for p in store['predictions']), default=0) + 1
    store['predictions'].append({
        'prediction_id': new_id, 'review_id': review_id,
        'sentiment': sentiment, 'confidence': confidence,
        'model_version': model_version,
        'predicted_at': time.strftime('%Y-%m-%d %H:%M:%S')
    })
    _save_store(store)
    return new_id


def create_explanation(prediction_id, keyword, impact_score, word_position=None):
    result = execute_query(
        "INSERT INTO explanations (prediction_id, keyword, impact_score, word_position) VALUES (%s, %s, %s, %s)",
        (prediction_id, keyword, impact_score, word_position)
    )
    if result is not None:
        return True
    # fallback
    store = _load_store()
    store['explanations'].append({
        'prediction_id': prediction_id, 'keyword': keyword,
        'impact_score': impact_score, 'word_position': word_position
    })
    _save_store(store)
    return True


def get_reviews_for_training(limit=None, offset=0):
    query = """
        SELECT review_text, sentiment, rating
        FROM reviews
        WHERE sentiment IS NOT NULL
        ORDER BY timestamp DESC
    """
    if limit:
        query += f" LIMIT {limit} OFFSET {offset}"
    result = execute_query(query, fetch=True)
    if result is not None:
        return result
    # fallback
    store = _load_store()
    reviews = [r for r in store['reviews'] if r.get('sentiment')]
    reviews.sort(key=lambda r: r.get('timestamp', ''), reverse=True)
    if limit:
        reviews = reviews[offset:offset + limit]
    return [{'review_text': r['review_text'], 'sentiment': r['sentiment'], 'rating': r.get('rating')} for r in reviews]


def get_new_reviews_count_since_training(model_version=None):
    if model_version:
        query = """
            SELECT COUNT(*) as count FROM reviews
            WHERE timestamp > (
                SELECT trained_on FROM model_logs WHERE model_version = %s ORDER BY trained_on DESC LIMIT 1
            )
        """
        result = execute_query(query, (model_version,), fetch=True)
    else:
        result = execute_query("SELECT COUNT(*) as count FROM reviews WHERE sentiment IS NOT NULL", fetch=True)
    if result is not None:
        return result[0]['count'] if result else 0
    # fallback
    store = _load_store()
    return len([r for r in store['reviews'] if r.get('sentiment')])


def log_model_training(model_version, accuracy, loss, training_samples, validation_samples,
                       epochs, training_time_seconds, model_path, notes=None):
    result = execute_query(
        """INSERT INTO model_logs
           (model_version, accuracy, loss, training_samples, validation_samples,
            epochs, training_time_seconds, model_path, notes)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (model_version, accuracy, loss, training_samples, validation_samples,
         epochs, training_time_seconds, model_path, notes)
    )
    if result is not None:
        return True
    # fallback
    store = _load_store()
    store['model_logs'].append({
        'model_version': model_version, 'accuracy': accuracy, 'loss': loss,
        'training_samples': training_samples, 'validation_samples': validation_samples,
        'epochs': epochs, 'training_time_seconds': training_time_seconds,
        'model_path': model_path, 'notes': notes,
        'trained_on': time.strftime('%Y-%m-%d %H:%M:%S')
    })
    _save_store(store)
    return True


def get_latest_model_version():
    result = execute_query(
        "SELECT model_version, accuracy, trained_on FROM model_logs ORDER BY trained_on DESC LIMIT 1",
        fetch=True
    )
    if result is not None:
        return result[0] if result else None
    # fallback
    store = _load_store()
    logs = sorted(store['model_logs'], key=lambda l: l.get('trained_on', ''), reverse=True)
    return logs[0] if logs else None
