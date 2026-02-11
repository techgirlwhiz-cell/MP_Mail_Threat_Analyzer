"""
Model Training Script
Trains a phishing detection model using supervised learning.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    VotingClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
import joblib
import argparse
from feature_extractor import FeatureExtractor
import os


def load_data(data_path, label_column='label'):
    """
    Load training data from CSV file.
    
    Expected CSV columns:
    - email_body: Email body text
    - email_subject: Email subject
    - from_address: Sender email address
    - to_address: Recipient email address (optional)
    - reply_to: Reply-to address (optional)
    - urls: URLs in email (optional)
    - label: 1 for phishing, 0 for legitimate
    """
    df = pd.read_csv(data_path)
    return df


def prepare_features(df, feature_extractor):
    """Extract features from email data."""
    print("Extracting features from emails...")
    
    features_list = []
    for idx, row in df.iterrows():
        email_data = {
            'email_body': row.get('email_body', ''),
            'email_subject': row.get('email_subject', ''),
            'from_address': row.get('from_address', ''),
            'to_address': row.get('to_address', ''),
            'reply_to': row.get('reply_to', ''),
            'urls': row.get('urls', ''),
            'headers': None  # Can be enhanced to parse headers from string/dict
        }
        
        features = feature_extractor.extract_features(email_data)
        features_list.append(features)
    
    features_df = pd.DataFrame(features_list)
    print(f"Extracted {len(features_df.columns)} features")
    
    return features_df


def train_model(X_train, y_train, model_type='random_forest'):
    """Train a phishing detection model. Supports ensemble + calibration."""
    print(f"Training {model_type} model...")
    
    if model_type == 'ensemble':
        # Voting classifier (soft) over RF, GBM, LR; then probability calibration
        base_rf = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
        )
        base_gb = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42,
        )
        base_lr = LogisticRegression(
            max_iter=1000,
            random_state=42,
            solver='liblinear',
        )
        voting = VotingClassifier(
            estimators=[
                ('rf', base_rf),
                ('gb', base_gb),
                ('lr', base_lr),
            ],
            voting='soft',
            n_jobs=-1,
        )
        model = CalibratedClassifierCV(voting, cv=3, method='sigmoid')
        model.fit(X_train, y_train)
        return model
    elif model_type == 'random_forest':
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
    elif model_type == 'gradient_boosting':
        model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
    elif model_type == 'logistic_regression':
        model = LogisticRegression(
            max_iter=1000,
            random_state=42,
            solver='liblinear'
        )
    elif model_type == 'svm':
        model = SVC(
            kernel='rbf',
            probability=True,
            random_state=42
        )
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    model.fit(X_train, y_train)
    return model


def evaluate_model(model, X_test, y_test):
    """Evaluate the trained model."""
    print("\nEvaluating model...")
    
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nAccuracy: {accuracy:.4f}")
    
    if y_pred_proba is not None:
        try:
            auc = roc_auc_score(y_test, y_pred_proba)
            print(f"AUC-ROC: {auc:.4f}")
        except:
            pass
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Legitimate', 'Phishing']))
    
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    return {
        'accuracy': accuracy,
        'y_pred': y_pred,
        'y_pred_proba': y_pred_proba
    }


def main():
    parser = argparse.ArgumentParser(description='Train phishing detection model')
    parser.add_argument('--data', type=str, required=True, help='Path to training data CSV')
    parser.add_argument('--output', type=str, default='phishing_model.pkl', help='Output model path')
    parser.add_argument('--model-type', type=str, default='ensemble',
                       choices=['ensemble', 'random_forest', 'gradient_boosting', 'logistic_regression', 'svm'],
                       help='Type of model to train (ensemble = VotingClassifier + CalibratedClassifierCV)')
    parser.add_argument('--test-size', type=float, default=0.2, help='Test set size ratio')
    parser.add_argument('--scale', action='store_true', help='Scale features before training')
    
    args = parser.parse_args()
    
    # Load data
    print(f"Loading data from {args.data}...")
    df = load_data(args.data)
    
    if 'label' not in df.columns:
        raise ValueError("Data must contain 'label' column (1 for phishing, 0 for legitimate)")
    
    # Extract features
    feature_extractor = FeatureExtractor()
    X = prepare_features(df, feature_extractor)
    y = df['label'].values
    
    # Handle missing values
    X = X.fillna(0)
    
    # Replace inf values
    X = X.replace([np.inf, -np.inf], 0)
    
    # Scale features if requested
    scaler = None
    if args.scale:
        print("Scaling features...")
        scaler = StandardScaler()
        X = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=42, stratify=y
    )
    
    print(f"\nTraining set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    print(f"Phishing samples in training: {sum(y_train)} ({sum(y_train)/len(y_train)*100:.1f}%)")
    
    # Train model
    model = train_model(X_train, y_train, args.model_type)
    
    # Evaluate model
    evaluate_model(model, X_test, y_test)
    
    # Save model and feature extractor
    print(f"\nSaving model to {args.output}...")
    model_data = {
        'model': model,
        'feature_extractor': feature_extractor,
        'scaler': scaler,
        'feature_names': list(X.columns)
    }
    joblib.dump(model_data, args.output)
    print("Model saved successfully!")


if __name__ == '__main__':
    main()

