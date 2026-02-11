"""
Automatic Background Trainer
Handles automatic model training when dataset is uploaded.
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
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
import joblib
from feature_extractor import FeatureExtractor
from pathlib import Path
import os


class AutoTrainer:
    """Automatically trains models in the background."""
    
    def __init__(self, callback=None):
        self.callback = callback  # Callback for progress updates
        self.feature_extractor = FeatureExtractor()
    
    def check_if_training_data(self, df):
        """Check if dataframe has 'label' column for training."""
        return 'label' in df.columns
    
    def train_model_auto(self, df, output_path=None, model_type='auto', test_size=0.2):
        """
        Automatically train model from dataset.
        
        Args:
            df: DataFrame with email data and 'label' column
            output_path: Where to save the model
            model_type: 'auto' (best), 'random_forest', 'gradient_boosting', etc.
            test_size: Test set ratio
            
        Returns:
            dict with model, metrics, and path
        """
        if self.callback:
            self.callback("Starting automatic training...", 0)
        
        # Extract features
        if self.callback:
            self.callback("Extracting features from emails...", 10)
        
        features_list = []
        total = len(df)
        
        for idx, row in df.iterrows():
            email_data = {
                'email_body': str(row.get('email_body', '')),
                'email_subject': str(row.get('email_subject', '')),
                'from_address': str(row.get('from_address', '')),
                'to_address': str(row.get('to_address', '')),
                'reply_to': str(row.get('reply_to', '')),
                'urls': str(row.get('urls', '')),
            }
            
            features = self.feature_extractor.extract_features(email_data)
            features_list.append(features)
            
            if self.callback and idx % max(1, total // 10) == 0:
                progress = 10 + int((idx + 1) / total * 40)
                self.callback(f"Processing email {idx + 1}/{total}...", progress)
        
        X = pd.DataFrame(features_list)
        y = df['label'].values
        
        # Handle missing values
        X = X.fillna(0)
        X = X.replace([np.inf, -np.inf], 0)
        
        if self.callback:
            self.callback("Preparing data for training...", 50)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        if self.callback:
            self.callback(f"Training set: {len(X_train)} samples, Test set: {len(X_test)} samples", 60)
        
        # Select best model if auto
        if model_type == 'auto':
            model_type = self._select_best_model_type(X_train, y_train)
            if self.callback:
                self.callback(f"Selected model type: {model_type}", 65)
        
        # Train model
        if self.callback:
            self.callback(f"Training {model_type} model...", 70)
        
        model, scaler = self._train_model(X_train, y_train, model_type)
        
        # Evaluate (scale X_test if we used scaler for training)
        if self.callback:
            self.callback("Evaluating model...", 85)
        X_test_eval = X_test
        if scaler is not None:
            X_test_eval = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns)
        accuracy = accuracy_score(y_test, model.predict(X_test_eval))
        
        # Save model
        if output_path is None:
            output_path = f"auto_trained_model_{model_type}.pkl"
        
        model_data = {
            'model': model,
            'feature_extractor': self.feature_extractor,
            'scaler': scaler,
            'feature_names': list(X.columns),
            'model_type': model_type,
            'accuracy': accuracy,
            'train_size': len(X_train),
            'test_size': len(X_test)
        }
        
        joblib.dump(model_data, output_path)
        
        if self.callback:
            self.callback(f"Model saved to {output_path}", 95)
            self.callback("Training complete!", 100)
        
        return {
            'model_data': model_data,
            'model_path': output_path,
            'accuracy': accuracy,
            'model_type': model_type,
            'train_size': len(X_train),
            'test_size': len(X_test)
        }
    
    def _select_best_model_type(self, X_train, y_train):
        """Select model type; use ensemble for best robustness and calibration."""
        return 'ensemble'
    
    def _train_model(self, X_train, y_train, model_type):
        """Train a specific model type. Ensemble = VotingClassifier + CalibratedClassifierCV."""
        scaler = None
        
        if model_type == 'ensemble':
            scaler = StandardScaler()
            X_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)
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
                estimators=[('rf', base_rf), ('gb', base_gb), ('lr', base_lr)],
                voting='soft',
                n_jobs=-1,
            )
            model = CalibratedClassifierCV(voting, cv=3, method='sigmoid')
            model.fit(X_scaled, y_train)
            return model, scaler
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
            scaler = StandardScaler()
            X_train = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)
            model = LogisticRegression(
                max_iter=1000,
                random_state=42,
                solver='liblinear'
            )
        elif model_type == 'svm':
            scaler = StandardScaler()
            X_train = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)
            model = SVC(
                kernel='rbf',
                probability=True,
                random_state=42
            )
        else:
            model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        
        model.fit(X_train, y_train)
        return model, scaler

