# Quick Start Steps

## 🚀 Run This Code in 5 Steps

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

**Windows Note**: If `python` doesn't work, try `py` or `python3`

### Step 1.5: Download NLTK Data (Important!)
```bash
python setup_nltk.py
```

This downloads required language data. **You only need to run this once.**

---

### Step 2: Test the System (Optional)
```bash
python quick_test.py
```
This verifies everything works by extracting features from example emails.

---

### Step 3: Prepare Your Training Data

Create a CSV file with your emails. Minimum required columns:

| email_body | email_subject | from_address | label |
|------------|---------------|--------------|-------|
| "Email text here..." | "Subject line" | "sender@example.com" | 1 or 0 |

- **label**: `1` = phishing, `0` = legitimate
- See `example_training_data.csv` for a complete example

---

### Step 4: Train the Model

**Basic command:**
```bash
python train_model.py --data your_data.csv --output model.pkl
```

**With more options:**
```bash
python train_model.py --data your_data.csv --output model.pkl --model-type random_forest --test-size 0.2
```

**What happens:**
- ✅ Extracts features from emails
- ✅ Trains the model
- ✅ Shows accuracy and metrics
- ✅ Saves model to `model.pkl`

---

### Step 5: Make Predictions

**For a single email:**

1. Create `email.json`:
```json
{
  "email_body": "Verify your account now!",
  "email_subject": "Urgent: Account Verification",
  "from_address": "security@example.com",
  "urls": "http://verify.example.com"
}
```

2. Run:
```bash
python predict.py --model model.pkl --email email.json
```

**For multiple emails (batch):**

```bash
python predict.py --model model.pkl --batch emails.csv --output results.csv
```

---

## 📋 Command Reference

### Training
```bash
python train_model.py --data <CSV_FILE> [OPTIONS]

Options:
  --output <FILE>          Output model file (default: phishing_model.pkl)
  --model-type <TYPE>      random_forest, gradient_boosting, logistic_regression, svm
  --test-size <FLOAT>      Test set size 0.0-1.0 (default: 0.2)
  --scale                  Scale features (recommended for SVM/LogisticRegression)
```

### Prediction
```bash
# Single email
python predict.py --model <MODEL_FILE> --email <JSON_FILE>

# Batch prediction
python predict.py --model <MODEL_FILE> --batch <CSV_FILE> --output <OUTPUT_CSV>
```

---

## 🆘 Troubleshooting

**Problem**: `python: command not found`
- **Solution**: Use `py` (Windows) or `python3` (Mac/Linux)

**Problem**: `ModuleNotFoundError`
- **Solution**: Run `pip install -r requirements.txt`

**Problem**: `LookupError: Resource punkt_tab not found`
- **Solution**: Run the setup script to download NLTK data:
  ```bash
  python setup_nltk.py
  ```
  Or manually download in Python:
  ```python
  import nltk
  nltk.download('punkt')
  nltk.download('punkt_tab')  # Required for newer NLTK versions
  nltk.download('stopwords')
  ```

**Problem**: Poor model accuracy
- **Solution**: 
  - Use more training data (100+ emails recommended)
  - Ensure balanced dataset (similar number of phishing and legitimate emails)
  - Try different model types with `--model-type`

---

## 📝 Example Workflow

### Command Line Workflow

```bash
# 1. Install
pip install -r requirements.txt

# 2. Test
python quick_test.py

# 3. Train (using example data)
python train_model.py --data example_training_data.csv --output my_model.pkl

# 4. Predict
python predict.py --model my_model.pkl --email example_email.json
```

### GUI Workflow (Easier!)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Train model (one time)
python train_model.py --data example_training_data.csv --output my_model.pkl

# 3. Run the app (choose one)
#    Web:  python web_backend.py   then open http://localhost:5001/login.html
#    Desktop:  python app.py
```

That's it! 🎉

