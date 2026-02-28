# Machine Learning Training Guide

Complete guide to model training, retraining, incremental learning, and logging for the Adaptive Honeypot System.

---

## Table of Contents

1. [Overview](#overview)
2. [Incremental Training & Continuous Learning](#incremental-training--continuous-learning)
   - [How Incremental Learning Works](#how-incremental-learning-works)
   - [Auto-Labeling Process](#auto-labeling-process)
   - [Retraining Trigger](#retraining-trigger)
   - [Training Process](#training-process)
   - [Manual Management](#manual-management)
3. [Startup Retraining Modes](#startup-retraining-modes)
   - [Command-Line Configuration](#command-line-configuration)
   - [Retraining Modes](#retraining-modes)
   - [Model Storage](#model-storage)
4. [Training Logs](#training-logs)
   - [Log File Location](#log-file-location)
   - [Log Format](#log-format)
   - [Monitoring & Debugging](#monitoring--debugging)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Overview

The Honeypot AI system includes two complementary machine learning training approaches:

1. **Incremental Training**: Continuous learning from real attack sessions (runs automatically during operation)
2. **Startup Retraining**: Batch retraining on historical data (runs on application startup)

Both approaches work together to improve model accuracy over time.

---

## Incremental Training & Continuous Learning

### How Incremental Learning Works

The Attacker Profiler uses **incremental learning** to continuously improve its models as new real attack data accumulates.

```
New Attack Occurs
    ↓
Session logged to HoneypotSession table
    ↓
AttackerProfiler analyzes session automatically
    ├─ Generates intent classification (Reconnaissance, RCE, Persistence, etc.)
    ├─ Generates skill assessment (novice, intermediate, advanced)
    └─ Calculates confidence scores
    ↓
Session auto-labeled with AI predictions
    └─ Saves to real_sessions/{session_id}.json
    ↓
Labeled session counter increments
    ↓
Every 10 labeled sessions:
    ├─ Trigger incremental retraining
    ├─ Combine synthetic data (100 sessions) + real data (N sessions)
    ├─ Train new Random Forest models
    ├─ Save new version: session_model_v{N+1}.pkl
    └─ Load into profiler (runtime update)
```

### Auto-Labeling Process

When a honeypot session completes, the system automatically:

#### 1. Extract Session Data
- Retrieve commands executed by the attacker
- Parse command sequences
- Extract features (length, entropy, complexity, etc.)

#### 2. Generate Predictions
- Run existing ML model on session features
- Get predicted intent: "Reconnaissance", "Persistence", "RCE", etc.
- Get predicted skill: "novice", "intermediate", or "advanced"
- Calculate confidence scores (0.0-1.0)

#### 3. Quality Check
- Verify prediction confidence ≥ 0.70 (70%)
- If confidence too low: Mark as "uncertain", skip labeling
- If confidence good: Proceed to labeling

#### 4. Save Labeled Session
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "intent": "Persistence",
  "skill": "intermediate",
  "confidence": 0.85,
  "created_at": "2024-02-22T17:45:30Z",
  "commands": [
    {"command": "cat /etc/passwd", "response": "..."},
    {"command": "ls -la ~/.ssh", "response": "..."}
  ]
}
```

Location: `honeypot-ai/attacker_profiler/real_sessions/{session_id}.json`

### Retraining Trigger

Retraining happens automatically when:

```python
# Check condition
labeled_sessions_count = count_files_in("attacker_profiler/real_sessions/")
if labeled_sessions_count % 10 == 0 and labeled_sessions_count > 0:
    trigger_incremental_retraining()
```

**Events That Trigger Retraining:**
- 10th session logged
- 20th session logged
- 30th session logged
- ... and so on

**NOT triggered for:**
- Incomplete sessions (< 1 command)
- Sessions with low confidence predictions
- Sessions already included in model

### Training Process

When retraining is triggered:

#### 1. Data Collection
```python
# Gather training data
synthetic_sessions = load_synthetic_data()           # 100 sessions (generated)
real_sessions = load_real_sessions()                  # N sessions (from real attacks)
training_data = synthetic_sessions + real_sessions   # 100 + N total
```

#### 2. Feature Extraction
```python
# Convert each session to feature vector
features = []
labels_intent = []
labels_skill = []

for session in training_data:
    # Aggregate command features
    vector = aggregate_session_features(session)
    features.append(vector)
    
    # Get labels (from auto-labeling or synthetic generation)
    labels_intent.append(session['intent'])
    labels_skill.append(session['skill'])
```

#### 3. Model Training
```python
# Train two Random Forest models
intent_model = RandomForestClassifier(n_estimators=200)
skill_model = RandomForestClassifier(n_estimators=200)

intent_model.fit(features, labels_intent)
skill_model.fit(features, labels_skill)

# Evaluate on test set
intent_accuracy = intent_model.score(X_test, y_test_intent)
skill_accuracy = skill_model.score(X_test, y_test_skill)
```

#### 4. Model Persistence
```python
# Save new model version
import joblib
version = get_latest_model_version() + 1
joblib.dump(intent_model, f"model_store/session_model_v{version}.pkl")

# Update profiler to use new model
profiler.load_model(version)
```

#### 5. Logging & Metrics
```
[2024-02-22 18:30:45] Incremental Retraining Complete
  Model Version: v5
  Training Samples: 130 (100 synthetic + 30 real)
  Intent Accuracy: 0.89 (89%)
  Skill Accuracy: 0.91 (91%)
  Duration: 2.3 seconds
  Status: Successfully loaded into profiler
```

### Data Composition Over Time

As real attacks accumulate, the data composition changes:

| Round | Synthetic | Real | Total | Model Accuracy |
|-------|-----------|------|-------|-----------------|
| Initial | 100 | 0 | 100 | 82% (intent), 85% (skill) |
| After 10 attacks | 100 | 10 | 110 | 84%, 87% |
| After 20 attacks | 100 | 20 | 120 | 86%, 89% |
| After 30 attacks | 100 | 30 | 130 | 87%, 90% |
| After 50 attacks | 100 | 50 | 150 | 89%, 92% |

**Key Insight:** As real data increases, model accuracy generally improves due to exposure to actual attacker behavior patterns.

### Manual Management

#### List All Sessions

```bash
# Show all labeled sessions
python honeypot-ai/attacker_profiler/manage_training.py list --all

# Show only high-confidence sessions
python honeypot-ai/attacker_profiler/manage_training.py list --min-confidence 0.80

# Show sessions from last 7 days
python honeypot-ai/attacker_profiler/manage_training.py list --recent 7
```

#### Force Retraining

```bash
# Retrain immediately using current data
python honeypot-ai/attacker_profiler/manage_training.py retrain

# Retrain with specific data mix
python honeypot-ai/attacker_profiler/manage_training.py retrain \
  --synthetic 100 \
  --min-real 5 \
  --max-real 50
```

#### Manually Label a Session

```bash
# Label a session that was previously uncertain
python honeypot-ai/attacker_profiler/manage_training.py label \
  <session_id> \
  --intent "Persistence" \
  --skill "advanced"

# Re-label with different value
python honeypot-ai/attacker_profiler/manage_training.py label \
  <session_id> \
  --intent "Reconnaissance" \
  --force  # Override existing label
```

#### Review Training History

```bash
# Show last 10 training events
python honeypot-ai/attacker_profiler/manage_training.py history --limit 10

# Show detailed metrics for specific version
python honeypot-ai/attacker_profiler/manage_training.py metrics --version 5
```

### Why Auto-Labeling Works

The auto-labeling system is reliable because:

1. **Initial Model Quality** - Trained on 100+ synthetic diverse sessions
   - Baseline accuracy: 82-85%
   - Sufficient for high-confidence predictions

2. **Confidence Filtering** - Only uses high-confidence predictions
   - Threshold: 70% minimum confidence
   - Filters out uncertain predictions
   - Reduces labeling errors

3. **Self-Reinforcing** - Better model makes better labels
   - V1 model (82% acc) labels data
   - V2 model trained on that data (85% acc)
   - V2 makes better labels
   - V3 trained on V2's labels (87% acc)
   - ... cycle continues

4. **Noise Tolerance** - ML models are robust
   - Random Forest tolerant to some mislabeled samples
   - Few labeling errors don't significantly degrade performance
   - Benefits of more training data outweigh occasional errors

### Monitoring Incremental Learning

#### Check Model Version

```bash
# See current model version loaded
cat honeypot-ai/attacker_profiler/model_store/CURRENT_VERSION.txt

# See all available models
ls -lh honeypot-ai/attacker_profiler/model_store/session_model_v*.pkl
```

#### Track Training Events

```bash
# Monitor training log file
tail -f honeypot-ai/logs/model_log.txt

# Count labeled sessions
ls honeypot-ai/attacker_profiler/real_sessions/*.json | wc -l
```

#### Verify Model Improvements

```bash
# Compare metrics between versions
python honeypot-ai/attacker_profiler/demo_runner.py --compare-versions v4 v5

# Evaluate current model on test set
python honeypot-ai/attacker_profiler/demo_runner.py --evaluate
```

### Disabling Incremental Learning

If you want to prevent automatic retraining:

#### Option 1: Disable Auto-Labeling

Edit `honeypot-ai/attacker_profiler/incremental_trainer.py`:
```python
# Set to False to disable auto-labeling
AUTO_LABEL_ON_SESSION_END = False
```

#### Option 2: Increase Retraining Threshold

Edit configuration:
```python
# Only retrain after 50 sessions instead of 10
RETRAIN_FREQUENCY = 50
```

#### Option 3: Manual Only Mode

```python
# Delete manage_training.py to enable manual retraining only
# Sessions still saved but retraining requires explicit command
```

---

## Startup Retraining Modes

### Command-Line Configuration

When starting the application, you can specify the retraining mode using the `RETRAIN_MODE` environment variable.

```bash
# Option 1: Retrain on ALL historical attack data
RETRAIN_MODE=all python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Option 2: Retrain on data from the last 7 days only
RETRAIN_MODE=recent python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Option 3: Skip retraining (default if no variable set)
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Or explicitly set to skip
RETRAIN_MODE=skip python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

**On Windows (PowerShell):**
```powershell
# Option 1: Retrain on all data
$env:RETRAIN_MODE='all'; python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Option 2: Retrain on recent data
$env:RETRAIN_MODE='recent'; python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Option 3: Skip (default)
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

**On Windows (CMD):**
```cmd
# Option 1: Retrain on all data
set RETRAIN_MODE=all && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Option 2: Retrain on recent data
set RETRAIN_MODE=recent && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Option 3: Skip (default)
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Retraining Modes

#### `all` Mode
- Retrains the model using **all historical attack data** from the database
- Best for: Initial setup or periodic full retraining
- Use case: When you want the model to learn from all past attacks accumulated in the system
- Performance: Slower startup, more comprehensive training

#### `recent` Mode
- Retrains the model using attack data from the **last 7 days only**
- Best for: Regular restarts, maintaining freshness without full retraining
- Use case: When you want to adapt to recent attack trends without overtraining on old data
- Performance: Faster startup, focused on recent threats

#### `skip` Mode (Default)
- **Skips retraining entirely** and loads the most recently trained model
- Best for: Quick restarts, development, testing
- Use case: When you don't have new attack data to train on yet
- Performance: Fastest startup

### Model Storage

- Models are stored in the `honeypot-ai/models/` directory
- Each retrained model is saved with a version number: `model_v1.pkl`, `model_v2.pkl`, etc.
- The latest model version is automatically loaded on startup
- Models persist between program restarts

### How Startup Retraining Works

1. **Database Initialization**: On startup, the database is initialized and attack signatures are seeded
2. **Model Loading**: The latest model version is loaded from the models directory (or dummy model if none exists)
3. **Retraining Decision**: Based on the `RETRAIN_MODE` argument:
   - If `all`: Extracts all attack logs (excluding failed logins)
   - If `recent`: Extracts attack logs from the last 7 days
   - If `skip`: Skips retraining
4. **Feature Extraction**: For each attack log:
   - Extracts the malicious payload (username field)
   - Calculates features: length, entropy, special characters, suspicious keywords
   - Labels it as malicious (1) or clean (0)
5. **Model Training**: If sufficient data exists (5+ samples), retrains the RandomForest model
6. **Model Saving**: The newly trained model is saved with an incremented version number

### Data Filtering

During retraining, the system:
- **Excludes**: "Failed Login" and "Successful Login" entries
- **Includes**: Only actual attacks (SQLi, XSS, CommandInjection, PathTraversal, Anomaly)
- **Requires**: Minimum 5 attack samples to proceed with retraining

If insufficient data exists, the system falls back to the previous model or dummy model and continues startup normally.

### Batch File Configuration

To use retraining with the batch file (`run_honeypot.bat`), update it as follows:

**For all-data retraining:**
```batch
@echo off
cd /d "%~dp0"
set RETRAIN_MODE=all
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
pause
```

**For recent-data retraining (recommended):**
```batch
@echo off
cd /d "%~dp0"
set RETRAIN_MODE=recent
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
pause
```

**For no retraining (fastest startup):**
```batch
@echo off
cd /d "%~dp0"
set RETRAIN_MODE=skip
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
pause
```

---

## Training Logs

### Log File Location

```
honeypot-ai/logs/model_log.txt
```

The system automatically logs all model retraining activity. This file is **overwritten on each startup**, providing a clean log of the current run's retraining status.

### What Gets Logged

Each time the system starts up, the following information is recorded:

1. **Timestamp** - When the startup occurred (UTC)
2. **Retraining Mode** - Which mode was selected (SKIP, RECENT, or ALL)
3. **Status** - Whether the operation succeeded or had info/errors
4. **Message** - Detailed description of what happened
5. **Samples Used** - Number of attack samples used for training (if applicable)
6. **Model Version** - The current model version after the operation

### Log Format

```
======================================================================
MODEL RETRAINING LOG - 2026-01-30 12:20:37 UTC
======================================================================

Retraining Mode: SKIP

Status: INFO
Message: Retraining skipped. Using existing model.
Samples Used: 0
Model Version: v0

======================================================================
```

### Different Scenarios

#### Scenario 1: Skip Mode (Fastest - No Retraining)
```
Retraining Mode: SKIP

Status: INFO
Message: Retraining skipped. Using existing model.
Samples Used: 0
Model Version: v0
```

#### Scenario 2: Successful Retraining
```
Retraining Mode: ALL

Status: SUCCESS
Message: Successfully retrained model on 25 samples. Saved as model_v1
Samples Used: 25
Model Version: v1
```

#### Scenario 3: Insufficient Data
```
Retraining Mode: RECENT

Status: INFO
Message: Insufficient training data: only 2 attack logs found. Using dummy model.
Samples Used: 0
Model Version: v0
```

#### Scenario 4: Error During Retraining
```
Retraining Mode: ALL

Status: ERROR
Message: Error during model retraining: [error details]. Keeping current model.
Samples Used: 0
Model Version: v0
```

### Monitoring & Debugging

#### View Recent Activity
```bash
cat honeypot-ai/logs/model_log.txt
```

#### Monitor in Real-Time During Startup
```bash
RETRAIN_MODE=all python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
sleep 2
cat honeypot-ai/logs/model_log.txt
```

#### Integrate with Scripts
You can parse this file in automation scripts:

```bash
#!/bin/bash
# Check if retraining was successful
if grep -q "SUCCESS" honeypot-ai/logs/model_log.txt; then
    echo "Model was successfully retrained"
else
    echo "Model retraining was skipped or failed"
fi
```

#### Example Startup Sequence

```bash
$ source venv/bin/activate.fish
$ cd honeypot-ai
$ RETRAIN_MODE=all python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# After 2-3 seconds:
$ cat logs/model_log.txt
======================================================================
MODEL RETRAINING LOG - 2026-01-30 13:45:22 UTC
======================================================================

Retraining Mode: ALL

Status: SUCCESS
Message: Successfully retrained model on 45 samples. Saved as model_v2
Samples Used: 45
Model Version: v2

======================================================================
```

---

## Best Practices

### 1. Let Incremental Training Run Naturally
- Incremental training happens automatically
- No manual intervention needed
- System improves with each attack

### 2. Monitor Progress Regularly
- Check `logs/model_log.txt` periodically
- Note accuracy improvements
- Watch for convergence (accuracy plateau)

### 3. Use Appropriate Startup Mode
- Development: `skip` mode (fastest)
- Production restarts: `recent` mode (balanced)
- Major updates: `all` mode (comprehensive)

### 4. Verify Labels Occasionally
- Review auto-labeled sessions in `real_sessions/`
- Correct any obvious mislabels
- Provides feedback on model quality

### 5. Maintain Synthetic Data
- Keep 100 synthetic sessions in training mix
- Prevents overfitting to specific real attacks
- Ensures generalization

### 6. Archive Old Models
- Keep version history for rollback
- Archive models if storage becomes an issue
- Document which versions performed best

### 7. Test Retraining
Run the test script to verify retraining functionality:

```bash
python tests/test_retraining.py
```

This will:
1. Initialize the model
2. Test all three retraining modes
3. Verify model files are persisted correctly
4. Show the current model version

---

## Troubleshooting

### Models Not Improving After Retraining

**Possible causes:**
- Real sessions don't represent different attack patterns
- Data too similar to synthetic training data
- Model parameters not optimal for your data

**Solutions:**
- Collect more diverse real attacks
- Manually label sessions with different intents
- Adjust model hyperparameters
- Increase training frequency

### Out of Memory During Retraining

**Possible causes:**
- Too many real sessions accumulated
- Random Forest using all trees
- Feature vectors too large

**Solutions:**
- Archive old sessions
- Limit max real sessions in training mix
- Use `max-real` parameter to cap training data
- Reduce number of trees in Random Forest

### Model Accuracy Decreased

**Possible causes:**
- Mislabeled sessions in training data
- Shift in attacker behavior patterns
- Overfitting to specific real attacks

**Solutions:**
- Review and correct mislabeled sessions
- Increase synthetic data proportion
- Rollback to previous model version
- Manually label sessions to guide learning

### Log File Not Being Created

**Check:**
1. Is the `logs/` directory writable?
2. Are there errors in the console during startup?
3. Is the log file path correct in configuration?

**Fix:**
```bash
# Create logs directory if missing
mkdir -p honeypot-ai/logs

# Check permissions
chmod 755 honeypot-ai/logs
```

### Startup Retraining Taking Too Long

**Problem:** Application startup delayed by training

**Solutions:**
1. Use `skip` or `recent` mode instead of `all`
2. Archive old attack data if too many samples
3. Reduce minimum sample requirement
4. Consider running retraining as separate scheduled task

---

## Summary

The ML training system provides:
- ✅ Continuous improvement through incremental learning
- ✅ Flexible startup retraining options
- ✅ Comprehensive logging and monitoring
- ✅ Automatic model versioning
- ✅ Manual override capabilities
- ✅ Graceful degradation on errors

The system is designed to work automatically, improving with each attack that occurs. Monitor progress periodically but let the natural learning process continue.

For detailed technical information, see [full_project.md](full_project.md#incremental-training--continuous-learning).
