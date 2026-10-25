-- Database Schema for Word Embedding Feature Design Project
-- MySQL Database Creation Script

CREATE DATABASE IF NOT EXISTS sentiment_analysis_db;
USE sentiment_analysis_db;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL, 
    role ENUM('user', 'admin') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Reviews Table
CREATE TABLE IF NOT EXISTS reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    review_text TEXT NOT NULL,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    sentiment VARCHAR(20),
    confidence DECIMAL(5, 4),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_timestamp (timestamp)
);

-- Predictions Table
CREATE TABLE IF NOT EXISTS predictions (
    prediction_id INT AUTO_INCREMENT PRIMARY KEY,
    review_id INT NOT NULL,
    sentiment VARCHAR(20) NOT NULL,
    confidence DECIMAL(5, 4) NOT NULL,
    model_version VARCHAR(50),
    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (review_id) REFERENCES reviews(review_id) ON DELETE CASCADE,
    INDEX idx_review_id (review_id),
    INDEX idx_sentiment (sentiment)
);

-- Explanations Table (for SHAP/Explainability)
CREATE TABLE IF NOT EXISTS explanations (
    explanation_id INT AUTO_INCREMENT PRIMARY KEY,
    prediction_id INT NOT NULL,
    keyword VARCHAR(255) NOT NULL,
    impact_score DECIMAL(10, 6) NOT NULL,
    word_position INT,
    FOREIGN KEY (prediction_id) REFERENCES predictions(prediction_id) ON DELETE CASCADE,
    INDEX idx_prediction_id (prediction_id)
);

-- Model Training Logs
CREATE TABLE IF NOT EXISTS model_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    model_version VARCHAR(50) NOT NULL,
    trained_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accuracy DECIMAL(5, 4) NOT NULL,
    loss DECIMAL(10, 6) NOT NULL,
    training_samples INT NOT NULL,
    validation_samples INT NOT NULL,
    epochs INT NOT NULL,
    training_time_seconds INT,
    model_path VARCHAR(500),
    notes TEXT,
    INDEX idx_model_version (model_version),
    INDEX idx_trained_on (trained_on)
);

-- Auto Training Queue (for threshold-based retraining)
CREATE TABLE IF NOT EXISTS training_queue (
    queue_id INT AUTO_INCREMENT PRIMARY KEY,
    status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
    review_count INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP NULL,
    error_message TEXT
);
