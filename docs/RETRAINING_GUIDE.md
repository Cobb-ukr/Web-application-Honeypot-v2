# Model Retraining Guide

## Overview

The Honeypot AI system now includes adaptive model retraining that allows the ML model to learn from historical attack data. The model is retrained every time the program starts based on a command-line argument.

## Command-Line / Environment Variables

When starting the application, you can specify the retraining mode using the `RETRAIN_MODE` environment variable:

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

## Retraining Modes

### `all` Mode
- Retrains the model using **all historical attack data** from the database
- Best for: Initial setup or periodic full retraining
- Use case: When you want the model to learn from all past attacks accumulated in the system
- Performance: Slower startup, more comprehensive training

### `recent` Mode
- Retrains the model using attack data from the **last 7 days only**
- Best for: Regular restarts, maintaining freshness without full retraining
- Use case: When you want to adapt to recent attack trends without overtraining on old data
- Performance: Faster startup, focused on recent threats

### `skip` Mode (Default)
- **Skips retraining entirely** and loads the most recently trained model
- Best for: Quick restarts, development, testing
- Use case: When you don't have new attack data to train on yet
- Performance: Fastest startup

## Model Storage

- Models are stored in the `honeypot-ai/models/` directory
- Each retrained model is saved with a version number: `model_v1.pkl`, `model_v2.pkl`, etc.
- The latest model version is automatically loaded on startup
- Models persist between program restarts

## How It Works

1. **Database Initialization**: On startup, the database is initialized and attack signatures are seeded
2. **Model Loading**: The latest model version is loaded from the models directory (or dummy model if none exists)
3. **Retraining Decision**: Based on the `--retrain-mode` argument:
   - If `all`: Extracts all attack logs (excluding failed logins)
   - If `recent`: Extracts attack logs from the last 7 days
   - If `skip`: Skips retraining
4. **Feature Extraction**: For each attack log:
   - Extracts the malicious payload (username field)
   - Calculates features: length, entropy, special characters, suspicious keywords
   - Labels it as malicious (1) or clean (0)
5. **Model Training**: If sufficient data exists (5+ samples), retrains the RandomForest model
6. **Model Saving**: The newly trained model is saved with an incremented version number

## Data Filtering

During retraining, the system:
- **Excludes**: "Failed Login" and "Successful Login" entries
- **Includes**: Only actual attacks (SQLi, XSS, CommandInjection, PathTraversal, Anomaly)
- **Requires**: Minimum 5 attack samples to proceed with retraining

If insufficient data exists, the system falls back to the previous model or dummy model and continues startup normally.

## Logging

The retraining process logs informational messages about:
- Selected retraining mode
- Number of attack logs found
- Number of successfully parsed samples
- Model version after retraining
- Any errors or warnings encountered

Example output:
```
INFO:root:Retraining mode: all
INFO:root:Retraining on all historical attack data
INFO:root:Successfully retrained model on 25 samples. Saved as model_v2
```

## Batch File Configuration

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

Or simply use the default (no retraining):
```batch
@echo off
cd /d "%~dp0"
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
pause
```

## Testing

Run the test script to verify retraining functionality:

```bash
python honeypot-ai/test_retraining.py
```

This will:
1. Initialize the model
2. Test all three retraining modes
3. Verify model files are persisted correctly
4. Show the current model version

## Notes

- Retraining only occurs on startup, not continuously during runtime
- The model learns exclusively from attack payloads in the username field
- Each retraining increments the version counter
- Old model versions are preserved in the models directory for potential rollback
- If retraining fails for any reason, the system continues startup with the previous model
