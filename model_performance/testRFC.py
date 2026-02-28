#!/usr/bin/env python3
"""
Test script for the Threat Detection Model (RandomForest Classifier).
Trains a new model on database attack data and evaluates its performance.

The model uses 4 features:
- length: Length of the payload
- entropy: Shannon entropy (randomness)
- special_chars: Count of non-alphanumeric characters
- keywords: Count of suspicious keywords

Usage:
    python test_threat_model_accuracy.py
"""

import os
import sys
import re
import math
import csv
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, precision_score, recall_score, f1_score
from datetime import datetime


def calculate_entropy(text):
    """Calculate Shannon entropy of a string."""
    if not text:
        return 0
    entropy = 0
    for x in range(256):
        p_x = float(text.count(chr(x))) / len(text)
        if p_x > 0:
            entropy += - p_x * math.log(p_x, 2)
    return entropy


def extract_features(payload):
    """Extract features from a payload (same as AIEngine.extract_features)."""
    if not payload:
        return [0, 0, 0, 0]
    
    length = len(payload)
    entropy = calculate_entropy(payload)
    special_chars = len(re.findall(r'[^a-zA-Z0-9\s]', payload))
    keywords = len(re.findall(r'(select|union|insert|delete|update|script|alert|etc|passwd)', payload, re.IGNORECASE))
    
    return [length, entropy, special_chars, keywords]


def load_data_from_csv():
    """
    Load attack data from CSV file and extract features and labels.
    
    Returns:
        tuple: (X, y, payloads) where:
            X: Feature vectors
            y: Binary labels (0=clean/failed login, 1=malicious attack)
            payloads: Original payloads for reference
    """
    csv_path = 'data.csv'
    
    # Check if CSV exists in current directory
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        print(f"Current directory: {os.getcwd()}")
        print("Make sure data.csv is in the model_performance folder")
        return None, None, None
    
    print(f"📂 Loading data from {csv_path}...")
    
    try:
        X = []
        y = []
        payloads = []
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    payload = row.get('payload', '').strip()
                    attack_type = row.get('attack_type', '').strip()
                    
                    if not payload:
                        continue
                    
                    # Extract features
                    features = extract_features(payload)
                    X.append(features)
                    payloads.append(payload)
                    
                    # Label: 1 if it's an actual attack, 0 if clean/failed login
                    is_malicious = attack_type in ["SQLi", "XSS", "CommandInjection", "PathTraversal", "Anomaly"]
                    y.append(1 if is_malicious else 0)
                    
                except Exception as e:
                    continue
        
        if len(X) < 5:
            print(f"❌ Insufficient data: only {len(X)} valid samples")
            return None, None, None
        
        print(f"✓ Loaded {len(X)} samples from CSV")
        print(f"  Clean samples: {sum(1 for label in y if label == 0)}")
        print(f"  Malicious samples: {sum(1 for label in y if label == 1)}")
        
        return np.array(X), np.array(y), payloads
        
    except Exception as e:
        print(f"❌ Error loading data from CSV: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None


def train_model(X_train, y_train):
    """Train a RandomForest classifier on the training data."""
    print("\n🤖 Training RandomForest model...")
    try:
        model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=20)
        model.fit(X_train, y_train)
        print(f"✓ Model trained on {len(X_train)} samples")
        return model
    except Exception as e:
        print(f"❌ Error training model: {e}")
        return None


def evaluate_model(model, X_test, y_test, payloads_test):
    """Evaluate the model and print comprehensive metrics."""
    print("\n" + "=" * 70)
    print("THREAT DETECTION MODEL EVALUATION")
    print("=" * 70)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    
    print(f"\nOverall Accuracy: {accuracy * 100:.2f}%")
    print(f"Total Test Samples: {len(y_test)}")
    print(f"Correct Predictions: {sum(y_test == y_pred)}/{len(y_test)}")
    print(f"Incorrect Predictions: {sum(y_test != y_pred)}/{len(y_test)}")
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    print("\n" + "-" * 70)
    print("CONFUSION MATRIX")
    print("-" * 70)
    print("                  Predicted Clean    Predicted Malicious")
    print(f"Actual Clean          {cm[0][0]:4d}                {cm[0][1]:4d}")
    print(f"Actual Malicious      {cm[1][0]:4d}                {cm[1][1]:4d}")
    
    # Calculate metrics from confusion matrix
    true_negatives = cm[0][0]
    false_positives = cm[0][1]
    false_negatives = cm[1][0]
    true_positives = cm[1][1]
    
    print("\n" + "-" * 70)
    print("DETAILED METRICS")
    print("-" * 70)
    print(f"True Positives (TP):  {true_positives:4d}  (Malicious correctly detected)")
    print(f"True Negatives (TN):  {true_negatives:4d}  (Clean correctly identified)")
    print(f"False Positives (FP): {false_positives:4d}  (Clean flagged as malicious)")
    print(f"False Negatives (FN): {false_negatives:4d}  (Malicious missed)")
    print()
    print(f"Accuracy:  {accuracy * 100:.2f}%")
    print(f"Precision: {precision * 100:.2f}%  (of flagged attacks, how many were real?)")
    print(f"Recall:    {recall * 100:.2f}%    (of real attacks, how many were caught?)")
    print(f"F1-Score:  {f1 * 100:.2f}%")
    
    # Classification Report
    print("\n" + "-" * 70)
    print("CLASSIFICATION REPORT")
    print("-" * 70)
    target_names = ['Clean', 'Malicious']
    print(classification_report(y_test, y_pred, target_names=target_names, zero_division=0))
    
    # Show misclassifications
    misclassified = []
    for i in range(len(y_test)):
        if y_test[i] != y_pred[i]:
            misclassified.append((payloads_test[i], y_test[i], y_pred[i]))
    
    if misclassified:
        print("-" * 70)
        print(f"MISCLASSIFIED SAMPLES ({len(misclassified)} total)")
        print("-" * 70)
        for i, (payload, actual, predicted) in enumerate(misclassified[:10], 1):
            actual_label = "Clean" if actual == 0 else "Malicious"
            predicted_label = "Clean" if predicted == 0 else "Malicious"
            print(f"{i}. Payload: '{payload[:60]}{'...' if len(payload) > 60 else ''}'")
            print(f"   Actual: {actual_label} | Predicted: {predicted_label}")
            print()
        
        if len(misclassified) > 10:
            print(f"... and {len(misclassified) - 10} more misclassified samples")
    else:
        print("\n✅ No misclassifications! Perfect model performance.")
    
    # Overall assessment
    print("\n" + "=" * 70)
    print("OVERALL ASSESSMENT")
    print("=" * 70)
    if accuracy >= 0.95:
        rating = "EXCELLENT ⭐⭐⭐⭐⭐"
        comment = "Model performs exceptionally well!"
    elif accuracy >= 0.85:
        rating = "GOOD ⭐⭐⭐⭐"
        comment = "Model performs well but has room for improvement."
    elif accuracy >= 0.75:
        rating = "FAIR ⭐⭐⭐"
        comment = "Model needs improvement to reliably detect threats."
    else:
        rating = "NEEDS IMPROVEMENT ⭐⭐"
        comment = "Model requires retraining with more diverse data."
    
    print(f"Rating: {rating}")
    print(f"Comment: {comment}")
    
    if false_negatives > 0:
        print(f"\n⚠️  WARNING: {false_negatives} malicious payloads were missed (False Negatives)")
        print("   This is critical - attackers could bypass detection!")
    
    if false_positives > 0:
        print(f"\n⚠️  NOTE: {false_positives} clean payloads were flagged as malicious (False Positives)")
        print("   This could impact legitimate users.")
    
    print("=" * 70)
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'confusion_matrix': cm
    }


def main():
    """Main function to run the model training and evaluation."""
    print("=" * 70)
    print("THREAT DETECTION MODEL - TRAIN & TEST")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load data from CSV
    X, y, payloads = load_data_from_csv()
    if X is None or len(X) < 10:
        print("\n❌ Cannot proceed without sufficient data.")
        print("\nTo generate data:")
        print("1. Ensure data.csv exists in the model_performance folder")
        print("2. You can add more attack samples to data.csv manually")
        print("3. CSV format: payload, attack_type, timestamp")
        print("4. Re-run this test script")
        return
    
    # Split data into training and testing sets
    print(f"\n📊 Splitting data into train/test (80/20 split)...")
    X_train, X_test, y_train, y_test, payloads_train, payloads_test = train_test_split(
        X, y, payloads,
        test_size=0.2,
        random_state=42,
        stratify=y if len(np.unique(y)) > 1 else None
    )
    
    print(f"✓ Training set: {len(X_train)} samples")
    print(f"  Clean: {sum(1 for label in y_train if label == 0)}")
    print(f"  Malicious: {sum(1 for label in y_train if label == 1)}")
    print(f"✓ Test set: {len(X_test)} samples")
    print(f"  Clean: {sum(1 for label in y_test if label == 0)}")
    print(f"  Malicious: {sum(1 for label in y_test if label == 1)}")
    
    # Train the model
    model = train_model(X_train, y_train)
    if model is None:
        return
    
    # Evaluate the model
    results = evaluate_model(model, X_test, y_test, payloads_test)
    
    print("\n✅ Evaluation complete!")
    print(f"Final Accuracy: {results['accuracy'] * 100:.2f}%")
    print(f"Final Precision: {results['precision'] * 100:.2f}%")
    print(f"Final Recall: {results['recall'] * 100:.2f}%")
    print(f"Final F1-Score: {results['f1_score'] * 100:.2f}%")


if __name__ == "__main__":
    main()
