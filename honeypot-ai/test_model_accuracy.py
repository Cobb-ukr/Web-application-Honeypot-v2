"""
Simple test script to evaluate the trained Random Forest models.
Tests both intent classification and skill assessment models.
"""
import os
import sys
import joblib
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from pathlib import Path

# Add attacker_profiler to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'attacker_profiler'))

try:
    from step2_generate import generate_synthetic_sessions
    from step3_aggregate import aggregate_session_features
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("Make sure you're running this from the honeypot-ai directory")
    sys.exit(1)

def find_latest_model(model_dir):
    """Find the latest model file in the directory"""
    model_files = list(Path(model_dir).glob("session_model_v*.pkl"))
    if not model_files:
        return None
    # Sort by version number
    model_files.sort(key=lambda x: int(x.stem.split('_v')[1]))
    return model_files[-1]

def load_model(model_path):
    """Load the trained model"""
    try:
        model_data = joblib.load(model_path)
        return model_data
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None

def generate_test_data(n_samples=100):
    """Generate synthetic test data"""
    print(f"📊 Generating {n_samples} test samples...")
    try:
        sessions = generate_synthetic_sessions(n_samples)
        
        # Aggregate features
        features = []
        labels_intent = []
        labels_skill = []
        
        for session in sessions:
            feature_vector = aggregate_session_features(session)
            features.append(feature_vector)
            labels_intent.append(session['intent'])
            labels_skill.append(session['skill'])
        
        return np.array(features), labels_intent, labels_skill
    except Exception as e:
        print(f"❌ Error generating test data: {e}")
        return None, None, None

def evaluate_model(model, X_test, y_test, model_name="Model"):
    """Evaluate model and print metrics"""
    print(f"\n{'='*60}")
    print(f"📈 {model_name} Evaluation")
    print(f"{'='*60}")
    
    try:
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate accuracy
        accuracy = accuracy_score(y_test, y_pred)
        print(f"\n✅ Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        
        # Get unique labels
        labels = sorted(set(y_test + y_pred))
        
        # Confusion Matrix
        print(f"\n📊 Confusion Matrix:")
        cm = confusion_matrix(y_test, y_pred, labels=labels)
        
        # Print header
        print("\n" + " " * 15, end="")
        for label in labels:
            print(f"{label[:12]:>12}", end=" ")
        print()
        print(" " * 15 + "-" * (13 * len(labels)))
        
        # Print matrix
        for i, label in enumerate(labels):
            print(f"{label[:12]:>12} | ", end="")
            for j in range(len(labels)):
                print(f"{cm[i][j]:>12}", end=" ")
            print()
        
        # Classification Report
        print(f"\n📋 Classification Report:")
        print("-" * 60)
        report = classification_report(y_test, y_pred, labels=labels, zero_division=0)
        print(report)
        
        # Per-class accuracy
        print(f"\n📊 Per-Class Accuracy:")
        print("-" * 60)
        for i, label in enumerate(labels):
            if cm[i].sum() > 0:
                class_acc = cm[i][i] / cm[i].sum()
                print(f"{label:>15}: {class_acc:.4f} ({class_acc*100:.2f}%)")
        
        return accuracy
        
    except Exception as e:
        print(f"❌ Error evaluating model: {e}")
        return None

def main():
    print("="*60)
    print("🧪 Random Forest Model Accuracy Test")
    print("="*60)
    
    # Find model directory
    model_dir = Path(__file__).parent / "attacker_profiler" / "model_store"
    
    if not model_dir.exists():
        print(f"❌ Model directory not found: {model_dir}")
        print("Please train a model first using the training scripts.")
        sys.exit(1)
    
    # Find latest model
    print(f"\n🔍 Looking for trained models in: {model_dir}")
    model_path = find_latest_model(model_dir)
    
    if not model_path:
        print("❌ No trained model found!")
        print("Please train a model first using:")
        print("  python attacker_profiler/step4_train.py")
        sys.exit(1)
    
    print(f"✅ Found model: {model_path.name}")
    
    # Load model
    print(f"\n📦 Loading model...")
    model_data = load_model(model_path)
    
    if not model_data:
        sys.exit(1)
    
    # Check if model has both classifiers
    if 'intent_model' not in model_data or 'skill_model' not in model_data:
        print("❌ Model file doesn't contain both intent and skill classifiers!")
        print(f"Model contains: {list(model_data.keys())}")
        sys.exit(1)
    
    intent_model = model_data['intent_model']
    skill_model = model_data['skill_model']
    
    print(f"✅ Loaded intent classifier: {type(intent_model).__name__}")
    print(f"✅ Loaded skill classifier: {type(skill_model).__name__}")
    
    # Generate test data
    print(f"\n{'='*60}")
    print("🧬 Generating Test Data")
    print(f"{'='*60}")
    
    X_test, y_intent_test, y_skill_test = generate_test_data(n_samples=200)
    
    if X_test is None:
        print("❌ Failed to generate test data")
        sys.exit(1)
    
    print(f"✅ Generated {len(X_test)} test samples")
    print(f"   - Intent classes: {set(y_intent_test)}")
    print(f"   - Skill classes: {set(y_skill_test)}")
    
    # Evaluate Intent Model
    intent_accuracy = evaluate_model(
        intent_model, 
        X_test, 
        y_intent_test, 
        "Intent Classification Model"
    )
    
    # Evaluate Skill Model
    skill_accuracy = evaluate_model(
        skill_model, 
        X_test, 
        y_skill_test, 
        "Skill Assessment Model"
    )
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Overall Summary")
    print(f"{'='*60}")
    print(f"Model File: {model_path.name}")
    print(f"Test Samples: {len(X_test)}")
    print(f"\n✅ Intent Classification Accuracy: {intent_accuracy:.4f} ({intent_accuracy*100:.2f}%)")
    print(f"✅ Skill Assessment Accuracy: {skill_accuracy:.4f} ({skill_accuracy*100:.2f}%)")
    
    # Overall performance rating
    avg_accuracy = (intent_accuracy + skill_accuracy) / 2
    print(f"\n🎯 Average Accuracy: {avg_accuracy:.4f} ({avg_accuracy*100:.2f}%)")
    
    if avg_accuracy >= 0.90:
        rating = "🌟 Excellent"
    elif avg_accuracy >= 0.80:
        rating = "✅ Good"
    elif avg_accuracy >= 0.70:
        rating = "⚠️  Fair"
    else:
        rating = "❌ Needs Improvement"
    
    print(f"Overall Performance: {rating}")
    print(f"{'='*60}")
    
    print("\n💡 Note: This test uses synthetic data. Real-world performance")
    print("   may vary based on actual attacker behavior patterns.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
