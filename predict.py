"""
Prediction Script
Uses trained model to predict if an email is phishing
and stores results in Supabase.
"""

import pandas as pd
import joblib
import argparse
import json
from feature_extractor import FeatureExtractor
from supabase_client import supabase


# ================= SINGLE EMAIL PREDICTION =================
def predict_email(model_path, email_data, user_id=None, output_format='dict'):
    """
    Predict if an email is phishing and optionally save to Supabase.

    Args:
        model_path: Path to saved model
        email_data: Dictionary with email data
        user_id: Supabase user ID (optional)
        output_format: 'dict' or 'json'

    Returns:
        Prediction result
    """

    # ----- Load model -----
    model_data = joblib.load(model_path)
    model = model_data['model']
    feature_extractor = model_data.get('feature_extractor', FeatureExtractor())
    scaler = model_data.get('scaler')
    feature_names = model_data.get('feature_names')

    # ----- Feature extraction -----
    features = feature_extractor.extract_features(email_data)
    features_df = pd.DataFrame([features])

    # Ensure feature order matches training
    if feature_names:
        for col in feature_names:
            if col not in features_df.columns:
                features_df[col] = 0
        features_df = features_df[feature_names]

    features_df = features_df.fillna(0)

    if scaler:
        features_df = pd.DataFrame(
            scaler.transform(features_df),
            columns=features_df.columns
        )

    # ----- Prediction -----
    prediction = model.predict(features_df)[0]
    probability = (
        model.predict_proba(features_df)[0]
        if hasattr(model, 'predict_proba')
        else None
    )

    result = {
        'is_phishing': int(prediction),
        'label': 'Phishing' if prediction == 1 else 'Legitimate',
        'confidence': float(probability[1]) if probability is not None else None
    }

    # ----- Save to Supabase -----
    try:
        supabase.table("email_scans").insert({
            "user_id": user_id,
            "email_subject": email_data.get("email_subject"),
            "email_body": email_data.get("email_body"),
            "from_address": email_data.get("from_address"),
            "urls": email_data.get("urls"),
            "prediction": int(prediction),
            "confidence": result["confidence"]
        }).execute()
    except Exception as e:
        print("⚠️ Supabase insert failed:", e)

    if output_format == 'json':
        return json.dumps(result, indent=2)

    return result


# ================= BATCH PREDICTION =================
def predict_batch(model_path, email_data_list, user_id=None, output_path=None):
    """
    Predict for multiple emails and save results to Supabase.

    Args:
        model_path: Path to saved model
        email_data_list: List of email data dictionaries
        user_id: Supabase user ID (optional)
        output_path: Optional CSV output

    Returns:
        DataFrame with predictions
    """

    # ----- Load model -----
    model_data = joblib.load(model_path)
    model = model_data['model']
    feature_extractor = model_data.get('feature_extractor', FeatureExtractor())
    scaler = model_data.get('scaler')
    feature_names = model_data.get('feature_names')

    # ----- Feature extraction -----
    features_list = [
        feature_extractor.extract_features(email)
        for email in email_data_list
    ]

    features_df = pd.DataFrame(features_list)

    if feature_names:
        for col in feature_names:
            if col not in features_df.columns:
                features_df[col] = 0
        features_df = features_df[feature_names]

    features_df = features_df.fillna(0)

    if scaler:
        features_df = pd.DataFrame(
            scaler.transform(features_df),
            columns=features_df.columns
        )

    # ----- Prediction -----
    predictions = model.predict(features_df)
    probabilities = (
        model.predict_proba(features_df)[:, 1]
        if hasattr(model, 'predict_proba')
        else None
    )

    results = pd.DataFrame({
        'is_phishing': predictions,
        'label': ['Phishing' if p == 1 else 'Legitimate' for p in predictions],
        'confidence': probabilities
    })

    # ----- Save batch results to Supabase -----
    for email_data, pred, conf in zip(email_data_list, predictions, probabilities):
        try:
            supabase.table("email_scans").insert({
                "user_id": user_id,
                "email_subject": email_data.get("email_subject"),
                "email_body": email_data.get("email_body"),
                "from_address": email_data.get("from_address"),
                "urls": email_data.get("urls"),
                "prediction": int(pred),
                "confidence": float(conf) if conf is not None else None
            }).execute()
        except Exception as e:
            print("⚠️ Supabase insert failed:", e)

    if output_path:
        results.to_csv(output_path, index=False)
        print(f"Predictions saved to {output_path}")

    return results


# ================= CLI ENTRY =================
def main():
    parser = argparse.ArgumentParser(description='Predict if email is phishing')
    parser.add_argument('--model', type=str, required=True, help='Path to trained model')
    parser.add_argument('--email', type=str, help='Path to single email JSON file')
    parser.add_argument('--batch', type=str, help='Path to CSV file with emails')
    parser.add_argument('--output', type=str, help='Output path for batch predictions')

    args = parser.parse_args()

    if args.email:
        with open(args.email, 'r') as f:
            email_data = json.load(f)

        result = predict_email(args.model, email_data, output_format='json')
        print(result)

    elif args.batch:
        df = pd.read_csv(args.batch)
        email_data_list = df.to_dict('records')

        results = predict_batch(args.model, email_data_list, output_path=args.output)
        print("\nPredictions:")
        print(results)

    else:
        print("⚠️ Please provide --email or --batch")


if __name__ == '__main__':
    main()
