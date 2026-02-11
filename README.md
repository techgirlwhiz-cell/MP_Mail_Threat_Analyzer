# Phishing Detection AI Model

A comprehensive machine learning system for detecting phishing emails using NLP techniques and supervised learning. This project analyzes email content, URLs, and metadata to identify phishing attempts.

> **📖 New to this project?** Start with [QUICK_START.md](QUICK_START.md) for a simple 5-step guide!

## Features

- **Email Content Analysis**: NLP-based feature extraction from email body and subject
  - Phishing keyword detection
  - Text complexity and structure analysis
  - Urgency and emotional manipulation indicators
  - Pattern matching for suspicious content

- **URL Analysis**: Comprehensive URL feature extraction
  - Domain analysis (TLD, entropy, subdomains)
  - Path and query parameter examination
  - Suspicious pattern detection
  - URL shortening service detection

- **Metadata Analysis**: Email header and structure analysis
  - Sender/reply-to address validation
  - Domain reputation checks
  - Subject line analysis
  - Header integrity checks

- **Multiple ML Algorithms**: Support for various supervised learning models
  - Random Forest (default)
  - Gradient Boosting
  - Logistic Regression
  - Support Vector Machine (SVM)

## Quick Start Guide

Follow these steps to get started:

### Step 1: Install Dependencies

Open a terminal/command prompt in the project directory and run:

```bash
pip install -r requirements.txt
```

**Note**: If you get a "python not found" error, try `python3` instead of `python`, or ensure Python is installed and added to your PATH.

### Step 1.5: Download NLTK Language Data

Run the setup script to download required NLTK resources:

```bash
python setup_nltk.py
```

**Important**: You only need to run this once. This downloads the language models needed for text analysis.

### Step 2: Test Feature Extraction (Optional but Recommended)

Verify that everything works by testing feature extraction:

```bash
python quick_test.py
```

This will show you how features are extracted from example emails. You should see a comparison between phishing and legitimate email features.

### Step 3: Prepare Training Data

Create a CSV file with your email data. You can use the provided `example_training_data.csv` as a template.

**Required columns:**
- `email_body`: The email body text
- `email_subject`: Email subject line
- `from_address`: Sender email address
- `label`: `1` for phishing, `0` for legitimate

**Optional columns:**
- `to_address`: Recipient email address
- `reply_to`: Reply-to address
- `urls`: URLs in the email

**Example CSV format:**
```csv
email_body,email_subject,from_address,urls,label
"Dear customer, verify your account...","Urgent: Verify Account","security@example.com","http://verify.example.com",1
"Thank you for your purchase...","Order Confirmation","orders@store.com","https://store.com/order",0
```

### Step 4: Train the Model

Train your phishing detection model using the training data:

```bash
python train_model.py --data example_training_data.csv --output phishing_model.pkl
```

**Command options:**
- `--data`: Path to your training CSV file (required)
- `--output`: Where to save the trained model (default: `phishing_model.pkl`)
- `--model-type`: Choose algorithm: `random_forest` (default), `gradient_boosting`, `logistic_regression`, or `svm`
- `--test-size`: Fraction of data for testing (default: 0.2, meaning 20%)
- `--scale`: Use this flag for SVM or Logistic Regression models

**Example with all options:**
```bash
python train_model.py --data my_training_data.csv --output my_model.pkl --model-type random_forest --test-size 0.2
```

The script will:
1. Extract features from all emails
2. Split data into training and testing sets
3. Train the model
4. Show accuracy and performance metrics
5. Save the trained model to the output file

### Step 5: Make Predictions

#### Option A: Predict Single Email

1. Create a JSON file (you can use `example_email.json` as a template):
```json
{
  "email_body": "Your account needs verification. Click here now!",
  "email_subject": "Urgent: Verify Account",
  "from_address": "security@example.com",
  "urls": "http://verify-account.example.com"
}
```

2. Run prediction:
```bash
python predict.py --model phishing_model.pkl --email example_email.json
```

The output will show:
- `is_phishing`: 1 if phishing, 0 if legitimate
- `label`: "Phishing" or "Legitimate"
- `confidence`: Probability score (0.0 to 1.0)

#### Option B: Batch Prediction (Multiple Emails)

1. Create a CSV file with emails (same format as training data, but **without** the `label` column)

2. Run batch prediction:
```bash
python predict.py --model phishing_model.pkl --batch emails_to_check.csv --output predictions.csv
```

This will create a `predictions.csv` file with predictions for all emails.

## Detailed Installation

1. Clone or download this repository

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Download NLTK data (run this setup script once):
```bash
python setup_nltk.py
```

Alternatively, you can download manually in Python:
```python
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')  # Required for newer NLTK versions
nltk.download('stopwords')
```

## Detailed Usage Guide

### 1. Prepare Training Data

Create a CSV file with your training data. Required columns:
- `email_body`: The email body text
- `email_subject`: Email subject line
- `from_address`: Sender email address
- `label`: 1 for phishing, 0 for legitimate

Optional columns:
- `to_address`: Recipient email address
- `reply_to`: Reply-to address
- `urls`: URLs found in the email (comma-separated or JSON list)

Example CSV structure:
```csv
email_body,email_subject,from_address,label
"Click here to verify your account...","Urgent: Verify Account","phish@example.com",1
"Thanks for your purchase...","Order Confirmation","orders@amazon.com",0
```

### 2. Train the Model

```bash
python train_model.py --data training_data.csv --output phishing_model.pkl --model-type random_forest
```

Options:
- `--data`: Path to training data CSV (required)
- `--output`: Output path for saved model (default: `phishing_model.pkl`)
- `--model-type`: Model type - `random_forest`, `gradient_boosting`, `logistic_regression`, or `svm` (default: `random_forest`)
- `--test-size`: Test set size ratio (default: 0.2)
- `--scale`: Scale features before training (recommended for SVM and Logistic Regression)

### 3. Make Predictions

#### Single Email Prediction

Create a JSON file with email data:
```json
{
  "email_body": "Dear customer, please verify your account immediately by clicking the link.",
  "email_subject": "Urgent: Verify Your Account",
  "from_address": "security@example.com",
  "urls": "http://example-verify.com/login"
}
```

Then predict:
```bash
python predict.py --model phishing_model.pkl --email email.json
```

#### Batch Prediction

For CSV file with emails (same format as training data, without label column):
```bash
python predict.py --model phishing_model.pkl --batch emails.csv --output predictions.csv
```

### 4. Programmatic Usage

```python
from feature_extractor import FeatureExtractor
import joblib

# Load trained model
model_data = joblib.load('phishing_model.pkl')
model = model_data['model']
feature_extractor = model_data['feature_extractor']

# Prepare email data
email_data = {
    'email_body': 'Your account will be suspended...',
    'email_subject': 'Urgent: Account Suspension',
    'from_address': 'noreply@example.com',
    'urls': 'http://verify-account.example.com'
}

# Extract features and predict
features = feature_extractor.extract_features(email_data)
# ... convert to DataFrame, scale if needed, and predict using model
```

## How to Run the Application

**Web dashboard (recommended):**
```bash
python web_backend.py
# or: ./run_web_ui.sh
```
Then open http://localhost:5001/login.html in your browser. Sign in with email/password (e.g. demo@example.com / demo123) or Connect Gmail.

**Desktop GUI (login + full dashboard):**
```bash
python app.py
```
Launches a login window, then the main phishing detection dashboard (CustomTkinter).

See [APPLICATION_OVERVIEW.md](APPLICATION_OVERVIEW.md) for end-to-end flow and [WEB_UI_README.md](WEB_UI_README.md) for the web interface.

## Example Data

See `example_training_data.csv` for a sample training dataset format.

## Model Performance

The model extracts 80+ features from emails, URLs, and metadata. Typical performance:
- Accuracy: 85-95% (depending on training data quality)
- Features include linguistic patterns, URL characteristics, and metadata anomalies

## Project Structure

```
.
├── email_analyzer.py      # NLP-based email content analysis
├── url_analyzer.py        # URL feature extraction
├── metadata_analyzer.py   # Email metadata analysis
├── feature_extractor.py   # Main feature engineering pipeline
├── train_model.py         # Model training script
├── predict.py             # Prediction script
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Feature Categories

### Email Content Features (20+ features)
- Character/word/sentence counts
- Phishing keyword frequency
- Text complexity metrics
- Urgency indicators
- Suspicious pattern detection

### URL Features (25+ features)
- URL structure analysis
- Domain characteristics
- Path and query parameters
- Suspicious pattern detection

### Metadata Features (20+ features)
- Email address analysis
- Domain reputation
- Header analysis
- Address mismatches

## Notes

- **Data Quality**: Model performance heavily depends on training data quality and diversity
- **Feature Engineering**: Features are designed based on common phishing tactics
- **Model Selection**: Random Forest typically works well for this task, but experiment with different models
- **Scaling**: Use `--scale` flag when training SVM or Logistic Regression models

## License

This project is provided as-is for educational and research purposes.

## Contributing

Feel free to enhance the feature extraction, add new analysis modules, or improve the model architecture.

