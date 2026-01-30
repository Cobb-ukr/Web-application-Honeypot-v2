# Adaptive Honeypot System with ML-Based Threat Detection

A sophisticated honeypot system that combines rule-based attack detection with machine learning to identify and trap malicious users while allowing legitimate access. The system implements an adaptive three-strike threat scoring mechanism to distinguish between attackers and legitimate users.

## Table of Contents

- [Features](#features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Starting the Application](#starting-the-application)
- [API Endpoints](#api-endpoints)
- [Model Retraining](#model-retraining)
- [Frontend](#frontend)
- [Database](#database)
- [Documentation](#documentation)

## Features

- **Hybrid Threat Detection**: Combines rule-based signatures with ML-based anomaly detection
- **Adaptive Threat Scoring**: Tracks threat scores per IP address with automatic escalation
- **Three-Strike System**: After 3 failed login attempts or detected attacks, users are redirected to honeypot
- **Dynamic Model Retraining**: Automatically retrains ML model on historical attack data
- **Honeypot Environment**: Fake dashboard and file system to trap and study attacker behavior
- **Admin Dashboard**: Real-time monitoring of attacks, threat levels, and honeypot sessions
- **User Authentication**: Secure login with password validation and malicious input detection

## System Architecture

```
honeypot-ai/
├── backend/
│   ├── main.py              # FastAPI application and startup logic
│   ├── auth.py              # Login/registration endpoints
│   ├── honeypot.py          # Fake dashboard and file system
│   ├── admin.py             # Admin dashboard and management endpoints
│   ├── ai_engine.py         # ML model and threat detection
│   ├── threat_scoring.py    # Threat score management
│   ├── database.py          # SQLAlchemy models
│   └── __pycache__/
├── frontend/
│   ├── login.html           # Login page
│   ├── welcome.html         # Welcome page for authenticated users
│   ├── dashboard.html       # Admin dashboard
│   ├── attack_details.html  # Attack log details view
│   ├── honeypot_session_details.html
│   ├── honeypot_ui.html     # Fake honeypot dashboard
│   ├── scripts.js           # Frontend JavaScript
│   └── styles.css           # Frontend styling
├── database/
│   └── honeypot.db          # SQLite database (created at runtime)
├── logs/
│   └── model_log.txt        # Model retraining logs
├── models/
│   └── model_v*.pkl         # Trained ML models (versioned)
├── requirements.txt
└── seed_attack_data.py      # Script to populate database with sample data
```

## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Step 1: Clone or Download the Project

```bash
cd /mnt/OldVolume/New_projects/final\ cyber
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Required Packages

The `requirements.txt` includes:

- **fastapi**: Web framework for building APIs
- **uvicorn**: ASGI server for running FastAPI
- **sqlalchemy**: ORM for database management
- **scikit-learn**: Machine learning library
- **pydantic**: Data validation
- **joblib**: Model serialization
- **numpy**: Numerical computations
- **python-multipart**: Form data parsing
- **jinja2**: Template engine
- **python-jose**: JWT authentication
- **passlib**: Password hashing
- **aiofiles**: Async file operations
- **user_agents**: User-agent parsing

## Configuration

### Environment Variables

Before starting the application, set the retraining mode:

```bash
# Mode options: "all", "recent", "skip"
export RETRAIN_MODE=skip
```

**Retraining Modes:**

- `skip`: Do not retrain the model (default)
- `all`: Retrain on all historical attack data in the database
- `recent`: Retrain on attacks from the last 7 days

### Database

The SQLite database is automatically created at `database/honeypot.db` on first run. No additional setup is required.

## Starting the Application

### Option 1: Using Python Directly

```bash
cd honeypot-ai
export RETRAIN_MODE=skip  # Or "all" / "recent"
python backend/main.py
```

### Option 2: Using Uvicorn

```bash
cd honeypot-ai
export RETRAIN_MODE=skip
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Option 3: Using the Windows Batch File (Windows Only)

```bash
cd honeypot-ai
run_honeypot.bat
```

### Accessing the Application

Once the server is running:

- **Login Page**: http://localhost:8000/static/login.html
- **Admin Dashboard**: http://localhost:8000/static/dashboard.html (after login as admin)
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative API Docs**: http://localhost:8000/redoc (ReDoc)

## API Endpoints

### Authentication Endpoints

#### **POST /auth/login**
Login with username and password.

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (Success):**
```json
{
  "token": "real-jwt-token-user",
  "redirect": "/static/welcome.html",
  "message": "Login Successful"
}
```

**Response (Malicious Input):**
```json
{
  "token": "fake-jwt-token-honeypot",
  "redirect": "/honeypot/dashboard",
  "message": "Login Successful"
}
```

**Response (Failed Login):**
```
HTTP 401 Unauthorized
{"detail": "Invalid credentials"}
```

---

#### **POST /auth/register**
Register a new user account.

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{"message": "User registered"}
```

---

### Honeypot Endpoints

#### **GET /honeypot/dashboard**
Load the fake honeypot dashboard interface.

**Query Parameters:**
- `session_id` (optional): Session ID for tracking user activity

**Response:** HTML page (honeypot_ui.html)

---

#### **GET /honeypot/files**
Return a list of fake files in the honeypot system.

**Query Parameters:**
- `session_id` (optional): Session ID

**Response:**
```json
{
  "files": [
    {"name": "passwords.txt", "size": "1.2KB", "type": "text"},
    {"name": "financial_report_2024.pdf", "size": "4.5MB", "type": "pdf"},
    {"name": "admin_backup.sql", "size": "120MB", "type": "sql"},
    {"name": "private_key.pem", "size": "2KB", "type": "key"}
  ]
}
```

---

#### **GET /honeypot/files/{filename}**
Request content of a fake file (returns empty content).

**Query Parameters:**
- `session_id` (optional): Session ID

**Response:** Empty string (tracks file access)

---

#### **POST /honeypot/execute**
Simulate command execution on the fake system.

**Request:**
```json
{
  "command": "ls -la",
  "output": "drwxr-xr-x  5 root root 4096 Jan 30 12:00 ."
}
```

**Response:**
```json
{"status": "success", "output": "drwxr-xr-x  5 root root 4096 Jan 30 12:00 ."}
```

---

#### **POST /honeypot/logout**
End a honeypot session.

**Request:**
```json
{
  "session_id": "uuid-string"
}
```

**Response:**
```json
{"message": "Session ended", "success": true}
```

---

### Admin Endpoints

#### **GET /api/admin/stats**
Get comprehensive statistics including attack counts, threat levels, and recent activity logs.

**Response:**
```json
{
  "total_logins": 42,
  "total_attacks": 15,
  "active_threats": 3,
  "attack_distribution": {
    "SQLi": 8,
    "XSS": 4,
    "Failed Login": 3,
    "Successful Login": 42
  },
  "recent_logs": [
    {
      "id": 1,
      "ip": "192.168.1.100",
      "type": "SQLi",
      "username": "admin",
      "password": "-",
      "attack_detail": "' OR '1'='1",
      "time": "2026-01-30T12:34:56Z",
      "time_formatted": "2026-01-30 12:34:56"
    }
  ]
}
```

---

#### **GET /api/admin/log/{log_id}**
Get detailed information about a specific attack log.

**Path Parameters:**
- `log_id`: Integer ID of the attack log

**Response:**
```json
{
  "id": 1,
  "ip": "192.168.1.100",
  "type": "SQLi",
  "username": "admin",
  "password": "HIDDEN",
  "attack_detail": "' OR '1'='1",
  "time": "2026-01-30T12:34:56Z",
  "time_formatted": "2026-01-30 12:34:56",
  "user_agent": "Mozilla/5.0...",
  "endpoint": "/auth/login",
  "method": "POST",
  "headers": {...},
  "threat_score": 0.9
}
```

---

#### **GET /api/admin/honeypot_session/{session_id}**
Get detailed information about a honeypot session.

**Path Parameters:**
- `session_id`: UUID of the honeypot session

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "ip_address": "192.168.1.101",
  "start_time": "2026-01-30T12:00:00Z",
  "end_time": "2026-01-30T12:15:30Z",
  "start_time_formatted": "2026-01-30 12:00:00",
  "end_time_formatted": "2026-01-30 12:15:30",
  "is_active": false,
  "duration_seconds": 930,
  "user_agent": "Mozilla/5.0...",
  "headers": {...},
  "commands": [
    {
      "timestamp": "2026-01-30T12:00:05Z",
      "type": "Terminal Command",
      "command": "whoami",
      "response": "root"
    }
  ],
  "num_commands": 5
}
```

---

#### **POST /api/admin/block_ip**
Manually block an IP address.

**Request:**
```json
{
  "ip": "192.168.1.100"
}
```

**Response:**
```json
{"message": "IP 192.168.1.100 blocked successfully"}
```

---

#### **POST /api/admin/unblock_ip**
Unblock a previously blocked IP address.

**Request:**
```json
{
  "ip": "192.168.1.100"
}
```

**Response:**
```json
{"message": "IP 192.168.1.100 unblocked successfully"}
```

---

#### **POST /api/admin/clear_logs**
Clear all attack logs, threat scores, and honeypot sessions.

**Response:**
```json
{
  "message": "Successfully deleted 45 attack logs, reset 12 threat scores, and cleared 3 honeypot sessions"
}
```

---

### Static Files

#### **GET /static/{filename}**
Access frontend HTML, CSS, and JavaScript files.

**Available Files:**
- `/static/login.html` - Login page
- `/static/welcome.html` - User welcome page
- `/static/dashboard.html` - Admin dashboard
- `/static/attack_details.html` - Attack detail view
- `/static/honeypot_session_details.html` - Session detail view
- `/static/scripts.js` - Frontend JavaScript
- `/static/styles.css` - Frontend styling

---

#### **GET /**
Redirects to `/static/login.html`

---

## Model Retraining

The system uses an adaptive machine learning model that can be automatically retrained on historical data during startup.

### Retraining Modes

Set the `RETRAIN_MODE` environment variable before starting the application:

#### **1. Skip Mode (Default)**

```bash
export RETRAIN_MODE=skip
python backend/main.py
```

- Does not retrain the model on startup
- Uses the latest existing model from the `models/` directory
- Fastest startup time
- Use this for production deployments

#### **2. All Mode**

```bash
export RETRAIN_MODE=all
python backend/main.py
```

- Retrains the model on **all historical attack data** in the database
- Creates a new model version (e.g., `model_v3.pkl`)
- Useful for periodic retraining with complete historical data
- Longer startup time depending on database size
- Use this for improving model accuracy over time

#### **3. Recent Mode**

```bash
export RETRAIN_MODE=recent
python backend/main.py
```

- Retrains the model on attacks from the **last 7 days only**
- Creates a new model version
- Good balance between data coverage and startup speed
- Use this for regular updates (e.g., daily restarts)

### Training Data

The model is trained on the following features extracted from payloads:

1. **Payload Length**: Total character count
2. **Entropy**: Randomness measure (0-8 scale)
3. **Special Characters**: Count of non-alphanumeric characters
4. **Suspicious Keywords**: Count of known attack keywords (select, union, script, alert, etc.)

### Model Output

The model predicts:
- **Class 0**: Clean/Benign payload
- **Class 1**: Malicious/Attack payload

Predictions with probability > 0.75 of class 1 are flagged as "Anomaly" type attacks.

### Retraining Log

All retraining activity is logged to `logs/model_log.txt`:

```
======================================================================
MODEL RETRAINING LOG - 2026-01-30 12:34:56
======================================================================

Retraining Mode: ALL

Status: SUCCESS
Message: Successfully retrained model on 127 samples. Saved as model_v3
Samples Used: 127
Model Version: v3

======================================================================
```

---

## Frontend

The system includes a responsive web interface with the following pages:

### **Login Page** (`login.html`)
- Username and password input
- Registration link
- Responsive design

### **Welcome Page** (`welcome.html`)
- Greeting for authenticated users
- Navigation to admin dashboard (for admins)

### **Admin Dashboard** (`dashboard.html`)
- Real-time attack statistics
- Attack distribution charts
- Recent activity feed
- IP blocking/unblocking controls
- Log export and filtering
- Honeypot session monitoring

### **Attack Details** (`attack_details.html`)
- Detailed view of individual attacks
- Payload information
- Request headers
- Threat score and classification

### **Honeypot Session Details** (`honeypot_session_details.html`)
- View of attacker interactions with fake system
- Command history
- Duration and timeline
- IP and user-agent information

---

## Database

### Schema

The application uses SQLite with the following main tables:

#### **users**
- `id`: Primary key
- `username`: Unique username
- `password_hash`: Hashed password
- `role`: "user" or "admin"

#### **attack_logs**
- `id`: Primary key
- `ip_address`: Source IP
- `timestamp`: Attack time
- `payload`: Attack payload (JSON)
- `attack_type`: Classification (SQLi, XSS, Failed Login, etc.)
- `threat_score`: Associated threat score
- `user_agent`: Browser/client info
- `endpoint`: Target endpoint
- `method`: HTTP method
- `headers`: Request headers (JSON)

#### **threat_scores**
- `id`: Primary key
- `ip_address`: Unique IP address
- `score`: Cumulative threat score
- `last_updated`: Last update timestamp

#### **blocked_ips**
- `id`: Primary key
- `ip_address`: Unique IP address
- `reason`: Block reason
- `timestamp`: Block time

#### **honeypot_sessions**
- `id`: Primary key
- `session_id`: Unique session ID
- `ip_address`: Source IP
- `start_time`: Session start
- `end_time`: Session end
- `is_active`: Active status
- `commands`: JSON array of executed commands
- `user_agent`: Client info
- `headers`: Request headers (JSON)

#### **attack_signatures**
- `id`: Primary key
- `pattern`: Regex pattern
- `type`: Attack type
- `description`: Pattern description

---

## Documentation

Additional documentation is available in the `docs/` folder:

- **[MODEL_LOGGING_GUIDE.md](docs/MODEL_LOGGING_GUIDE.md)** - Detailed information about model logging and performance tracking
- **[RETRAINING_GUIDE.md](docs/RETRAINING_GUIDE.md)** - Comprehensive guide for model retraining strategies

---

## Threat Scoring System

### How It Works

1. **Failed Login Attempt**: +1.0 score per attempt
2. **Malicious Payload**: Score based on detection type
   - SQLi/Command Injection: +0.9
   - XSS/Anomaly: +0.8
   - Path Traversal: +0.8
3. **Successful Login**: Score reset to 0.0 (user is legitimate)

### Three-Strike System

- **Score < 3.0**: Normal login page shown, 401 error on failed login
- **Score ≥ 3.0**: User is redirected to honeypot dashboard
- **Honeypot**: Fake interface to study attacker behavior and collect data

---

## Troubleshooting

### ModuleNotFoundError: No module named 'sqlalchemy'

**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Port 8000 Already in Use

**Solution:** Use a different port:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8001
```

### Database Errors

**Solution:** Delete the database file to reset:
```bash
rm honeypot-ai/database/honeypot.db
```

The database will be automatically recreated with the default schema on next startup.

### Model Not Retraining

**Solution:** Ensure you've set the environment variable:
```bash
export RETRAIN_MODE=all  # or "recent"
python backend/main.py
```

Check `logs/model_log.txt` for retraining status.

---

## Security Notes

- **Passwords**: Currently stored as plain text for demo purposes. Use proper hashing in production.
- **JWT Tokens**: Authentication tokens should be validated for production use.
- **CORS**: Currently allows all origins. Restrict in production.
- **Database**: Use a production-grade database (PostgreSQL) for deployment.

---

## License

This project is provided as-is for educational and research purposes.
