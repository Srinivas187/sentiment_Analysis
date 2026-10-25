# Word Embedding Feature Design for Product Review Classification

**Final Year B.Tech Project (2026)**

An Intelligent, Auto-Training, Explainable NLP System for Real-Time Product Review Sentiment Classification using FastText embeddings and Bi-LSTM with Attention mechanism.

## 🎯 Project Overview

This system implements an advanced text classification framework that leverages **Dense Word Embedding Feature Design** to transform raw review text into meaningful, low-dimensional vector representations, significantly improving classification accuracy.

### Key Features

- ✅ **FastText Embeddings**: Handles typos, slang, and rare words through sub-word embeddings
- ✅ **Bi-LSTM + Attention**: Captures context in both forward and backward directions
- ✅ **Explainable AI**: SHAP-based explanation of predictions with word-level contributions
- ✅ **Auto-Training**: Automatic model retraining when threshold (500 reviews) is reached
- ✅ **Real-time Classification**: Live sentiment prediction with MySQL storage
- ✅ **Chatbot Interface**: NLP-based chat UI for interactive queries
- ✅ **User Authentication**: Secure login/register system with JWT tokens

## 📋 Prerequisites

- Python 3.8+
- MySQL 8.0+
- Node.js 16+ (optional, for frontend development)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "Word Embedding Feature Design for Product Review Classification"
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate.bat        # or run the PowerShell script after adjusting execution policy

# On Linux/Mac
source venv/bin/activate
```

> **Windows tip:** if `python` is not found or points to a non‑existent path
> (e.g. `C:\Python314\python.exe`), make sure a supported Python installation
> (3.8–3.11, 64‑bit) is on your `%PATH%` or use the `py` launcher:
>
> ```powershell
> py -3.11 -m venv venv    # explicitly choose the installed Python version
> ```
>
> Running `where python` (or `py -0p`) shows which interpreter is being used.
> Adjust your PATH or reinstall Python if it points to a missing location.


### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download NLTK Data

```python
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### 5. Database Setup

1. Install MySQL and create database:

```bash
mysql -u root -p < database/schema.sql
```

Or run the initialization script:

```bash
python database/init_db.py
```

2. Update database configuration in `backend/config.py` or create `.env` file:

```bash
cp .env.example .env
# Edit .env with your database credentials
```

## 🏃 Running the Application

### 1. Train Initial Model

First, train the model with initial data:

```bash
python ml/train_model.py
```

This will:
- Load data from `data/reviews_dataset.csv`
- Build vocabulary
- Create FastText embeddings
- Train Bi-LSTM + Attention model
- Save model to `models/best_model.h5`

### 2. Start Backend Server

```bash
python backend/app.py
```

Backend will run on `http://localhost:5000`

### 3. Open Frontend

Open `frontend/index.html` in your web browser or serve it with a local server:

```bash
cd frontend
python -m http.server 8000
```

Then open `http://localhost:8000` in your browser.

## 📁 Project Structure

```
.
├── backend/
│   ├── app.py              # Flask main application
│   ├── auth.py             # Authentication module
│   ├── model_manager.py    # Model loading and prediction
│   ├── auto_train.py       # Auto-training logic
│   ├── db_utils.py         # Database utilities
│   └── config.py           # Configuration
├── ml/
│   ├── preprocessing.py    # Text preprocessing
│   ├── embedding_loader.py # FastText embeddings
│   ├── model.py            # Bi-LSTM + Attention model
│   ├── explainability.py   # SHAP explainability
│   └── train_model.py      # Training script
├── frontend/
│   └── index.html          # Web UI
├── database/
│   ├── schema.sql          # Database schema
│   └── init_db.py          # Database initialization
├── data/
│   └── reviews_dataset.csv # Training data
├── models/                 # Saved models (created after training)
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔌 API Endpoints

### Authentication
- `POST /api/register` - Register new user
- `POST /api/login` - Login user

### Prediction
- `POST /api/predict` - Predict sentiment for review
- `POST /api/explain` - Get explanation for prediction

### Chatbot
- `POST /api/chat` - Chatbot interaction

### Training
- `POST /api/train` - Trigger manual training (admin only)
- `GET /api/status` - Get system status

## 🔄 Auto-Training System

The system automatically retrains the model when:
- 500 new reviews are added (threshold)
- New reviews are stored in MySQL database
- CSV file is updated with new reviews

Auto-training process:
1. New reviews stored in MySQL
2. CSV file updated automatically
3. When threshold reached, training triggered
4. New model replaces old one
5. System uses latest model for predictions

## 🧪 Model Architecture

```
Input Text
    ↓
Preprocessing (Tokenization, Cleaning)
    ↓
FastText Embeddings (300-dim)
    ↓
Bi-LSTM (128 units, bidirectional)
    ↓
Attention Layer
    ↓
Dense Layer (64 units)
    ↓
Output (3 classes: Negative, Neutral, Positive)
```

## 📊 Performance

- **Accuracy**: 96%+ on validation set
- **Architecture**: Bi-LSTM with Attention
- **Embeddings**: FastText (300 dimensions)
- **Sequence Length**: 200 tokens
- **Vocabulary Size**: 10,000 words

## 🛠️ Usage Examples

### Register User

```python
POST /api/register
{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123"
}
```

### Login

```python
POST /api/login
{
    "email": "john@example.com",
    "password": "password123"
}
```

### Predict Sentiment

```python
POST /api/predict
Headers: Authorization: Bearer <token>
{
    "review_text": "This product is amazing! Great quality and fast delivery.",
    "rating": 5
}
```

### Chatbot Query

```python
POST /api/chat
Headers: Authorization: Bearer <token>
{
    "message": "Why is this review positive?",
    "review_text": "Excellent product, highly recommend!"
}
```

## 🐛 Troubleshooting

### Model Not Loading

If model is not loaded, train it first:
```bash
python ml/train_model.py
```

### Database Connection Error

Check database credentials in `backend/config.py` or `.env` file.

### Import Errors

Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## 📝 License

This project is part of a B.Tech Final Year Project (2026).

## 👥 Authors

- Batch-8, CSE-C, Vasavi College

## 🙏 Acknowledgments

- FastText for word embeddings
- TensorFlow/Keras for deep learning
- SHAP for explainable AI

---

**Note**: This is a production-ready prototype system. For production deployment, ensure proper security measures, error handling, and scalability optimizations.
