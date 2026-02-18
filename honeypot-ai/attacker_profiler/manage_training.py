import argparse
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from attacker_profiler.incremental_trainer import (
    load_real_sessions,
    retrain_with_real_sessions,
    save_real_session,
    auto_label_session,
)


def main():
    parser = argparse.ArgumentParser(description="Manage incremental training for attacker profiler")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # List sessions
    list_parser = subparsers.add_parser("list", help="List real sessions")
    list_parser.add_argument("--all", action="store_true", help="Show all sessions (including unlabeled)")
    
    # Retrain model
    retrain_parser = subparsers.add_parser("retrain", help="Retrain model with real sessions")
    retrain_parser.add_argument("--synthetic", type=int, default=100, help="Number of synthetic sessions")
    retrain_parser.add_argument("--threshold", type=float, default=0.70, help="Confidence threshold for auto-labeling")
    retrain_parser.add_argument("--min-real", type=int, default=5, help="Minimum real sessions required")
    
    # Auto-label
    label_parser = subparsers.add_parser("label", help="Auto-label a specific session")
    label_parser.add_argument("session_id", help="Session ID to label")
    label_parser.add_argument("--threshold", type=float, default=0.70, help="Confidence threshold")
    
    args = parser.parse_args()
    
    if args.command == "list":
        sessions = load_real_sessions(labeled_only=not args.all)
        print(f"Found {len(sessions)} sessions")
        for s in sessions:
            labeled = "✓" if s.get("labeled") else "✗"
            auto = " (auto)" if s.get("auto_labeled") else ""
            intent = s.get("intent", "N/A")
            skill = s.get("skill", "N/A")
            cmd_count = len(s.get("commands", []))
            print(f"{labeled} {s['session_id'][:8]}... | {cmd_count} cmds | {intent}/{skill}{auto}")
    
    elif args.command == "retrain":
        retrain_with_real_sessions(
            num_synthetic=args.synthetic,
            confidence_threshold=args.threshold,
            min_real_sessions=args.min_real,
        )
    
    elif args.command == "label":
        result = auto_label_session(args.session_id, confidence_threshold=args.threshold)
        if result:
            print(f"Session {args.session_id} labeled successfully")
        else:
            print(f"Failed to label session {args.session_id}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
