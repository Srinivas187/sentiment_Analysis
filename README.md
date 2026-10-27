# Sentiment Analysis

A full-stack sentiment analysis project for product reviews, built with Python, Flask, TensorFlow/Keras, MySQL, and a React-style frontend. The system classifies reviews as positive, negative, or neutral, stores results in a database, and provides explainability for model decisions.

## Overview

This project is designed to analyze customer/product feedback using machine learning and provide a user-friendly interface to:

- register and log in users
- submit product reviews
- classify review sentiment in real time
- view explanation highlights for predictions
- interact with a chatbot for review analysis
- trigger model training and monitor training status

The backend exposes REST API endpoints, while the frontend provides a dashboard and report interface for end users.

## Features

- Real-time sentiment classification for product reviews
- Support for positive, negative, and neutral sentiment labels
- User authentication and authorization
- MySQL-backed review and prediction storage
- Model explainability for key review words
- Chatbot-style sentiment assistance
- Auto-training trigger based on review volume
- Frontend dashboard for predictions and analytics
- Dummy model fallback for local development and demo environments

## Tech Stack

### Backend
- Python 3.10+
- Flask
- Flask-CORS
- Flask-JWT-Extended
- MySQL / MySQL Connector
- SQLAlchemy

### Machine Learning
- TensorFlow / Keras
- NumPy, Pandas, Scikit-learn
- Gensim
- NLTK
- SHAP

### Frontend
- HTML / CSS / JavaScript
- React-style frontend structure in `frontend/`

## Repository Structure

```text
sentiment_Analysis/
├── backend/
│   ├── __init__.py
│   ├── app.py
│   ├── auth.py
│   ├── auto_train.py
│   ├── config.py
│   ├── db_utils.py
│   └── model_manager.py
├── database/
│   ├── init_db.py
│   └── schema.sql
├── frontend/
│   ├── README.md
│   ├── package.json
│   ├── package-lock.json
│   ├── public/
│   └── src/
├── ml/
│   ├── __init__.py
│   ├── create_dummy_model_files.py
│   ├── explainability.py
│   ├── model.py
│   └── preprocessing.py
├── data/
│   └── ...
├── .gitignore
├── check_and_install.py
├── project_structure.txt
├── requirements.txt
├── run_all.py
├── run_project.py
├── setup_db_fixed.py
├── README.md
└── SETUP.md
```

## Getting Started

### Prerequisites

Before running the project, make sure you have:

- Python 3.10 or later
- MySQL Server installed and running
- Git
- Node.js and npm (for frontend development)

### Clone the Repository

```bash
git clone https://github.com/Srinivas187/sentiment_Analysis.git
cd sentiment_Analysis
```

### Create a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Set Up the Database

The database can be initialized using the project scripts.

```bash
python setup_db_fixed.py
```

Or use the database initialization helper from the project runner.

## Running the Application

### Option 1: Run Everything with the Project Script

This is the easiest way to start the app locally.

```bash
python run_all.py
```

This script will:
- install dependencies (if needed)
- initialize the database
- create dummy model artifacts if missing
- start the backend API
- start the frontend static server

### Option 2: Start Components Manually

#### Start the backend

```bash
python backend/app.py
```

The backend runs on:

```text
http://localhost:5000
```

#### Start the frontend

```bash
cd frontend
npm install
npm start
```

The frontend usually runs on:

```text
http://localhost:3000
```

## API Endpoints

The backend provides the following routes:

### Authentication
- `POST /api/register`
- `POST /api/login`

### Prediction
- `POST /api/predict`
- `POST /api/explain`
- `POST /api/chat`

### Training / Monitoring
- `POST /api/train`
- `GET /api/status`
- `POST /api/upload-csv`

### Root
- `GET /`

## Example API Request

### Register user

```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123"
  }'
```

### Predict sentiment

```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "review_text": "This product is excellent and works perfectly.",
    "rating": 5
  }'
```

## Model & Explanation

The project uses a text classification model to identify the sentiment of product reviews. It also includes explainability features that highlight the words contributing most strongly to the prediction.

This helps users understand why a review was classified as positive, negative, or neutral.

## Data Flow

1. User registers or logs in.
2. Review text is submitted through the frontend or API.
3. The backend preprocesses the review and sends it to the model.
4. The model predicts the sentiment.
5. The prediction is stored in the database.
6. Explainability data is generated and returned to the client.
7. Training can be triggered automatically or manually.

## Configuration

The project config is mainly stored in:

- `backend/config.py`
- `.env` files (if used locally)

Set your MySQL and application settings there before running the project in a local environment.

## Notes

- This project is intended for learning, demo, and academic use.
- The repository includes a dummy model generation script so that local development can proceed even before a trained model is available.
- For production-grade deployment, additional security, validation, and infrastructure hardening should be implemented.

## License

This project is available for educational and personal use. Please check repository ownership and usage rights before production deployment or commercial redistribution.

## Contributors

This repository is maintained and developed as a sentiment analysis / product review classification project.

## Acknowledgements

- Flask for API development
- TensorFlow and Keras for deep learning
- MySQL for data storage
- NLTK and Gensim for NLP processing
- SHAP for explainability

---

If you want, I can also generate a more polished version with badges, screenshots, architecture diagram, and a project-specific demo section for GitHub.
