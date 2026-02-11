"""
Quick Test Script
Tests the feature extraction pipeline without requiring a trained model.
"""

from feature_extractor import FeatureExtractor
import pandas as pd
import json


def test_feature_extraction():
    """Test feature extraction on example emails."""
    
    feature_extractor = FeatureExtractor()
    
    # Example phishing email
    phishing_email = {
        'email_body': 'Dear customer, your account will be suspended. Click here immediately to verify: http://verify-account.tk/login?id=12345',
        'email_subject': 'URGENT: Account Suspension Warning!!!',
        'from_address': 'security@bank-verify.tk',
        'reply_to': 'noreply@different-domain.com',
        'urls': 'http://verify-account.tk/login?id=12345'
    }
    
    # Example legitimate email
    legitimate_email = {
        'email_body': 'Thank you for your recent purchase. Your order has been confirmed and will ship soon.',
        'email_subject': 'Order Confirmation',
        'from_address': 'orders@amazon.com',
        'urls': 'https://amazon.com/orders/12345'
    }
    
    print("Extracting features from phishing email...")
    phishing_features = feature_extractor.extract_features(phishing_email)
    
    print("\nExtracting features from legitimate email...")
    legitimate_features = feature_extractor.extract_features(legitimate_email)
    
    # Compare key features
    print("\n" + "="*60)
    print("FEATURE COMPARISON")
    print("="*60)
    
    key_features = [
        'phishing_keyword_count', 'url_count', 'has_url', 
        'from_is_trusted_provider', 'subject_has_urgency',
        'url_avg_url_length', 'urgency_word_count'
    ]
    
    comparison_data = {
        'Feature': [],
        'Phishing Email': [],
        'Legitimate Email': []
    }
    
    for feature in key_features:
        # Check all possible variations
        phish_val = None
        legit_val = None
        
        # Try direct feature name
        if feature in phishing_features:
            phish_val = phishing_features[feature]
            legit_val = legitimate_features.get(feature, 'N/A')
        else:
            # Try with prefixes
            for prefix in ['url_', 'url_avg_', 'url_max_', 'from_', 'reply_to_']:
                prefixed_feature = prefix + feature
                if prefixed_feature in phishing_features:
                    phish_val = phishing_features[prefixed_feature]
                    legit_val = legitimate_features.get(prefixed_feature, 'N/A')
                    break
        
        if phish_val is not None:
            comparison_data['Feature'].append(feature)
            comparison_data['Phishing Email'].append(phish_val)
            comparison_data['Legitimate Email'].append(legit_val)
    
    df_comparison = pd.DataFrame(comparison_data)
    print(df_comparison.to_string(index=False))
    
    print("\n" + "="*60)
    print("ALL FEATURES EXTRACTED")
    print("="*60)
    print(f"\nTotal features extracted: {len(phishing_features)}")
    print(f"\nSample features from phishing email:")
    for i, (key, value) in enumerate(list(phishing_features.items())[:10]):
        print(f"  {key}: {value}")
    print("  ...")
    
    return phishing_features, legitimate_features


if __name__ == '__main__':
    print("Phishing Detection Feature Extraction Test\n")
    test_feature_extraction()
    print("\n✓ Feature extraction test completed!")

