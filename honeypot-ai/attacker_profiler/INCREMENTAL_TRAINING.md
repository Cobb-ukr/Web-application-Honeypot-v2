# Incremental Training for Attacker Profiler

## How It Works

When a honeypot session ends (logout), the system automatically:
1. Saves the session commands to `attacker_profiler/real_sessions/`
2. Auto-labels the session using the current model (if confidence ≥ 70%)
3. Retrains the model every 10 labeled sessions

## Files Created

- `attacker_profiler/real_sessions/*.json` - Stored real honeypot sessions
- `attacker_profiler/training_log.json` - Training history with metrics

## Manual Management

List all sessions:
```bash
python attacker_profiler/manage_training.py list --all
```

Force retrain with current real sessions:
```bash
python attacker_profiler/manage_training.py retrain --synthetic 100 --min-real 5
```

Manually label a session:
```bash
python attacker_profiler/manage_training.py label <session_id> --threshold 0.70
```

## Configuration

Edit `incremental_trainer.py` to change:
- `confidence_threshold`: Minimum confidence for auto-labeling (default: 0.70)
- Auto-retrain trigger: Currently every 10 sessions (line in `trigger_incremental_update`)
- Synthetic/real session ratio in retraining

## Monitoring

Check training log:
```bash
cat attacker_profiler/training_log.json
```

View session count:
```bash
ls attacker_profiler/real_sessions/ | wc -l
```
