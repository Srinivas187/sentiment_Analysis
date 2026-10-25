# Setup Guide - Product Review Sentiment Classification

## Quick Start (Step-by-Step)

### Step 1: Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Database Setup

1. **Install MySQL** (if not installed)
   - Download from: https://dev.mysql.com/downloads/mysql/
   - Remember your root password

2. **Create Database**

   Option A: Using SQL script
   ```bash
   mysql -u root -p < database/schema.sql
   ```

   Option B: Using Python script
   ```bash
   python database/init_db.py
   ```

3. **Configure Database**

   Edit `backend/config.py` or create `.env` file:
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'user': 'root',
       'password': 'your_password',  # Change this
       'database': 'sentiment_analysis_db',
   }
   ```

### Step 3: Download NLTK Data

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### Step 4: Train Initial Model

**IMPORTANT**: Train the model before starting the server!

```bash
python ml/train_model.py
```

This will:
- Load data from `data/reviews_dataset.csv` (60+ reviews already included)
- Build vocabulary and embeddings
- Train Bi-LSTM + Attention model
- Save model to `models/best_model.h5`
- Target: 96%+ accuracy

Training takes ~5-10 minutes depending on your hardware.

### Step 5: Start Backend Server

```bash
python backend/app.py
```

Server will run on: `http://localhost:5000`

You should see:
```
* Running on http://0.0.0.0:5000
```

### Step 6: Run Frontend (React.js)

**Prerequisite:** Node.js 16+ must be installed. Download from https://nodejs.org/

**Commands to run the frontend:**

```bash
# Navigate to frontend folder
cd frontend

# Install dependencies (first time only)
npm install

# Start React development server
npm start
```

- The app will open automatically in your browser at **http://localhost:3000**
- If it doesn’t, open **http://localhost:3000** manually
- Keep this terminal open while using the app

**Other useful frontend commands:**

```bash
# Build for production (creates optimized build in frontend/build)
npm run build

# Run tests
npm test
```

**Important:** The backend must be running at `http://localhost:5000` before using the frontend. Start the backend in a **separate terminal** with `python backend/app.py`.

---

## Frontend Setup – Full Analysis

### What the frontend is

- **Stack:** React 18 with React Router, Axios, Bootstrap 5
- **Entry:** `frontend/src/index.js` → `App.js` → routes
- **API base URL:** `http://localhost:5000/api` (set in `frontend/src/utils/api.js`)

### Correct way to run the frontend

| Step | Command | Purpose |
|------|---------|--------|
| 1 | `cd frontend` | Go to frontend folder |
| 2 | `npm install` | Install Node dependencies (first time only) |
| 3 | `npm start` | Start React dev server on port 3000 |

### Windows (PowerShell / CMD)

```powershell
cd frontend
npm install
npm start
```

### Linux / Mac

```bash
cd frontend
npm install
npm start
```

### Two terminals needed

1. **Terminal 1 – Backend**
   ```bash
   python backend/app.py
   ```
   Backend runs at **http://localhost:5000**

2. **Terminal 2 – Frontend**
   ```bash
   cd frontend
   npm start
   ```
   Frontend runs at **http://localhost:3000**

### If the frontend can’t reach the backend

- Ensure the backend is running first.
- If the frontend runs on a different host/port, set the API URL:
  - Create `frontend/.env` with:
    ```
    REACT_APP_API_URL=http://localhost:5000/api
    ```
  - Restart `npm start` after changing `.env`.

### Frontend project structure

```
frontend/
├── public/
│   └── index.html          # HTML template
├── src/
│   ├── index.js            # Entry point
│   ├── App.js              # Routes & auth state
│   ├── index.css           # Global styles
│   ├── components/         # React screens
│   │   ├── Login.js
│   │   ├── Register.js
│   │   ├── Dashboard.js
│   │   ├── ReviewInput.js
│   │   ├── ResultDisplay.js
│   │   ├── ExplanationScreen.js
│   │   ├── Chatbot.js
│   │   ├── AutoTrainingStatus.js
│   │   └── Analytics.js
│   └── utils/
│       ├── api.js          # Backend API calls
│       └── auth.js         # Token storage
├── package.json            # Dependencies & scripts
└── README.md
```

---

## Test Login Credentials

After running the seed script once, you can use this account to login:

| Field    | Value              |
|----------|--------------------|
| **Email**    | `test@example.com` |
| **Password** | `test123`          |

**Create the test user (run once from project root):**

```bash
python scripts/seed_test_user.py
```

Then login in the frontend (http://localhost:3000) or via API with the credentials above.

**How it maps:**
- **Frontend Login** → `POST /api/login` with `{ "email": "test@example.com", "password": "test123" }`
- **Backend** → checks `users` table in MySQL (`sentiment_analysis_db`) → returns JWT **token** + **user** (user_id, name, email, role)
- **Frontend** → stores token in `localStorage` and sends `Authorization: Bearer <token>` on every API call (predict, chat, etc.)
- **Database** → `users` table: `user_id`, `name`, `email`, `password_hash`, `role`; reviews/predictions link via `user_id`

---

## Using the Application

### 1. Register/Login
- Click "Register" tab to create new account
- Fill in: Name, Email, Password
- Click "Register" button
- Then login with your credentials

### 2. Analyze Review
- Enter product review text
- Optionally select rating (1-5)
- Click "Analyze Sentiment"
- View results:
  - Sentiment (Positive/Negative/Neutral)
  - Confidence percentage
  - Probability distribution
  - Word-level explanations
  - Highlighted review text

### 3. Chatbot
- Enter review in text area above
- In chatbot, try:
  - "Analyze this review"
  - "Why is it negative?"
  - "What words influenced the sentiment?"

### 4. Auto-Training and CSV
- **Auto Train Now** (Training Status page): Syncs DB → CSV, then retrains the model. No threshold; any user can run it.
- **Upload CSV** (same page): Upload a CSV with columns `review_text`, `sentiment` (positive/negative/neutral), `rating` (optional). Rows are added to the database and the CSV file is updated automatically. Then use **Auto Train Now** to retrain.
- System also auto-retrains when 500+ new reviews exist (threshold-based).
- **Mapping:** User reviews → MySQL `reviews` table; CSV `data/reviews_dataset.csv` is kept in sync with DB (full overwrite on sync). Training uses the CSV; predictions use the latest model.

## Troubleshooting

### Error: "Model not loaded"
**Solution**: Train the model first
```bash
python ml/train_model.py
```

### Error: "Database connection failed"
**Solution**: 
1. Check MySQL is running
2. Verify credentials in `backend/config.py`
3. Run `python database/init_db.py`

### Error: "Module not found"
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Error: "NLTK data not found"
**Solution**: Download NLTK data
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### Low Accuracy (< 90%)
**Solution**:
1. Check if training completed successfully
2. Verify CSV has enough data (should have 60+ reviews)
3. Try training again with more epochs
4. Check training logs for errors

### Error: "npm is not recognized" or "npm: command not found"
**Solution:** Install Node.js from https://nodejs.org/ (LTS version). Restart the terminal after installing.

### Error: Frontend shows "Network Error" or can't login
**Solution:** Backend must be running. Start it in another terminal: `python backend/app.py`. Ensure it runs on http://localhost:5000.

### Error: 401 when clicking "Auto Train Now" or other actions
**Solution:** Your session expired. Log in again (token lasts 24 hours). The app will redirect you to the login page on 401. Ensure backend CORS allows the frontend origin and `Authorization` header.

### Error: "Port 3000 is already in use"
**Solution:** Either close the app using port 3000, or run on another port:
```bash
# Windows (PowerShell / CMD)
set PORT=3001 && npm start

# Linux/Mac
PORT=3001 npm start
```
Then open http://localhost:3001

## API Testing

### Using curl:

**Register:**
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"test123"}'
```

**Login:**
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

**Predict (Replace TOKEN with your JWT token):**
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"review_text":"This product is amazing!"}'
```

## Project Structure

```
├── backend/          # Flask backend API (run: python backend/app.py)
├── ml/               # Machine learning models
├── frontend/         # React.js UI (run: cd frontend then npm start)
├── database/         # Database schemas
├── data/             # Training data CSV
├── models/           # Saved models (created after training)
└── requirements.txt  # Python dependencies
```

## Quick Reference – All Commands in Order

**First-time setup (run from project root):**

```bash
# 1. Virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

# 2. Python dependencies
pip install -r requirements.txt

# 3. NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# 4. Database (ensure MySQL is running)
python database/init_db.py

# 5. (Optional) Create test login user
python scripts/seed_test_user.py
# Then use: Email test@example.com, Password test123

# 6. Train model
python ml/train_model.py
```

**Frontend (first time):**

```bash
cd frontend
npm install
```

**Every time you run the project:**

**Terminal 1 – Backend:**
```bash
python backend/app.py
```
→ Backend: **http://localhost:5000**

**Terminal 2 – Frontend:**
```bash
cd frontend
npm start
```
→ Frontend: **http://localhost:3000** (browser opens automatically)

---

## Next Steps

1. ✅ Complete setup (Steps 1-6)
2. ✅ Train initial model
3. ✅ Start backend server (Terminal 1)
4. ✅ Start frontend (Terminal 2): `cd frontend` then `npm start`
5. ✅ Open http://localhost:3000 and register / login
6. ✅ Analyze sample reviews
7. ✅ Test chatbot functionality
8. ✅ Add more reviews to test auto-training

## Support

For issues or questions:
- Check README.md for detailed documentation
- Review error messages in console
- Verify all prerequisites are installed
- Check database connection

---

**Note**: This is a complete, production-ready system. All features are implemented and working end-to-end!


login detiles:

"email":"test@example.com 
"password":"test123