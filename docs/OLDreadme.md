# Sentinel AI - Adaptive Honeypot System

## Overview
**Sentinel AI** is an advanced, academic-grade adaptive honeypot system designed to detect, deceive, and analyze attackers using a hybrid AI approach (Rule-Based + Machine Learning detection).

The system appears as a legitimate "Secure Enterprise Portal" but dynamically switches malicious actors to a **deceptive high-interaction honeypot** upon detecting threats such as SQL Injection, XSS, or Command Injection.

---

## Key Features

### Core Security & AI
- **Hybrid AI Engine**:
    - **Layer 1 (Signatures)**: Instantly detects known patterns (SQLi, XSS, Cmd Injection).
    - **Layer 2 (Machine Learning)**: Uses random forest classifiers to detect anomalies based on entropy, length, and keyword density.
- **Threat Scoring System**: Tracks IP reputation.
    - **3-Strike Rule**: 3 Failed logins = Immediate ban (Score > 3.0).
    - **Attack Detection**: Instant ban (Score +5.0).
- **Maximum Deception Mode**: Blocked IPs are **silently redirected** to the honeypot instead of receiving a "403 Access Denied" error, keeping the attacker unaware they have been caught.

### User Interface (Frontend)
- **Dual-View Login**:
    - **Legitimate Users**: Redirected to a `Welcome` page.
    - **Attackers**: Redirected to the `Honeypot Dashboard`.
- **Registration System**: Functional sign-up flow for legitimate users.
- **Modern Glassmorphism Design**: High-end UI to maintain illusion of a secure corporate tool.

### The Deceptive Honeypot
- **Fake Dashboard**: Looks like a real employee portal with "Pending Reviews" and "Messages".
- **Simulated Terminal**: A functional-looking Ubuntu shell (`user@internal:~$`).
    - Supports commands: `ls`, `cat`, `download`, `help`, `clear`.
    - **Hidden Files**: Attackers can "find" and "download" fake confidential documents (`passwords.txt`, `network_map.png`).

### Admin Dashboard (SOC)
- **Live Attack Feed**: Real-time table of all login attempts.
- **Granular Metrics**:
    - **Total Logins**: Successful legitimate logins.
    - **Total Attacks**: Failed logins + Malicious payloads.
    - **Active Threats**: IPs currently flagged/blocked.
- **Forensic Tools**:
    - **Password Eye**: Toggle to reveal the masked password attackers tried to use.
    - **Payload Analysis**: Shows the exact malicious string (e.g., `' OR 1=1`).
    - **Manual Block**: One-click IP blocking.

---

### Project Structure
```
honeypot-ai/
├── backend/
│   ├── main.py         # Entry Point & Router Config
│   ├── auth.py         # Authentication & Attack Logic (The "Brain")
│   ├── admin.py        # Dashboard API & Metrics
│   ├── honeypot.py     # Fake Routes (Terminal/Files)
│   ├── ai_engine.py    # ML Model & Detection Rule Engine
│   ├── threat_scoring.py # IP Reputation Logic
│   └── database.py     # SQLite Models
├── frontend/
│   ├── login.html      # The Trap (Login Page)
│   ├── dashboard.html  # The Watchtower (Admin Page)
│   ├── honeypot_ui.html# The Cage (Fake Dashboard)
│   ├── styles.css      # UI Styling
│   └── scripts.js      # Frontend Logic (Terminal Simulation)
├── database/           # Persistent Storage (honeypot.db)
└── run_honeypot.bat    # One-click Startup Script
```

---

##  Setup & Usage

### 1. Prerequisites
*   Python 3.9+ installed.
*   `pip` package manager.

### 2. Installation
Open your terminal in the project folder:
```powershell
pip install -r requirements.txt
```

### 3. Run the System
Simply double-click **`run_honeypot.bat`** OR run:
```powershell
.\run_honeypot.bat
```
*(Manual Command: navigate to /honeypot-ai directory and run  `uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000`)*

### 4. Access Points
*   **Vulnerable Login (The Trap)**: `http://localhost:8000/static/login.html`
*   **Admin Dashboard (SOC)**: `http://localhost:8000/static/dashboard.html`

---

### Attack Simulation Guide (How to Test)

Use **Kali Linux** `curl` or a browser to test the defenses.

### Scenario 1: The "Hacker" (SQL Injection)
Attempt to bypass login using a classic SQL payload.
**Payload:** `admin' OR 1=1 --`
1.  Enter this as the **Username**.
2.  Password can be anything.
3.  **Result**: The system will pretend to log you in ("Login Successful") but seamlessly redirect you to the **Honeypot Dashboard**.
4.  **Admin View**: You will see a **RED** alert for "SQLi".

### Scenario 2: The "Brute Force" (3-Strike Rule)
Try to guess a password 3 times.
1.  Enter `admin` / `wrongpass`. (Result: "Invalid Credentials").
2.  Repeat.
3.  **3rd Attempt**: The system logic (`threat_scoring.py`) sees your score hit 3.0. It triggers the trap. You are let "in" to the Honeypot to waste your time.
4.  **Admin View**: You will see **ORANGE** alerts for "Failed Login".

### Scenario 3: The "Script Kiddie" (XSS)
Try to inject a script.
**Payload:** `<script>alert(1)</script>`
- **Result**: Immediate ban and redirect to Honeypot.

### Scenario 4: Inside the Honeypot
Once trapped in the `Honeypot Dashboard`:
1.  Click inside the **Terminal**.
2.  Type `ls` to see hidden files.
3.  Type `cat passwords.txt` to read fake credentials.
4.  Type `download passwords.txt` to download the decoy file.
5.  *Everything you do here is logged.*

---

### Ethical Disclaimer
This tool is developed for **academic research and defensive security testing only**.
- **Passive Defense**: This system does **not** launch counter-attacks or hack back.
- **Privacy**: Passwords are masked by default in logs (Eye toggle available for forensic analysis only).
- Do not use this Codebase to target systems you do not own or have explicit permission to test.

