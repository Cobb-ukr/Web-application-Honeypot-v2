# Model Retraining Logging Guide

## Overview

The Honeypot AI system now automatically logs all model retraining activity to a file called `model_log.txt` in the honeypot-ai root directory. This file is **overwritten on each startup**, providing a clean log of the current run's retraining status.

## Log File Location

```
honeypot-ai/model_log.txt
```

## What Gets Logged

Each time the system starts up, the following information is recorded:

1. **Timestamp** - When the startup occurred (UTC)
2. **Retraining Mode** - Which mode was selected (SKIP, RECENT, or ALL)
3. **Status** - Whether the operation succeeded or had info/errors
4. **Message** - Detailed description of what happened
5. **Samples Used** - Number of attack samples used for training (if applicable)
6. **Model Version** - The current model version after the operation

## Log File Format

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

## Different Scenarios

### Scenario 1: Skip Mode (Fastest - No Retraining)
```
Retraining Mode: SKIP

Status: INFO
Message: Retraining skipped. Using existing model.
Samples Used: 0
Model Version: v0
```

### Scenario 2: Successful Retraining
```
Retraining Mode: ALL

Status: SUCCESS
Message: Successfully retrained model on 25 samples. Saved as model_v1
Samples Used: 25
Model Version: v1
```

### Scenario 3: Insufficient Data
```
Retraining Mode: RECENT

Status: INFO
Message: Insufficient training data: only 2 attack logs found. Using dummy model.
Samples Used: 0
Model Version: v0
```

### Scenario 4: Error During Retraining
```
Retraining Mode: ALL

Status: ERROR
Message: Error during model retraining: [error details]. Keeping current model.
Samples Used: 0
Model Version: v0
```

## Using the Log File

### View Recent Activity
```bash
cat honeypot-ai/model_log.txt
```

### Monitor in Real-Time During Startup
```bash
RETRAIN_MODE=all python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
sleep 2
cat honeypot-ai/model_log.txt
```

### Integrate with Scripts
You can parse this file in automation scripts:

```bash
#!/bin/bash
# Check if retraining was successful
if grep -q "SUCCESS" honeypot-ai/model_log.txt; then
    echo "Model was successfully retrained"
else
    echo "Model retraining was skipped or failed"
fi
```

## File Overwriting Behavior

- **On Each Startup**: The log file is completely overwritten
- **Previous Logs**: Discarded (only the current run's log is kept)
- **No Accumulation**: Log file only contains the latest startup information

This design keeps the log file clean and focused on the current session.

## Implementation Details

The logging is handled by two functions:

### In `backend/main.py`
- `retrain_ai_model()` - Orchestrates retraining and writes to file

### In `backend/ai_engine.py`
- `retrain_on_historical_data()` - Returns detailed result dictionary with:
  - `success` (bool)
  - `message` (str)
  - `samples` (int)
  - `version` (int)

## Example Startup Sequence

```bash
$ source venv/bin/activate.fish
$ cd honeypot-ai
$ RETRAIN_MODE=all python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# After 2-3 seconds:
$ cat model_log.txt
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

## Debugging Tips

1. **Check if retraining ran**: Look for "SUCCESS" or "INFO" status
2. **Understand why it didn't retrain**: Check the message for reasons (insufficient data, errors, etc.)
3. **Track model improvements**: Monitor the model version number increases
4. **Verify the log file is being written**: Check the timestamp updates each restart

## Notes

- The log file is created automatically on the first startup
- Directory must be writable for logging to work
- If the log file cannot be written, an error will appear in console logs but startup will continue
- The log file is human-readable and does not require parsing
- Timestamps are in UTC timezone
