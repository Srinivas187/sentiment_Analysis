"""
Model Manager Module
Handles model loading, prediction, and versioning
"""

import os
import sys
import pickle
import numpy as np
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from ml.model import load_model
from ml.preprocessing import tokenize, texts_to_sequences, int_to_label
from ml.explainability import explain_prediction_simple, explain_prediction_shap
from backend.config import MODEL_DIR, MAX_SEQUENCE_LENGTH

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages model loading and prediction"""
    
    def __init__(self):
        self.model = None
        self.vocab = None
        self.metadata = None
        self.load_latest_model()
    
    def load_latest_model(self):
        """Load latest trained model"""
        try:
            # Load vocabulary
            vocab_path = MODEL_DIR / 'vocab.pkl'
            if vocab_path.exists():
                with open(vocab_path, 'rb') as f:
                    self.vocab = pickle.load(f)
                logger.info(f"Loaded vocabulary from {vocab_path}")
            else:
                logger.warning(f"Vocabulary not found at {vocab_path}")
                return False
            
            # Load model metadata
            metadata_path = MODEL_DIR / 'model_metadata.pkl'
            if metadata_path.exists():
                with open(metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
                logger.info(f"Loaded model metadata: {self.metadata.get('model_version', 'unknown')}")
            
            # Load model
            model_path = MODEL_DIR / 'best_model.h5'
            if not model_path.exists():
                # Try to find any model file
                model_files = list(MODEL_DIR.glob('model_*.h5'))
                if model_files:
                    model_path = model_files[0]
                else:
                    logger.error("No model file found")
                    return False
            
            self.model = load_model(str(model_path))
            
            if self.model is None:
                logger.error("Failed to load model")
                return False
            
            logger.info(f"Model loaded successfully from {model_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def preprocess_text(self, text):
        """Preprocess text for prediction"""
        if self.vocab is None:
            raise ValueError("Vocabulary not loaded")
        
        # Tokenize
        tokens = tokenize(text)
        
        # Convert to sequence
        sequence = [self.vocab.get(token, self.vocab.get('<unk>', 1)) for token in tokens]
        
        # Pad or truncate
        if len(sequence) < MAX_SEQUENCE_LENGTH:
            sequence = sequence + [self.vocab.get('<pad>', 0)] * (MAX_SEQUENCE_LENGTH - len(sequence))
        else:
            sequence = sequence[:MAX_SEQUENCE_LENGTH]
        
        return np.array([sequence])
    
    def predict(self, review_text, return_probabilities=False):
        """Predict sentiment for review text"""
        if self.model is None:
            raise ValueError("Model not loaded")
        
        # Preprocess
        sequence = self.preprocess_text(review_text)
        
        # Predict
        predictions = self.model.predict(sequence, verbose=0)
        predicted_class = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class])
        sentiment = int_to_label(predicted_class)
        
        probabilities = {
            'negative': float(predictions[0][0]),
            'neutral': float(predictions[0][1]),
            'positive': float(predictions[0][2])
        }
        
        if return_probabilities:
            return sentiment, confidence, probabilities
        else:
            return sentiment, confidence
    
    def explain(self, review_text, method='simple'):
        """Explain prediction"""
        if self.model is None or self.vocab is None:
            raise ValueError("Model or vocabulary not loaded")
        
        try:
            if method == 'shap':
                explanation = explain_prediction_shap(
                    self.model,
                    review_text,
                    self.vocab,
                    max_length=MAX_SEQUENCE_LENGTH
                )
            else:
                explanation = explain_prediction_simple(
                    self.model,
                    review_text,
                    self.vocab,
                    max_length=MAX_SEQUENCE_LENGTH
                )
            
            return explanation
        except Exception as e:
            logger.error(f"Error explaining prediction: {e}")
            return {
                'method': 'error',
                'word_contributions': []
            }
    
    def get_model_version(self):
        """Get current model version"""
        if self.metadata:
            return self.metadata.get('model_version', 'unknown')
        return 'unknown'
    
    def get_model_accuracy(self):
        """Get current model accuracy"""
        if self.metadata:
            return self.metadata.get('accuracy', 0.0)
        return 0.0


# Global model manager instance
model_manager = ModelManager()


def get_model_manager():
    """Get model manager instance"""
    return model_manager


def reload_model():
    """Reload latest model"""
    global model_manager
    model_manager = ModelManager()
    return model_manager.model is not None
