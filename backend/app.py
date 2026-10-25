"""
Flask Application - Main Entry Point
Product Review Sentiment Classification System
"""

import os
import sys
from pathlib import Path

# Add parent directory to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from flask import Flask, request, jsonify
try:
    from flask_cors import CORS
    HAS_CORS = True
except ImportError:
    HAS_CORS = False
from datetime import datetime
import logging

from backend.config import DEBUG, TRAINING_THRESHOLD
from backend.auth import register_user_handler, login_user_handler, token_required
from backend.model_manager import get_model_manager, reload_model
from backend.db_utils import (
    create_review, create_prediction, create_explanation,
    get_latest_model_version, log_model_training,
    get_new_reviews_count_since_training
)
from backend.auto_train import (
    trigger_auto_training, update_csv_from_database, check_training_threshold,
    sync_db_to_csv, trigger_manual_training
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
if HAS_CORS:
    CORS(app, resources={r"/api/*": {"origins": "*", "allow_headers": ["Authorization", "Content-Type"], "methods": ["GET", "POST", "OPTIONS"]}})
else:
    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        return response

# Get model manager
model_manager = get_model_manager()


@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        'message': 'Product Review Sentiment Classification API',
        'version': '1.0.0',
        'endpoints': {
            'register': '/api/register',
            'login': '/api/login',
            'predict': '/api/predict',
            'explain': '/api/explain',
            'chat': '/api/chat',
            'train': '/api/train',
            'status': '/api/status'
        }
    })


@app.route('/api/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.get_json()
        
        if not data or 'name' not in data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        result = register_user_handler(
            data['name'],
            data['email'],
            data['password']
        )
        
        if result['success']:
            return jsonify({'message': result['message']}), 201
        else:
            return jsonify({'error': result['error']}), 400
    
    except Exception as e:
        logger.error(f"Error in register: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Missing email or password'}), 400
        
        result = login_user_handler(data['email'], data['password'])
        
        if result['success']:
            return jsonify({
                'token': result['token'],
                'user': result['user']
            }), 200
        else:
            return jsonify({'error': result['error']}), 401
    
    except Exception as e:
        logger.error(f"Error in login: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/predict', methods=['POST'])
@token_required
def predict():
    """Predict sentiment for review"""
    try:
        data = request.get_json()
        
        if not data or 'review_text' not in data:
            return jsonify({'error': 'Missing review_text'}), 400
        
        review_text = data['review_text']
        rating = data.get('rating')
        user_id = request.current_user['user_id']
        
        # Predict sentiment
        sentiment, confidence, probabilities = model_manager.predict(review_text, return_probabilities=True)
        model_version = model_manager.get_model_version()

        # Get explanation (always, for response)
        try:
            explanation = model_manager.explain(review_text, method='simple')
        except Exception as ex:
            logger.warning(f"Explain failed: {ex}")
            explanation = {'method': 'none', 'word_contributions': []}

        # Save review to database
        review_id = create_review(
            user_id=user_id,
            review_text=review_text,
            rating=rating,
            sentiment=sentiment,
            confidence=confidence
        )

        # Save prediction and explanations
        if review_id:
            prediction_id = create_prediction(
                review_id=review_id,
                sentiment=sentiment,
                confidence=confidence,
                model_version=model_version
            )
            if prediction_id and explanation.get('word_contributions'):
                for word_info in explanation['word_contributions']:
                    create_explanation(
                        prediction_id=prediction_id,
                        keyword=word_info['word'],
                        impact_score=word_info['impact_score'],
                        word_position=word_info.get('position')
                    )

        # Check if auto-training is needed
        if check_training_threshold():
            # Trigger auto-training in background (async)
            try:
                import threading
                thread = threading.Thread(target=trigger_auto_training)
                thread.daemon = True
                thread.start()
            except Exception as e:
                logger.warning(f"Failed to trigger auto-training: {e}")
        
        return jsonify({
            'sentiment': sentiment,
            'confidence': confidence,
            'probabilities': probabilities,
            'model_version': model_version,
            'review_id': review_id,
            'explanation': explanation
        }), 200
    
    except Exception as e:
        logger.error(f"Error in predict: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/explain', methods=['POST'])
@token_required
def explain():
    """Explain sentiment prediction"""
    try:
        data = request.get_json()
        
        if not data or 'review_text' not in data:
            return jsonify({'error': 'Missing review_text'}), 400
        
        review_text = data['review_text']
        method = data.get('method', 'simple')
        
        # Get prediction
        sentiment, confidence = model_manager.predict(review_text)
        
        # Get explanation
        explanation = model_manager.explain(review_text, method=method)
        
        return jsonify({
            'sentiment': sentiment,
            'confidence': confidence,
            'explanation': explanation
        }), 200
    
    except Exception as e:
        logger.error(f"Error in explain: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat', methods=['POST'])
@token_required
def chat():
    """Chatbot-style interaction"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message'}), 400
        
        message = data['message'].lower()
        review_text = data.get('review_text', '')
        
        # Simple intent detection
        if 'analyze' in message or 'sentiment' in message or 'predict' in message:
            if review_text:
                sentiment, confidence = model_manager.predict(review_text)
                explanation = model_manager.explain(review_text)
                
                response = f"The sentiment is **{sentiment}** with {confidence:.2%} confidence."
                if explanation.get('word_contributions'):
                    top_words = sorted(
                        explanation['word_contributions'],
                        key=lambda x: abs(x['impact_score']),
                        reverse=True
                    )[:5]
                    words_str = ', '.join([w['word'] for w in top_words])
                    response += f" Key words: {words_str}."
                
                return jsonify({
                    'response': response,
                    'sentiment': sentiment,
                    'confidence': confidence,
                    'explanation': explanation
                }), 200
            else:
                return jsonify({'response': 'Please provide a review text to analyze.'}), 400
        
        elif 'why' in message or 'negative' in message or 'positive' in message:
            if review_text:
                sentiment, confidence = model_manager.predict(review_text)
                explanation = model_manager.explain(review_text)
                
                if explanation.get('word_contributions'):
                    positive_words = [w for w in explanation['word_contributions'] if w['impact_score'] > 0.1]
                    negative_words = [w for w in explanation['word_contributions'] if w['impact_score'] < -0.1]
                    
                    response = f"The sentiment is {sentiment} because: "
                    if positive_words:
                        words = ', '.join([w['word'] for w in positive_words[:3]])
                        response += f"Positive words: {words}. "
                    if negative_words:
                        words = ', '.join([w['word'] for w in negative_words[:3]])
                        response += f"Negative words: {words}."
                else:
                    response = f"The sentiment is {sentiment} based on the overall context."
                
                return jsonify({
                    'response': response,
                    'sentiment': sentiment,
                    'confidence': confidence,
                    'explanation': explanation
                }), 200
            else:
                return jsonify({'response': 'Please provide a review text to explain.'}), 400
        
        elif 'words' in message or 'influence' in message:
            if review_text:
                explanation = model_manager.explain(review_text)
                
                if explanation.get('word_contributions'):
                    top_words = sorted(
                        explanation['word_contributions'],
                        key=lambda x: abs(x['impact_score']),
                        reverse=True
                    )[:10]
                    
                    response = "The most influential words are: "
                    words_list = []
                    for w in top_words:
                        impact = "positive" if w['impact_score'] > 0 else "negative"
                        words_list.append(f"{w['word']} ({impact})")
                    response += ', '.join(words_list) + "."
                    
                    return jsonify({
                        'response': response,
                        'explanation': explanation
                    }), 200
            else:
                return jsonify({'response': 'Please provide a review text.'}), 400
        
        else:
            return jsonify({
                'response': 'I can help you analyze reviews. Try asking: "Analyze this review" or "Why is it negative?"'
            }), 200
    
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/train', methods=['POST'])
@token_required
def train():
    """Trigger manual model training (any user). Runs in background; model reloads when done."""
    import threading
    try:
        def run_training_and_reload():
            try:
                if trigger_manual_training():
                    reload_model()
                    logger.info("Model reloaded after training.")
            except Exception as e:
                logger.error(f"Background training error: {e}")

        thread = threading.Thread(target=run_training_and_reload, daemon=True)
        thread.start()
        return jsonify({
            'message': 'Training started. CSV synced from database. Model will update when training completes (check back in a few minutes).'
        }), 200
    except Exception as e:
        logger.error(f"Error in train: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload-csv', methods=['POST'])
@token_required
def upload_csv():
    """Upload CSV file: insert rows into DB, then sync CSV with DB. Columns: review_text, sentiment, rating."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        file = request.files['file']
        if file.filename == '' or not file.filename.lower().endswith('.csv'):
            return jsonify({'error': 'Please upload a CSV file'}), 400

        import pandas as pd
        import io
        user_id = request.current_user['user_id']

        content = file.read().decode('utf-8', errors='replace')
        df = pd.read_csv(io.StringIO(content), engine='python', on_bad_lines='skip')
        required = ['review_text', 'sentiment']
        if not all(c in df.columns for c in required):
            return jsonify({'error': 'CSV must have columns: review_text, sentiment (and optionally rating)'}), 400

        if 'rating' not in df.columns:
            df['rating'] = None
        df = df[['review_text', 'sentiment', 'rating']].dropna(subset=['review_text', 'sentiment'])
        df['sentiment'] = df['sentiment'].str.strip().str.lower()
        df = df[df['sentiment'].isin(['positive', 'negative', 'neutral'])]

        added = 0
        for _, row in df.iterrows():
            review_text = str(row['review_text']).strip()
            if not review_text:
                continue
            rating = row['rating'] if pd.notna(row['rating']) else None
            if rating is not None:
                try:
                    rating = int(rating)
                    if rating < 1 or rating > 5:
                        rating = None
                except (ValueError, TypeError):
                    rating = None
            rid = create_review(user_id=user_id, review_text=review_text, rating=rating, sentiment=row['sentiment'], confidence=None)
            if rid:
                added += 1

        sync_db_to_csv()
        return jsonify({
            'message': f'Uploaded {added} reviews. Database and CSV updated.',
            'added': added
        }), 200
    except Exception as e:
        logger.error(f"Error in upload_csv: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/status', methods=['GET'])
def status():
    """Get system status"""
    try:
        model_version = model_manager.get_model_version()
        model_accuracy = model_manager.get_model_accuracy()
        
        # Get latest model info from database
        latest_model = get_latest_model_version()
        
        # Check training threshold
        threshold_reached = check_training_threshold()
        new_reviews_count = get_new_reviews_count_since_training(model_version)
        
        return jsonify({
            'model_loaded': model_manager.model is not None,
            'model_version': model_version,
            'model_accuracy': model_accuracy,
            'latest_training': latest_model,
            'training_threshold': TRAINING_THRESHOLD,
            'new_reviews_count': new_reviews_count,
            'threshold_reached': threshold_reached
        }), 200
    
    except Exception as e:
        logger.error(f"Error in status: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Ensure directories exist
    from backend.config import MODEL_DIR, DATA_DIR
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check if model is loaded
    if model_manager.model is None:
        logger.warning("Model not loaded. Please train the model first using: python ml/train_model.py")
    
    # Run app
    app.run(host='0.0.0.0', port=5000, debug=DEBUG)
