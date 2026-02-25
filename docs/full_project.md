# Comprehensive Project Documentation: Adaptive Honeypot System with ML-Based Threat Detection

**Date:** February 22, 2026  
**Project Type:** Cybersecurity/Threat Detection System  
**Technology Stack:** Python, FastAPI, SQLAlchemy, scikit-learn, XGBoost  
**Status:** Production Ready

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [Technical Methodologies](#technical-methodologies)
5. [Data Flow & Processing](#data-flow--processing)
6. [Machine Learning Implementation](#machine-learning-implementation)
7. [Security Mechanisms](#security-mechanisms)
8. [Frontend & User Interface](#frontend--user-interface)
9. [Database Schema](#database-schema)
10. [API Endpoints](#api-endpoints)
11. [Email & Reporting System](#email--reporting-system)
12. [Testing & Deployment](#testing--deployment)

---

## Project Overview

### What It Is

The **Adaptive Honeypot System** is a sophisticated cybersecurity detection and analysis platform that combines rule-based attack detection with machine learning to identify, trap, and analyze malicious users while permitting legitimate access. The system serves dual purposes:

1. **Active Defense**: Detects and isolates attackers through dynamic threat scoring
2. **Threat Intelligence**: Analyzes attacker behavior patterns to build threat profiles

### What It Does

The system implements a **three-strike threat escalation mechanism** with **hybrid detection methodology**:

- **Real-time attack detection** on login attempts and API requests
- **Adaptive threat scoring** that accumulates risk indicators per IP address
- **Automatic honeypot redirection** when threat thresholds are exceeded
- **Terminal emulation** that simulates a compromised Linux system
- **Command profiling** using machine learning to classify attacker intent and skill level
- **Automated session reporting** with AI-generated attacker profiles
- **Email alerts** with comprehensive attack documentation

### Core Philosophy

The system doesn't simply block attackers—it **deceptively redirects them to a fake environment** while collecting behavioral data for post-analysis. This allows analysts to understand attack methodologies and attacker sophistication levels.

---

## Architecture

### High-Level System Design

```
┌─────────────────────────────────────────────────────────────────┐
│                        HONEYPOT SYSTEM                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
         ┌──────▼────────┐ ┌─▼──────────┐ ┌─▼───────────────┐
         │  FRONTEND     │ │  BACKEND   │ │  ATTACKER       │
         │               │ │  SERVICES  │ │  PROFILER       │
         ├───────────────┤ ├────────────┤ ├─────────────────┤
         │• Login Page   │ │• Auth Mgmt │ │• Step 1: Index  │
         │• Dashboard    │ │• Threat    │ │  Playbooks      │
         │• Attack Logs  │ │  Scoring   │ │                 │
         │• Honeypot UI  │ │• AI Engine │ │• Step 2: Gen    │
         └───────────────┘ │• Terminal  │ │  Synthetic Data │
                           │  Emulator  │ │                 │
                           │• Reporting │ │• Step 3:        │
                           │  Module    │ │  Aggregate      │
                           │• Email     │ │  Features       │
                           │  Service   │ │                 │
                           └────────────┘ │• Step 4: Train  │
                                          │  Models         │
                                          │                 │
                                          │• Step 5: Infer  │
                                          │  Profiles       │
                                          └─────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │  SQLITE DATABASE   │
                    ├────────────────────┤
                    │• Users             │
                    │• Attack Logs       │
                    │• Threat Scores     │
                    │• Honeypot Sessions │
                    │• Blocked IPs       │
                    │• Attack Signatures │
                    └────────────────────┘
```

### Directory Structure

```
honeypot-ai/
├── backend/                          # FastAPI application core
│   ├── main.py                       # Application entry point & startup
│   ├── auth.py                       # Authentication & login processing
│   ├── honeypot.py                   # Fake dashboard & terminal emulation
│   ├── admin.py                      # Admin dashboard & threat management
│   ├── ai_engine.py                  # ML model & threat detection
│   ├── threat_scoring.py             # Threat score calculations
│   ├── database.py                   # SQLAlchemy ORM models
│   ├── email_service.py              # SMTP email handling
│   ├── email_templates.py            # Alert email templates
│   ├── email_templates_report.py    # Session report email templates
│   ├── playbook_loader.py            # YAML playbook loading
│   ├── debug_counters.py             # Debug logging utilities
│   │
│   ├── terminal_emulator/            # Simulated Linux terminal
│   │   ├── __init__.py
│   │   ├── command_filter.py         # Command validation & blocking
│   │   ├── state_manager.py          # File system state tracking
│   │   └── state_history/            # Persistent state snapshots
│   │
│   ├── database/                     # SQLite database file location
│   └── logs/                         # Model training logs
│
├── frontend/                         # HTML/CSS/JS user interfaces
│   ├── login.html                    # Login entry point
│   ├── welcome.html                  # Legitimate user dashboard
│   ├── dashboard.html                # Admin monitoring dashboard
│   ├── attack_details.html           # Detailed attack log viewer
│   ├── honeypot_ui.html              # Fake compromised system UI
│   ├── honeypot_session_details.html # Honeypot session details
│   ├── scripts.js                    # Frontend JavaScript
│   ├── styles.css                    # Styling
│   └── terminal.html                 # Terminal emulator HTML
│
├── attacker_profiler/                # ML pipeline for behavior analysis
│   ├── __init__.py
│   ├── step1_playbook.py             # Index playbooks, extract features
│   ├── step2_generate.py             # Generate synthetic training data
│   ├── step3_aggregate.py            # Feature aggregation
│   ├── step4_train.py                # Train Random Forest models
│   ├── step5_infer.py                # Inference on real sessions
│   ├── incremental_trainer.py        # Continuous model improvement
│   ├── common.py                     # Shared utilities
│   ├── demo_runner.py                # Demo/testing interface
│   ├── manage_training.py            # Training job management
│   ├── commands.json                 # Attack command corpus
│   ├── model_store/                  # Trained model storage
│   └── real_sessions/                # Captured real attack sessions
│
├── reportGen/                        # Session reporting module
│   ├── __init__.py
│   └── session_report_generator.py   # Report generation logic
│
├── playbook_data/                    # YAML attack playbooks
│   ├── gtfobins.json                # GTFOBins database
│   └── atomic-red-team/             # ATT&CK framework tactics
│
├── models/                           # Trained ML models
│   └── model_v*.pkl                 # Versioned model snapshots
│
├── seed_attack_data.py               # Database initialization
├── test_email.py                     # Email service testing
└── requirements.txt                  # Python dependencies
```

---

## Core Components

### 1. Authentication Module (`auth.py`)

**Purpose:** Validates login credentials and detects malicious authentication attempts

**Key Functions:**

#### `login()` Endpoint
- **Input:** Username, password, HTTP request object
- **Process:**
  1. Check if IP is blocked (hard-blocked IPs receive 403)
  2. Analyze username for injection patterns (SQL, XSS, command injection)
  3. Validate credentials against user database
  4. Implement failed login tracking with three-strike system:
     - Strike 1: Log failed attempt, don't update threat score
     - Strike 2: Log failed attempt, don't update threat score
     - Strike 3: Log as "Brute Force Attempt", add 3.0 to threat score
  5. Successful login resets threat score to 0.0
  6. Malicious input patterns trigger automatic honeypot redirection
  7. Return JWT token with appropriate redirect URL

**Attack Detection Logic:**
- Username analyzed for payloads (password excluded for false positive reduction)
- AI engine computes threat score from payload features
- Threshold (0.7 confidence) determines if attack is detected
- Attack type classification: SQLi, XSS, CommandInjection, etc.

**Output:**
- Login attempt logged to `AttackLog` table
- Threat score updated in `ThreatScore` table
- Response: Either legitimate dashboard, honeypot, or 401 error

---

### 2. Threat Scoring System (`threat_scoring.py`)

**Purpose:** Manages dynamic threat accumulation and risk assessment per IP address

**Threat Scorer Class:**

```python
class ThreatScorer:
    threshold_block: 5.0      # Score for permanent honeypot redirection
    threshold_alert: 3.0      # Score for initial honeypot redirection
    failed_login_threshold: 3 # Consecutive failed logins before attack flag
```

**Key Methods:**

#### `update_score()`
```
Input: ip_address, attack_score (float), attack_type (string)
Process:
  1. Query ThreatScore table for existing entry
  2. Create if not exists (initial score = 0.0)
  3. Add attack_score to cumulative score
  4. Update last_updated timestamp
  5. Return new total score
```

**Scoring Logic:**
- **SQLi/CommandInjection:** High impact, add full AI engine score (typically 0.5-1.0)
- **XSS:** Medium impact, add AI engine score
- **Brute Force:** Fixed 3.0 points per attack
- **Anomaly:** Variable based on feature analysis

#### `track_failed_login()`
```
Input: ip_address
Process:
  1. Retrieve or create ThreatScore entry
  2. Increment failed_login_count
  3. Return True if count >= 3 (triggering attack behavior)
  4. If True, caller updates threat score separately
```

#### `should_redirect()`
```
Input: ip_address
Returns: Boolean - True if IP should be redirected to honeypot
Logic:
  - Returns True if threat_score >= threshold_alert (3.0)
  - Returns True if IP is in BlockedIP table
  - Returns False otherwise (allow legitimate access)
```

#### `get_risk_level()`
```
Scoring bands:
  - 0-3:   Low risk
  - 3-5:   Medium risk
  - 5+:    High risk
```

---

### 3. AI Engine (`ai_engine.py`)

**Purpose:** Real-time threat detection using hybrid rule-based + ML approach

**Detection Pipeline:**

#### Rule-Based Signature Matching

**SQL Injection Patterns:**
```regex
1. (\%27)|(\')|(\-\-)|(\%23)|(#)           # Comments & quotes
2. ((\%3D)|(=))[^\n]*((\%27)|(\')|(;))     # Assignment with escaped chars
3. \w*((\%27)|(\'))((\%6F)|o)((\%72)|r)    # OR operators
4. ((\%27)|(\'))(union)                    # UNION queries
5. exec(\s|\+)+(s|x)p\w+                   # SQL procedures
6. select\s+.*\s+from                      # SELECT statements
7. or\s+1\s*=\s*1                          # Tautologies
```

**Cross-Site Scripting (XSS) Patterns:**
```regex
1. <script>                                 # Script tags
2. javascript:                              # JS protocol
3. onload\s*=                              # Event handlers
4. onerror\s*=                             # Error handlers
5. <img\s+src                              # Image source
6. alert\(                                 # Alert functions
```

**Command Injection Patterns:**
```regex
1. cmd\.exe                                 # Windows shell
2. /bin/sh                                  # Unix shells
3. /bin/bash
4. \s+;\s+                                 # Command separators
5. \s+\|\s+                                # Pipes
6. \s+&&\s+                                # AND operators
```

**Path Traversal Patterns:**
```regex
1. \.\./                                    # Relative traversal
2. \.\.\                                    # Backslash traversal
```

#### Feature Extraction

```python
def extract_features(payload: str) -> List[float]:
    """
    Input: Raw user payload (username/URL/input)
    Returns: [length, entropy, special_chars_count, keyword_count]
    
    Features:
      1. length: Character count of payload
      2. entropy: Shannon entropy (0-8 bits typically)
      3. special_chars: Count of non-alphanumeric characters
      4. keywords: Count of dangerous keywords (select, union, script, etc.)
    
    These features feed the ML model for probabilistic classification.
    """
```

**Entropy Calculation:**
```
Shannon Entropy = -Σ(p_x * log₂(p_x)) for x in [0-255]

Where p_x = frequency of character code x in text

High entropy (>5.0) indicates:
  - Encoded payloads
  - Compressed data
  - Encrypted content
  - Obfuscated attack attempts

Legitimate text typically has entropy 3.5-4.5
```

#### ML-Based Classification

**Model Type:** Random Forest Classifier (10 decision trees for production)

**Training Data:**
- **Malicious samples:** SQLi attempts, XSS payloads, command injections
- **Benign samples:** Normal usernames, typical input

**Classification:**
```
Model Output: 0 = Safe, 1 = Malicious
Confidence Threshold: 0.7 (70% probability)

If model.predict() = 1 AND probability > 0.7:
    threat_score += model.predict_proba()[1]  # Add confidence as score
```

**Model Persistence:**
- Models stored as versioned pickle files: `models/model_v1.pkl`, `model_v2.pkl`, etc.
- Latest model loaded on startup
- Automatic versioning prevents overwrites

#### Retraining Logic

```python
def retrain_on_historical_data(retrain_mode: str) -> bool:
    """
    Retrain model on accumulated attack data.
    
    Modes:
      - "all":    Retrain on entire attack history
      - "recent": Retrain on last 7 days of attacks
      - "skip":   Skip retraining (default for performance)
    
    Process:
      1. Query AttackLog table
      2. Filter by mode (time-based or all)
      3. Extract features from payloads
      4. Train new Random Forest
      5. Save as model_v{n+1}.pkl
      6. Update self.model_version
    
    Returns: True if successful, False on error
    """
```

---

### 4. Honeypot Module (`honeypot.py`)

**Purpose:** Simulates a compromised Linux system with fake dashboard and terminal emulator

**Session Management:**

#### Session Lifecycle

```
1. User redirected to /portal/dashboard (honeypot token)
   ↓
2. get_or_create_session() called:
   - IP address captured
   - Session created in HoneypotSession table
   - Email alert sent (optional)
   ↓
3. User interacts with fake system:
   - browse_filesystem()
   - browse_process_list()
   - execute_command()
   - system_info()
   ↓
4. Commands logged in JSON array:
   {
     "timestamp": "2024-02-22T15:30:45.123Z",
     "type": "command",
     "command": "ls -la",
     "response": "...",
     "details": {...}
   }
   ↓
5. User logs out:
   - session.is_active = False
   - session.end_time = now()
   - Generate & email session report
   - Save to real_sessions/ for training
```

#### Terminal Emulator Architecture

**File System State Management** (`terminal_emulator/state_manager.py`):

```python
def load_state(state_name: str) -> Dict:
    """
    Load persistent filesystem state from state_history/
    
    Files:
      - filesystem.json: Directory listings and file contents
      - test_*.json: Test-specific states
    
    Structure:
      {
        "/": {
          "dirs": ["home", "usr", "etc", "var", "opt"],
          "files": {"passwd": "content...", "hostname": "..."}
        },
        "/home/user": {
          "dirs": ["Desktop", "Documents"],
          "files": {"bashrc": "..."}
        }
      }
    """
```

**Command Filtering & Processing** (`terminal_emulator/command_filter.py`):

```python
def should_use_llm(command: str) -> Tuple[bool, str]:
    """
    Determine if command needs LLM processing or is hardcoded.
    
    Returns: (allowed, reason)
    
    Hardcoded Commands (no LLM):
      help, ls, cat, whoami, pwd, clear, exit, cd, mkdir, rm, echo, 
      uname, ps, netstat
    
    Blocked Patterns:
      - rm -rf /
      - shutdown/reboot commands
      - Destructive filesystem operations (mkfs, dd)
      - Fork bomb: :(){ :|: &};
    
    Validation:
      - max_length: 200 characters
      - No control characters except \n, \r, \t
    """
```

**LLM-Based Responses:**

For allowed commands, the system integrates with Groq API to generate realistic command output:

```python
def get_command_response(command: str) -> str:
    """
    Call Groq LLM to simulate realistic Linux command output.
    
    Prompt engineering:
      "Simulate realistic output for this Linux command. 
       Keep response under 2000 characters. 
       Return only the output, no explanations."
    
    Post-processing:
      1. Remove markdown code fences
      2. Remove ANSI escape codes
      3. Normalize line endings
      4. Remove consecutive duplicates
      5. Remove fake bash error lines
      6. Cap at 20 lines
    """
```

#### Honeypot Endpoints

**GET `/portal/dashboard`** - Main honeypot interface
- Returns HTML with fake system dashboard
- Loads current filesystem state
- Sets up terminal emulator

**POST `/portal/execute`** - Execute terminal command
```json
{
  "session_id": "abc123",
  "command": "ls -la /home"
}
→
{
  "output": "total 24\ndrwxr-xr-x ...",
  "timestamp": "2024-02-22T15:30:45.123Z"
}
```

**POST `/portal/browse`** - List directory contents
```json
{
  "session_id": "abc123",
  "path": "/home/user"
}
→
{
  "directories": ["Desktop", "Documents"],
  "files": [{"name": "bashrc", "size": 1234}]
}
```

**POST `/portal/process-list`** - Fake process listing
- Returns simulated Linux processes
- Rotates based on time/commands executed

**POST `/portal/system-info`** - Fake system information
- Hostname, uptime, CPU, memory
- Consistent per session

**POST `/portal/logout`** - Session termination
```python
def end_session(session_id: str):
    """
    1. Mark session inactive
    2. Set end_time
    3. Trigger report generation (async)
    4. Send email with findings
    5. Save to real_sessions/ for profiler
    """
```

---

### 5. Attacker Profiler (Multi-Step ML Pipeline)

**Purpose:** Analyze attack session commands to classify attacker intent and skill level

**Architecture Overview:**

```
STEP 1: Playbook Indexing
    ↓
STEP 2: Synthetic Data Generation
    ↓
STEP 3: Feature Aggregation
    ↓
STEP 4: Model Training
    ↓
STEP 5: Inference on Real Sessions
```

#### Step 1: Playbook Indexing (`step1_playbook.py`)

**Data Sources:**
- `gtfobins.json` - GTFOBins command database
- `atomic-red-team/` - MITRE ATT&CK framework tactics
- `commands.json` - Custom attack command corpus

**Processing:**
```python
def build_playbook_index() -> Dict:
    """
    Creates comprehensive playbook database.
    
    Returns:
    {
        "entries": [
            {
                "command": "cat /etc/passwd | grep root",
                "intent": "Reconnaissance",
                "tactic": "T1087 - Account Discovery",
                "technique": "MITRE ATT&CK ID",
                "description": "Extract privileged user info"
            },
            ... (100+ entries per category)
        ],
        "binary_intent_map": {
            "cat": "Reconnaissance",
            "curl": "C2 Communication",
            "nc": "Persistence",
            "sudo": "Privilege Escalation",
            ...
        },
        "binary_complexity_map": {
            "cat": 1.0,       # Simple file read
            "curl": 2.5,      # Network + parsing
            "nc": 3.0,        # Reverse shell
            "gcc": 3.5,       # Compilation
            ...
        }
    }
    """
```

**Intent Categories:**
1. **Reconnaissance** - Information gathering (whoami, cat /etc/passwd)
2. **Privilege Escalation** - Elevation attempts (sudo, chmod, setcap)
3. **Persistence** - Long-term access (cron jobs, backdoors, SSH keys)
4. **Data Exfiltration** - Data theft (scp, curl to attacker, compression)
5. **RCE (Remote Code Execution)** - Command execution (curl | bash, wget | sh)
6. **ToolDeployment** - Malware/tool installation (wget, curl, git clone)

#### Step 2: Synthetic Data Generation (`step2_generate.py`)

**Purpose:** Create diverse training samples when real attack data is limited

**Generation Process:**

```python
def generate_synthetic_sessions(
    playbook_index: Dict,
    num_sessions: int = 100,
    seed: int = 42,
    min_cmds: int = 3,
    max_cmds: int = 12
) -> List[Dict]:
    """
    Creates synthetic attacker sessions for training.
    
    For each session:
    1. Randomly select intent (e.g., "Persistence")
    2. Generate 3-12 commands matching that intent
    3. Apply noise transformations (20% chance each):
       - Extra spaces: "ls -la" → "ls  -la"
       - Pipe to base64: "cat file" → "cat file | base64"
       - Command chaining: "pwd" → "pwd && echo done"
       - Semicolon separation: "ls; echo ok"
    4. Compute skill level from command complexity
    5. Return formatted session
    """
```

**Skill Level Computation:**

```python
def _compute_skill(commands: List[str], playbook_index: Dict) -> str:
    """
    Determines attacker sophistication from command patterns.
    
    Scoring:
      - complexity_score: Sum of binary complexity values
      - chain_rate: Fraction of commands with pipes/semicolons/&&
    
    average_complexity = total_complexity / num_commands
    chaining_rate = num_chained_commands / num_commands
    skill_score = average_complexity + chaining_rate
    
    Thresholds:
      - < 2.2:  "novice"  (basic, single commands)
      - 2.2-3.4: "intermediate" (simple chaining, some obfuscation)
      - > 3.4:  "advanced"  (complex pipelines, evasion techniques)
    """
```

**Output Format:**
```json
{
  "session_id": "uuid",
  "intent": "Persistence",
  "skill": "intermediate",
  "created_at": "2024-02-22T15:30:45Z",
  "commands": [
    {"command": "cat /etc/passwd", "response": ""},
    {"command": "ls -la ~/.ssh", "response": ""},
    {"command": "echo 'malicious' >> ~/.bashrc", "response": ""}
  ]
}
```

#### Step 3: Feature Aggregation (`step3_aggregate.py`)

**Purpose:** Convert command sequences into numerical feature vectors

**Per-Command Feature Extraction:**

```python
def extract_command_features(command: str, playbook_index: Dict) -> Dict:
    """
    Extracts 10 features from a single command.
    
    1. length: len(command)
    2. entropy: Shannon entropy of character distribution
    3. special_chars: Count of non-alphanumeric chars
    4. keywords: Count of dangerous keywords (select, union, etc.)
    5. chain_semicolon: 1 if ';' present, 0 otherwise
    6. chain_pipe: 1 if '|' present, 0 otherwise
    7. chain_and: 1 if '&&' present, 0 otherwise
    8. binary: Primary command (ls, cat, curl, etc.)
    9. intent: Inferred from playbook (Reconnaissance, RCE, etc.)
    10. complexity: Lookup from playbook complexity map
    """
```

**Session-Level Aggregation:**

```python
def aggregate_session(session: Dict, playbook_index: Dict) -> Tuple[List[float], List[str]]:
    """
    Aggregates all commands in a session into feature vector.
    
    Process:
    1. Extract features for each command
    2. Aggregate statistics across all commands:
       - total_commands: Count
       - distinct_binaries: Unique primary commands
       - chain_rate: (total_chains / total_commands)
    3. Compute stats over all commands:
       - avg/max length
       - avg/max entropy
       - avg/max special_chars
       - avg/max complexity
    4. Count commands by intent category
    
    Final Feature Vector (19 features):
      [
        total_commands,
        distinct_binaries,
        chain_rate,
        avg_length, max_length,
        avg_entropy, max_entropy,
        avg_special_chars, max_special_chars,
        avg_complexity, max_complexity,
        intent_count_Reconnaissance,
        intent_count_RCE,
        intent_count_DataExfiltration,
        intent_count_Persistence,
        intent_count_ToolDeployment,
        intent_count_PrivilegeEscalation,
        intent_count_Unknown
      ]
    
    Example for reconnaissance session:
      [5, 3, 0.4, 18.2, 32, 4.1, 5.2, 2.8, 6, 1.5, 2.0, 5, 0, 0, 0, 0, 0, 0]
    """
```

**Feature Normalization:**
- Features maintain raw scale to preserve relative magnitudes
- Random Forest doesn't require normalization (tree-based model)
- Allows interpretability of feature importance

#### Step 4: Model Training (`step4_train.py`)

**Two-Model Ensemble Architecture:**

```python
def train_models(
    sessions: List[Dict],
    playbook_index: Dict,
    test_size: float = 0.2,
    seed: int = 42
) -> Tuple[str, Dict[str, float]]:
    """
    Trains dual Random Forest models.
    
    Model 1 - INTENT CLASSIFIER:
      Input: 19-dimensional feature vector
      Output: Classification (Reconnaissance, RCE, Persistence, etc.)
      Trees: 200 decision trees
      Task: Predicts attacker's primary goal
    
    Model 2 - SKILL CLASSIFIER:
      Input: Same 19-dimensional feature vector
      Output: Skill level (novice, intermediate, advanced)
      Trees: 200 decision trees
      Task: Predicts sophistication level
    
    Training Process:
    1. Split data: 80% train, 20% test
    2. Stratified split (maintains class distribution)
    3. Fit both models on training data
    4. Evaluate on test set
    5. Compute accuracy metrics
    6. Bundle models + feature metadata
    7. Serialize to pickle file: model_store/session_model_v{N}.pkl
    """
```

**Random Forest Configuration:**

```
n_estimators: 200      # Number of trees in forest
max_depth: None        # Full tree growth (unlimited depth)
min_samples_split: 2   # Minimum samples to split node
min_samples_leaf: 1    # Minimum samples at leaf
random_state: 42       # Reproducible results
n_jobs: -1             # Parallel processing
criterion: "gini"      # Gini impurity for splits
```

**Why Random Forest for Attacker Profiling:**

1. **Non-linear boundaries** - Attack intent not linearly separable
2. **Feature importance** - Can extract which features matter most
3. **Ensemble robustness** - Multiple trees reduce overfitting
4. **Multi-class capable** - Handles 7+ intent categories
5. **Fast inference** - Millisecond predictions
6. **Interpretable** - Tree splits correspond to command patterns

**Model Evaluation Metrics:**

```
Accuracy = (Correct Predictions) / (Total Predictions)

Example Output:
  intent_accuracy: 0.87    (87% correctly classify intent)
  skill_accuracy: 0.92     (92% correctly classify skill)
```

#### Step 5: Inference (`step5_infer.py`)

**AttackerProfiler Class:**

```python
class AttackerProfiler:
    def analyze_session(self, commands: List[Union[str, Dict]]) -> Dict:
        """
        Profiles an attacker based on their command sequence.
        
        Input:
          commands: [
            {"command": "cat /etc/passwd", "response": "..."},
            {"command": "ls -la /root", "response": "..."},
            ...
          ]
        
        Process:
        1. Normalize commands to standard format
        2. Aggregate session into 19-feature vector
        3. intent_model.predict(features) → intent class
        4. skill_model.predict(features) → skill class
        5. Extract confidence from predict_proba()
        6. Combine intent + skill confidence
        
        Output:
        {
            "intent": "Reconnaissance",
            "skill": "intermediate",
            "confidence": 0.872,           # Overall confidence
            "intent_confidence": 0.95,     # Intent prediction confidence
            "skill_confidence": 0.79       # Skill prediction confidence
        }
        """
```

**Confidence Calculation:**

```python
def _predict_confidence(model, features: List[float]) -> float:
    """
    Extracts prediction confidence from Random Forest.
    
    Method: Use predict_proba() to get class probabilities
    
    Random Forest predict_proba:
      - Returns probability for each class
      - Array shape: (1, num_classes)
      - Probabilities sum to 1.0
    
    Confidence = max(probabilities)
      - E.g., [0.92, 0.05, 0.03] → confidence = 0.92
    
    Range: 0.0 - 1.0 (higher = more confident)
    Typical: 0.70+ indicates reliable classification
    """
```

---

### 6. Session Report Generator (`reportGen/session_report_generator.py`)

**Purpose:** Generate comprehensive reports when attacker logs out

**Report Generation Pipeline:**

```python
def generate_session_report(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Orchestrates report generation from raw session data.
    
    Process:
    1. get_session_data()
       - Query database for HoneypotSession
       - Extract JSON commands array
       - Extract HTTP headers
    
    2. calculate_connection_duration()
       - Subtract start_time from end_time
       - Format as "1h 23m 45s"
    
    3. extract_browser_fingerprint()
       - Parse user agent string
       - Extract browser (Chrome/Firefox/Safari/Edge)
       - Extract OS (Windows/macOS/Linux/Android)
       - Extract HTTP header details
    
    4. format_command_history()
       - Convert JSON commands to readable text
       - Include timestamps and responses
       - Truncate long responses (500 chars max)
    
    5. get_attacker_profile()
       - Call AttackerProfiler.analyze_session()
       - Returns: intent, skill, confidence scores
    
    Output: Complete report dictionary
    """
```

**Report Data Structure:**

```json
{
  "session_id": "abc123-def456",
  "attacker_ip": "192.168.1.100",
  "session_start": "2024-02-22T15:30:00Z",
  "session_end": "2024-02-22T16:45:30Z",
  "connection_duration": "1h 15m 30s",
  "command_count": 27,
  "browser_fingerprint": {
    "browser": "Chrome",
    "os": "Linux",
    "user_agent": "Mozilla/5.0...",
    "accept_language": "en-US,en;q=0.9",
    "accept_encoding": "gzip, deflate, br",
    "sec_fetch_dest": "document",
    "sec_fetch_mode": "navigate"
  },
  "command_history": "--- Command 1 ---\nTimestamp: 2024-02-22T15:30:15Z\nCommand: cat /etc/passwd\nResponse: root:x:0:0...",
  "attacker_profile": {
    "intent": "Persistence",
    "skill": "intermediate",
    "confidence": 0.87,
    "intent_confidence": 0.92,
    "skill_confidence": 0.82
  }
}
```

---

### 7. Email Service (`email_service.py`, `email_templates_report.py`)

**Purpose:** Send alerts and comprehensive session reports

**Email Types:**

#### 1. Honeypot Session Alert (Real-time)

**Triggered:** When attacker enters honeypot environment

**Content:**
- New honeypot session detected
- Attacker IP address
- Browser information
- Timestamp
- User agent details

#### 2. Session Completion Report (Post-analysis)

**Triggered:** When attacker logs out

**Content:**
- Complete session metadata
- Command history (all 27+ commands)
- Browser fingerprinting details
- AI-generated attacker profile:
  - Intent classification (with confidence %)
  - Skill level (with confidence %)
  - Sophistication indicators
- Connection duration
- Attack vectors used

**Template Structure (HTML + Plain Text):**

```python
def get_session_report_email_template(report: Dict) -> tuple[str, str, str]:
    """
    Returns: (subject, html_body, text_body)
    
    Subject: "Session Report: Attacker 192.168.1.100 - 1h 15m session"
    
    HTML Features:
    - Professional gradient header
    - Color-coded sections
    - Responsive design
    - Metrics highlighted in colored boxes
    - Code blocks for commands
    - Confidence percentages
    
    Plain Text Fallback:
    - Readable format for non-HTML clients
    - All data preserved
    - ASCII formatting
    """
```

**Email Configuration:**

```python
SMTP_SERVER: str      # e.g., "smtp.gmail.com"
SMTP_PORT: int        # 587 (TLS) or 465 (SSL)
SMTP_USERNAME: str    # Sender email
SMTP_PASSWORD: str    # App-specific password
RECIPIENT_EMAIL: str  # Analyst inbox
```

---

### 8. Admin Dashboard (`admin.py`)

**Purpose:** Provide analysts with attack monitoring and threat management tools

**Key Endpoints:**

#### `GET /admin/stats`
```json
{
  "total_logins": 45,
  "total_attacks": 12,
  "active_threats": 5,
  "attack_types": {
    "SQLi": 4,
    "XSS": 3,
    "Brute Force": 3,
    "Successful Login": 45
  },
  "recent_logs": [
    {
      "id": 123,
      "ip": "192.168.1.100",
      "type": "SQLi",
      "threat_score": 2.5,
      "timestamp": "2024-02-22T15:30:45Z"
    }
  ]
}
```

#### `GET /admin/active_threats`
```json
{
  "active_threats": [
    {
      "ip": "192.168.1.100",
      "score": 6.2,
      "risk": "High",
      "last_updated": "2024-02-22T16:45:30Z"
    }
  ]
}
```

#### `POST /admin/block_ip`
```
Input: {"ip": "192.168.1.100"}
Process:
  1. Add to BlockedIP table
  2. All future attempts from IP: 403 Forbidden
  3. Force to honeypot (if already logged in)
Output: {"message": "IP blocked successfully"}
```

#### `DELETE /admin/threat/{ip}`
```
Remove threat score entry for specific IP
Allows legitimate user recovery if mistakenly flagged
```

---

## Technical Methodologies

### Hybrid Detection Approach

The system combines two independent detection mechanisms:

**1. Rule-Based Detection (Signature Matching)**
- Regular expression patterns for known attack signatures
- Fast (microsecond-level matching)
- Deterministic results
- Effective against established attack patterns

**2. Machine Learning Detection (Anomaly Scoring)**
- Feature extraction from payload
- Random Forest probabilistic classification
- Adaptive to unknown attacks
- Confidence-based thresholding

**Decision Logic:**
```
IF (regex_match_found) OR (ml_score > 0.7) THEN
    attack_detected = True
    score = max(regex_score, ml_score)
ELSE
    attack_detected = False
```

This "OR" logic (Defense in Depth) means an attack is caught by either method:
- Known attacks caught by regex patterns
- Novel attacks caught by ML model
- Reduces false negatives

### Three-Strike Threat Escalation

**Mechanism:** Progressive punishment for failed login attempts

```
Attempt 1: Invalid credentials
  Action: Log attempt, don't update threat score
  Status: User sees "Invalid credentials" error
  
Attempt 2: Invalid credentials
  Action: Log attempt, don't update threat score
  Status: User sees "Invalid credentials" error
  
Attempt 3: Invalid credentials
  Action: Log as "Brute Force", add 3.0 to threat score
  Status: User logged to honeypot (if score >= 3.0)
```

**Rationale:**
- Allows legitimate users 2 password retries
- 3rd failure indicates systematic attack (brute force)
- Incremental escalation reduces false positives
- Failed login count resets on successful login

### Shannon Entropy Feature

Entropy measures randomness/disorder in data:

```
Formula: H = -Σ(p_x * log₂(p_x))

Interpretation:
  - Entropy = 0: Single repeated character ("aaaa")
  - Entropy = 1-3: Normal text ("hello")
  - Entropy = 3.5-4.5: Natural language (English text)
  - Entropy = 5-6: Encoded/compressed ("YWJjZGVm" - base64)
  - Entropy = 7-8: Random/encrypted data

Attack Detection:
  - Encoded payloads have >5.0 entropy (obfuscation)
  - Legitimate usernames have 2-4 entropy
  - Feature helps ML model detect obfuscated SQLi/XSS
```

### Feature Aggregation in Profiler

The profiler uses a sophisticated **sequence aggregation** technique:

```
Per-Session Process:

1. Extract 10 features from each command
   cmd1: [length, entropy, special_chars, keywords, chain_x3, binary, intent, complexity]
   cmd2: [...]
   cmd3: [...]
   ... (up to 12 commands)

2. Aggregate statistics across ALL commands:
   
   Command Count Metrics:
   - total_commands = 6
   - distinct_binaries = 3 (cat, grep, curl)
   - chain_rate = 2/6 = 0.33 (33% use pipes/semicolons)
   
   Length Statistics (aggregated):
   - Commands: [12, 18, 15, 22, 11, 16]
   - avg_length = 15.7
   - max_length = 22
   
   Entropy Statistics (aggregated):
   - avg_entropy = 3.8
   - max_entropy = 5.2 (encoded payload detected)
   
   Special Character Statistics:
   - avg_special_chars = 2.1
   - max_special_chars = 5
   
   Complexity Statistics:
   - avg_complexity = 1.8
   - max_complexity = 3.0
   
   Intent Distribution (histogram):
   - Reconnaissance: 3 commands
   - Persistence: 2 commands
   - RCE: 1 command

3. Final Feature Vector (19 dimensions):
   [6, 3, 0.33, 15.7, 22, 3.8, 5.2, 2.1, 5, 1.8, 3.0, 3, 0, 1, 2, 0, 0, 0]
   
   Why aggregation helps:
   - Captures session-level patterns (not individual commands)
   - Handles variable command counts (3-12 commands)
   - Intent distribution reveals attacker goals
   - High max values indicate obfuscation/evasion
   - Chaining rate shows sophistication
```

### Skill Level Computation

Combines multiple signals to rank attacker sophistication:

```
Inputs:
  1. Command Complexity (from playbook)
     - "ls" = 1.0 (basic)
     - "curl" = 2.5 (network + parsing)
     - "gcc" = 3.5 (compilation/advanced)
  
  2. Chaining Patterns (pipes, semicolons, &&)
     - Single commands = less sophisticated
     - Complex chains = more sophisticated
  
Calculation:
  complexity_sum = 1.0 + 3.5 + 2.5 + 1.0 = 8.0
  complexity_avg = 8.0 / 4 = 2.0
  
  chains = 2 (out of 4 commands)
  chain_rate = 2/4 = 0.5
  
  skill_score = complexity_avg + chain_rate
              = 2.0 + 0.5 = 2.5
  
Thresholds:
  skill_score < 2.2  → "novice"      (simple commands, no chaining)
  2.2 ≤ score < 3.4  → "intermediate" (moderate complexity, some chains)
  score ≥ 3.4        → "advanced"    (complex chains, evasion techniques)
```

---

## Data Flow & Processing

### Complete Attack Scenario Flow

```
1. ATTACKER ATTEMPTS LOGIN
   ├─ POST /auth/login (username, password)
   ├─ IP captured from request headers
   └─ HTTP headers stored for fingerprinting

2. THREAT DETECTION PIPELINE
   ├─ Query BlockedIP table
   │  └─ If match: Return 403 Forbidden
   │
   ├─ AI Engine Analysis
   │  ├─ Extract features from username
   │  │  [length, entropy, special_chars, keywords]
   │  │
   │  ├─ Regex pattern matching
   │  │  └─ Check 7+ SQLi patterns
   │  │  └─ Check 6+ XSS patterns
   │  │  └─ Check 6+ Command patterns
   │  │
   │  └─ ML Model Classification
   │     ├─ Feed features to Random Forest
   │     ├─ Get prediction (0=safe, 1=malicious)
   │     └─ Get confidence score (0.0-1.0)
   │
   └─ Decision: Threat Score Calculation
      ├─ If regex match: threat += pattern_score
      └─ If ML.predict() == 1: threat += ML_confidence

3. DATABASE LOGGING
   ├─ Create AttackLog entry
   │  ├─ ip_address
   │  ├─ timestamp
   │  ├─ payload (username or full payload)
   │  ├─ attack_type (SQLi, XSS, etc.)
   │  ├─ threat_score
   │  ├─ user_agent
   │  └─ headers (JSON)
   │
   └─ Update ThreatScore entry
      ├─ Accumulate score: score += new_threat
      ├─ Update last_updated timestamp
      └─ Query should_redirect()

4. CREDENTIAL VALIDATION
   ├─ If malicious: Skip validation
   │
   ├─ If credentials invalid:
   │  ├─ Increment failed_login_count
   │  ├─ If count == 3: Mark as brute force, add 3.0 to score
   │  └─ If count < 3: Log but don't update score
   │
   └─ If credentials valid:
      ├─ Reset failed_login_count to 0
      ├─ Reset threat_score to 0.0
      └─ Return JWT for legitimate user dashboard

5. REDIRECTION DECISION
   ├─ IF (threat_score >= 3.0) OR (is_blocked) OR (is_malicious)
   │  └─ Redirect to honeypot
   │     ├─ Return fake JWT token
   │     ├─ Return redirect to /portal/dashboard
   │     └─ Honeypot endpoint handles session creation
   │
   └─ ELSE
      └─ Return legitimate JWT
         └─ Redirect to /static/welcome.html (real dashboard)

6. HONEYPOT SESSION CREATION (if redirected)
   ├─ get_or_create_session()
   ├─ Create HoneypotSession record
   │  ├─ session_id (UUID)
   │  ├─ ip_address
   │  ├─ start_time
   │  ├─ is_active = True
   │  ├─ commands = "[]"  (empty array)
   │  ├─ user_agent
   │  └─ headers (JSON string)
   │
   ├─ Send email alert to analyst
   │  └─ IP address, browser info, timestamp
   │
   └─ Return honeypot dashboard HTML
      └─ Frontend loads fake system interface

7. COMMAND EXECUTION & LOGGING
   ├─ User submits command via /portal/execute
   │
   ├─ Command Validation
   │  ├─ Check if hardcoded (help, ls, cat, etc.)
   │  │  └─ Return predefined response
   │  │
   │  ├─ Check for blocked patterns (rm -rf /)
   │  │  └─ Return error message
   │  │
   │  └─ If allowed: Send to Groq LLM for realistic output
   │     └─ LLM generates command output
   │
   ├─ Log command to session
   │  └─ Append to HoneypotSession.commands JSON array
   │     {
   │       "timestamp": "2024-02-22T15:30:45Z",
   │       "command": "cat /etc/passwd",
   │       "response": "root:x:0:0:root:..."
   │     }
   │
   └─ Return output to frontend
      └─ Terminal displays command + response

8. SESSION TERMINATION (logout)
   ├─ User clicks logout or session timeout
   │
   ├─ end_session()
   │  ├─ Mark is_active = False
   │  ├─ Set end_time = now()
   │  └─ Save to database
   │
   ├─ Report Generation (async)
   │  ├─ Retrieve complete session data
   │  ├─ Extract session duration
   │  ├─ Extract browser fingerprint
   │  ├─ Format command history
   │  ├─ Run AttackerProfiler on commands
   │  │  ├─ Aggregate features
   │  │  ├─ Classify intent (Reconnaissance, RCE, etc.)
   │  │  ├─ Classify skill (novice, intermediate, advanced)
   │  │  └─ Return confidence scores
   │  │
   │  └─ Build report dictionary
   │     ├─ Session metadata
   │     ├─ Connection duration
   │     ├─ Browser fingerprint
   │     ├─ Command history
   │     └─ Attacker profile
   │
   ├─ Email Report
   │  ├─ Format report as HTML + plain text
   │  ├─ Include all metrics and profiles
   │  ├─ Send to analyst inbox (SMTP)
   │  └─ Log email sent status
   │
   ├─ Save for Training
   │  └─ Write session JSON to real_sessions/
   │     ├─ Auto-label via AttackerProfiler
   │     ├─ Add to labeled pool
   │     └─ Trigger retraining if 10+ labeled sessions
   │
   └─ Return logout response to frontend

9. CONTINUOUS LEARNING
   ├─ Monitor labeled session count
   ├─ If count % 10 == 0:
   │  ├─ Trigger incremental retraining
   │  ├─ Combine real sessions with synthetic data
   │  ├─ Train new Random Forest models
   │  ├─ Save as session_model_v{N}.pkl
   │  └─ Update profiler's loaded model
   │
   └─ Log training event
      ├─ Timestamp
      ├─ Metrics (intent accuracy, skill accuracy)
      ├─ Model path
      └─ Data composition
```

---

## Machine Learning Implementation

### Model Architecture Summary

| Component | Type | Algorithm | Input | Output |
|-----------|------|-----------|-------|--------|
| **Login Threat Detection** | Binary Classification | Random Forest (10 trees) | [length, entropy, special_chars, keywords] | 0/1 + confidence |
| **Intent Profiler** | Multi-class Classification | Random Forest (200 trees) | [19 aggregated features] | Intent (7 classes) + confidence |
| **Skill Profiler** | Multi-class Classification | Random Forest (200 trees) | [19 aggregated features] | Skill (3 classes) + confidence |

### Training Data

**AI Engine (Login Detection):**
- Malicious samples: 50+ SQLi, XSS, command injection attempts
- Benign samples: 50+ normal usernames
- Features: Extracted from payload
- Labels: 0 (safe) or 1 (malicious)

**Attacker Profiler (Session Analysis):**
- Synthetic training data: 100+ generated sessions
- Real training data: Accumulated from actual attacks
- Features: 19-dimensional vector from command aggregation
- Intent labels: 7 categories (Reconnaissance, RCE, etc.)
- Skill labels: 3 levels (novice, intermediate, advanced)

### Model Persistence & Versioning

**AI Engine Models:**
```
models/
├── model_v1.pkl      # Initial baseline
├── model_v2.pkl      # After 100 attacks
├── model_v3.pkl      # After 500 attacks
└── model_v4.pkl      # Current production
```

**Attacker Profiler Models:**
```
attacker_profiler/model_store/
├── session_model_v1.pkl    # Initial
├── session_model_v2.pkl    # After 10 real sessions
└── session_model_v3.pkl    # Current
```

**Version Management:**
```python
def _get_latest_model_version(self) -> int:
    """
    Scans models directory for highest version.
    
    Logic:
      1. List all model_v*.pkl files
      2. Extract version numbers
      3. Return max version
    
    Prevents overwrites & maintains history
    """
```

---

## Security Mechanisms

### 1. IP-Based Blocking

**Hard Blocking:**
- IPs in `BlockedIP` table receive 403 Forbidden
- Applies to ALL endpoints
- Admin-controlled via `/admin/block_ip`

**Soft Blocking (Honeypot Redirection):**
- IPs with threat score >= 3.0 see fake dashboard
- Transparent to attacker (no error indication)
- Allows behavior analysis

### 2. Input Validation

**Login Endpoint:**
- Username analyzed for attacks
- Password excluded (to avoid false positives on legitimate special characters)
- Injection patterns checked against regex corpus

**Terminal Commands:**
- Max length: 200 characters
- No control characters (except newline, tab)
- Hardcoded commands bypass LLM (deterministic)
- Dangerous patterns blocked (rm -rf /, shutdown, mkfs)

### 3. Credential Handling

**Password Storage:**
- Python code shows plaintext comparison (anti-pattern)
- **In production:** Should use bcrypt hashing via passlib
- Uses `passlib[bcrypt]` in requirements

**Authentication Tokens:**
- Real users: JWT tokens signed with secret
- Honeypot users: Fake JWT tokens (accepted but don't grant real access)
- Token used only for frontend routing, not API authentication

### 4. Data Protection

**Database:**
- SQLite (file-based, not network-exposed)
- Location: `honeypot-ai/database/honeypot.db`
- Access controlled by filesystem permissions

**Email Credentials:**
```python
SMTP_USERNAME = os.getenv("SMTP_USERNAME")    # From .env file
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")    # Encrypted in transit
```

**Sensitive Data in Logs:**
```python
# AttackLog stores:
log_payload = json.dumps({
    "username": username,        # Stored for analysis
    "password": password,         # Stored (should be redacted)
    "full_payload": payload if is_malicious else "HIDDEN"
})
```

---

## Frontend & User Interface

### User Interfaces

**1. Login Page** (`login.html`)
- Form with username & password fields
- Error messages for invalid credentials
- Styled with responsive CSS
- CSRF protection via form tokens

**2. Legitimate User Dashboard** (`welcome.html`)
- Real user dashboard (post-authentication)
- Shows basic system information
- Logout button

**3. Admin Dashboard** (`dashboard.html`)
- Real-time attack statistics
- Active threat list with IP addresses & threat scores
- Attack type breakdown
- Recent attack log table
- Features:
  - Block IP button
  - Clear logs button
  - Threat level indicators (color-coded)

**4. Attack Details** (`attack_details.html`)
- Detailed view of specific attack
- Payload display
- Timestamp & IP address
- Attack classification

**5. Honeypot Interface** (`honeypot_ui.html`)
- Simulates compromised Linux system
- File browser (shows fake filesystem)
- Terminal emulator (command input/output)
- Process list display
- System info display
- Logout button

**6. Session Details** (`honeypot_session_details.html`)
- Post-session analysis view
- Shows all commands executed
- Connection duration
- Browser fingerprint info
- Attacker profile (if available)

### Frontend JavaScript (`scripts.js`)

**Key Functions:**
- `login()` - Handle login form submission
- `executeCommand()` - Send command to backend
- `updateDashboard()` - Refresh admin stats
- `blockIP()` - Send block request
- `logout()` - Session termination

---

## Database Schema

### Core Tables

#### `users`
```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username VARCHAR UNIQUE INDEX,
  password_hash VARCHAR,
  role VARCHAR DEFAULT 'user'  -- 'user' or 'admin'
);
```

#### `attack_logs`
```sql
CREATE TABLE attack_logs (
  id INTEGER PRIMARY KEY,
  ip_address VARCHAR INDEX,
  timestamp DATETIME DEFAULT UTC,
  payload VARCHAR,  -- JSON or raw payload
  attack_type VARCHAR,  -- SQLi, XSS, CommandInjection, etc.
  threat_score FLOAT,
  user_agent VARCHAR,
  endpoint VARCHAR,
  method VARCHAR,
  headers VARCHAR  -- JSON string
);
```

#### `threat_scores`
```sql
CREATE TABLE threat_scores (
  id INTEGER PRIMARY KEY,
  ip_address VARCHAR UNIQUE INDEX,
  score FLOAT DEFAULT 0.0,  -- Accumulating score
  last_updated DATETIME,
  failed_login_count INTEGER DEFAULT 0
);
```

#### `blocked_ips`
```sql
CREATE TABLE blocked_ips (
  id INTEGER PRIMARY KEY,
  ip_address VARCHAR UNIQUE INDEX,
  reason VARCHAR,
  timestamp DATETIME DEFAULT UTC
);
```

#### `attack_signatures`
```sql
CREATE TABLE attack_signatures (
  id INTEGER PRIMARY KEY,
  pattern VARCHAR UNIQUE,  -- Regex pattern
  type VARCHAR,  -- SQLi, XSS, Cmd
  description VARCHAR
);
```

#### `honeypot_sessions`
```sql
CREATE TABLE honeypot_sessions (
  id INTEGER PRIMARY KEY,
  session_id VARCHAR UNIQUE INDEX,
  ip_address VARCHAR INDEX,
  start_time DATETIME,
  end_time DATETIME,
  is_active BOOLEAN DEFAULT True,
  commands VARCHAR,  -- JSON array of commands
  user_agent VARCHAR,
  headers VARCHAR  -- JSON string of initial HTTP headers
);
```

### Database Operations

**Initialization (`init_db()`):**
```python
def init_db():
    """
    Called on application startup.
    
    Process:
    1. Create all tables (if not exist)
    2. Seed default attack signatures
    3. Initialize AI model
    """
    Base.metadata.create_all(bind=engine)
```

**Seed Signatures:**
```python
def seed_signatures():
    """
    Populates attack_signatures table with default patterns.
    
    Patterns seeded:
    - 7 default signature patterns
    - Categories: SQLi, XSS, CommandInjection
    - Only inserts if pattern doesn't exist
    """
```

---

## API Endpoints

### Authentication Endpoints

**POST `/auth/login`**
```
Input:
  - username (Form)
  - password (Form)
  - request (HTTP request object)

Output:
  - status: 200 (successful) or 401 (failed)
  - token: JWT token
  - redirect: URL to redirect after login
  - message: Status message

Process: See "Complete Attack Scenario Flow" above
```

**POST `/auth/register`**
```
Input:
  - username (Form)
  - password (Form)

Output:
  - message: "User registered"

Security: Allows basic registration (no email verification)
```

### Honeypot Endpoints

**GET `/portal/dashboard`**
- Returns honeypot UI HTML
- Initiates session creation

**POST `/portal/execute`**
```
{
  "session_id": "abc123",
  "command": "ls -la /home"
}
```

**POST `/portal/browse`**
```
{
  "session_id": "abc123",
  "path": "/home/user"
}
```

**POST `/portal/logout`**
- Triggers session termination
- Generates & sends report
- Saves for training

### Admin Endpoints

**GET `/admin/stats`**
- Total logins, attacks, active threats
- Attack type breakdown
- Recent logs

**GET `/admin/active_threats`**
- List of IPs with threat scores > 0
- Risk levels

**POST `/admin/block_ip`**
```json
{"ip": "192.168.1.100"}
```

**DELETE `/admin/threat/{ip}`**
- Remove threat score entry

**POST `/admin/clear_logs`**
- Delete all attack logs and threat scores
- Reset database

---

## Email & Reporting System

### Email Service Configuration

**Environment Variables:**
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=honeypot.alerts@gmail.com
SMTP_PASSWORD=<app-specific-password>
RECIPIENT_EMAIL=analyst@company.com
```

**Connection:**
- TLS encryption (port 587)
- Uses `smtplib` for SMTP communication
- Async sending (non-blocking)

### Report Email Template

**Subject:** `"Session Report: Attacker 192.168.1.100 - 1h 15m session"`

**HTML Components:**
1. Header with gradient background
2. Session metadata section
3. Browser fingerprint details
4. Command history (code block)
5. Attacker profile section (with confidence percentages)
6. Footer with timestamp

**Report Metrics Included:**
- Attacker IP address
- Session duration (formatted)
- Connection start/end times
- Browser & OS detection
- User agent string
- HTTP headers analysis
- Full command execution history
- AI-generated skill level
- AI-generated intent classification
- Confidence scores (0-100%)

---

## Testing & Deployment

### Test Modules

**`test_auth_flow.py`** - Authentication testing
- Valid credentials
- Invalid credentials
- Malicious payloads
- Threat score updates

**`test_failed_login_behavior.py`** - Three-strike system
- 1st failed login (no score change)
- 2nd failed login (no score change)
- 3rd failed login (score += 3.0)
- Successful login (score reset)

**`test_model_logging.py`** - AI model tracking
- Model version incrementation
- Model persistence
- Training logging

**`test_retraining.py`** - Model retraining
- Data collection
- Feature extraction
- Model training
- Evaluation metrics

**`test_all_modes.py`** - Complete integration
- All components together
- End-to-end flows

### Deployment Checklist

**Prerequisites:**
- Python 3.11+
- Virtual environment
- Dependencies installed (`pip install -r requirements.txt`)

**Configuration (.env file):**
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
RECIPIENT_EMAIL=analyst@company.com
GROQ_API_KEY=your-groq-api-key
RETRAIN_MODE=skip|recent|all
```

**Startup:**
```bash
cd honeypot-ai
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

**Verification:**
- Visit `http://localhost:8000/static/login.html`
- Test login with known credentials
- Check admin dashboard at `http://localhost:8000/static/dashboard.html`
- Verify email alerts sent

### Production Considerations

**Security Hardening:**
- Use environment variables for all secrets
- Enable HTTPS (SSL/TLS certificates)
- Use strong JWT secrets
- Implement rate limiting on login endpoint
- Add CORS restrictions to known domains
- Use bcrypt for password hashing (not plaintext comparison)

**Performance:**
- Database indexing on ip_address, session_id, timestamp
- Model inference caching for repeated sessions
- Async email sending (non-blocking)
- Connection pooling for database

**Monitoring:**
- Log all attacks to file + database
- Monitor model accuracy over time
- Track false positive rates
- Alert on unusual patterns

**Backup & Recovery:**
- Regular SQLite database backups
- Version control for models
- Disaster recovery plan for email service

---

## Low-Level Implementation Details

### Session JSON Structure

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "ip_address": "192.168.1.100",
  "start_time": "2024-02-22T15:30:00Z",
  "end_time": "2024-02-22T16:45:30Z",
  "is_active": false,
  "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
  "headers": {
    "host": "localhost:8000",
    "user-agent": "Mozilla/5.0...",
    "accept": "text/html,application/xhtml+xml",
    "accept-language": "en-US,en;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "connection": "keep-alive",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none"
  },
  "commands": [
    {
      "timestamp": "2024-02-22T15:30:15.123Z",
      "command": "whoami",
      "response": "www-data"
    },
    {
      "timestamp": "2024-02-22T15:30:45.456Z",
      "command": "cat /etc/passwd",
      "response": "root:x:0:0:root:/root:/bin/bash\nwww-data:x:33:33:www-data:..."
    }
  ]
}
```

### Feature Vector Example

```python
# Single command features
"cat /etc/passwd | grep root"
features = {
    "length": 28,                    # len(command)
    "entropy": 4.2,                  # Shannon entropy
    "special_chars": 4,              # Count of non-alphanumeric
    "keywords": 1,                   # Count of dangerous keywords (grep)
    "chain_semicolon": 0,            # Has ';'?
    "chain_pipe": 1,                 # Has '|'?
    "chain_and": 0,                  # Has '&&'?
    "binary": "cat",                 # Primary command
    "intent": "Reconnaissance",      # From playbook
    "complexity": 1.5                # From playbook
}

# Session aggregation (6 commands)
session_vector = [
    6,        # total_commands
    3,        # distinct_binaries (cat, grep, curl)
    0.33,     # chain_rate (2 out of 6 use pipes)
    18.2,     # avg_length
    28,       # max_length
    4.1,      # avg_entropy
    5.2,      # max_entropy
    2.8,      # avg_special_chars
    6,        # max_special_chars
    1.8,      # avg_complexity
    3.0,      # max_complexity
    3,        # intent_count_Reconnaissance
    0,        # intent_count_RCE
    0,        # intent_count_DataExfiltration
    2,        # intent_count_Persistence
    1,        # intent_count_ToolDeployment
    0,        # intent_count_PrivilegeEscalation
    0         # intent_count_Unknown
]

# ML Model Prediction
random_forest.predict([session_vector])
→ ["Reconnaissance"]  # Primary intent

random_forest.predict_proba([session_vector])
→ [[0.92, 0.05, 0.02, 0.01, 0.0, 0.0, 0.0]]
→ confidence = 0.92 (92%)
```

### Entropy Calculation Example

```python
def calculate_entropy(text: str) -> float:
    """Calculate Shannon entropy of text."""
    if not text:
        return 0
    
    entropy = 0
    text_length = len(text)
    
    # For each possible byte value (0-255)
    for byte_value in range(256):
        # Count occurrences of this byte
        char = chr(byte_value)
        count = text.count(char)
        
        # Calculate probability
        p = count / text_length
        
        # Add to entropy sum
        if p > 0:
            entropy += -p * math.log2(p)
    
    return entropy

# Examples
calculate_entropy("aaaaaaa") → 0.0 (single char)
calculate_entropy("hello") → 2.1 (normal text)
calculate_entropy("YWJjZGVm") → 5.8 (base64 encoded)
calculate_entropy("Ā"ü©ðÿ") → 7.9 (random bytes)
```

### Threat Score Accumulation

```python
# Initial state
threat_score = 0.0

# Attack 1: SQLi payload detected
threat_score += 1.2  # ML confidence + regex match
# threat_score = 1.2

# Attack 2: XSS payload detected
threat_score += 0.8
# threat_score = 2.0  (Medium risk)

# Attack 3: Failed login (2nd attempt)
# threat_score unchanged
# threat_score = 2.0

# Attack 4: Failed login (3rd attempt - brute force)
threat_score += 3.0  # Fixed brute force penalty
# threat_score = 5.0  (High risk)

# Decision: threat_score >= 5.0 → Redirect to honeypot
# User sees fake dashboard, analyst notified
```

---

## Copyright & Attribution Considerations

This project integrates several publicly available knowledge bases:

### Integrated Data Sources

1. **GTFOBins** (`gtfobins.json`)
   - Public database of Unix/Linux binaries
   - Used for command complexity estimation
   - Attribution: GTFOBins contributors (Creative Commons)

2. **MITRE ATT&CK Framework** (`atomic-red-team/`)
   - Tactics, techniques, and procedures
   - Used for attack classification
   - Attribution: MITRE Corporation (Apache 2.0 License)

3. **Custom Command Corpus** (`commands.json`)
   - Commands generated from documented attack techniques
   - No proprietary payloads from real exploits
   - Derived from public security research

### Original Implementation

The following components are original implementations:

- **Honeypot architecture** - Custom deception system design
- **Three-strike threat scoring** - Original algorithm
- **Session aggregation features** - Novel feature engineering approach
- **Terminal emulator with LLM integration** - Original implementation
- **Email reporting system** - Custom report generation
- **Incremental training pipeline** - Original continuous learning system

### Potential IP Concerns

**Areas that should be reviewed for IP clearance:**

1. **ML Model Training Data**
   - Synthetic attack samples generated from public sources
   - Real attack data captured from honeypot (proprietary)
   - Consider: Who owns analysis of real attacks?

2. **Attack Signatures**
   - Regex patterns derived from OWASP/CWE databases
   - Standard attack vectors (public knowledge)
   - Custom patterns for detection (original)

3. **Playbook Data**
   - Derived from public sources (ATT&CK, GTFOBins)
   - Remixed and reorganized (transformative)

### Recommendations

1. **Open Source Compliance**
   - Add LICENSE file (e.g., MIT, Apache 2.0)
   - Document all dependencies in requirements.txt
   - Cite MITRE ATT&CK and GTFOBins in documentation

2. **Proprietary Components**
   - Keep ML training data separate from open source release
   - Document which models are trained on proprietary data
   - Use separate licensing for proprietary vs. public components

3. **Attribution**
   - Create ATTRIBUTION.md file listing:
     - GTFOBins (with license)
     - MITRE ATT&CK Framework (with license)
     - Atomic Red Team (with license)
     - scikit-learn, FastAPI, SQLAlchemy (with licenses)

---

## Conclusion

This Adaptive Honeypot System represents a sophisticated integration of:

- **Real-time threat detection** (hybrid rule + ML)
- **Deceptive defense mechanisms** (honeypot redirection)
- **Behavioral analysis** (multi-step ML profiler)
- **Continuous learning** (incremental model updates)
- **Comprehensive reporting** (automated incident analysis)

The system is production-ready with modular architecture, enabling:
- Scalable threat detection
- Detailed attacker profiling
- Automated incident reporting
- Continuous model improvement

All techniques are well-documented and derived from established security research methodologies.

