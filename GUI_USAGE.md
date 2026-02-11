# GUI Application Usage Guide

## 🎨 Desktop GUI (CustomTkinter)

The desktop app includes a login window and a main dashboard for analysis, training, and history.

## Launching the Desktop GUI

```bash
python app.py
```
Log in with your credentials, then use the dashboard tabs for analysis, model loading, and CSV upload.

## Features

### 📁 CSV File Upload
- Click the **"📤 Upload CSV File"** button to select and load your CSV file
- The CSV file should contain email data with columns:
  - `email_body` (required)
  - `email_subject` (required)
  - `from_address` (required)
  - `urls` (optional)
  - `to_address` (optional)
  - `reply_to` (optional)

### 🤖 Model Loading
- Click **"📁 Load Model (.pkl)"** to load a trained phishing detection model
- The model file should be saved from the training script (`train_model.py`)

### 🔍 Email Analysis
- Once both CSV file and model are loaded, click **"🔍 Analyze Emails"**
- The system will:
  - Extract features from each email
  - Run predictions using the loaded model
  - Display results with confidence scores
  - Show statistics (total emails, phishing count, etc.)

### 📊 Results Display
- View detailed results in the right panel
- See predictions for each email (Phishing/Legitimate)
- View confidence scores
- Statistics summary at the top

### 💾 Export Results
- Click **"💾 Export Results to CSV"** to save results
- Exports include original email data plus predictions and confidence scores

## User Interface Elements

### Header Section
- Purple gradient header with title
- Modern, clean design

### Left Panel (Controls)
- Model selection area
- CSV file upload button
- Analyze button
- Progress bar
- Status messages

### Right Panel (Results)
- Scrollable results display
- Color-coded predictions (🔴 Phishing / 🟢 Legitimate)
- Export button

## Color Scheme

- **Primary Purple**: `#8B5CF6`
- **Dark Purple**: `#6D28D9`
- **Light Purple Background**: `#F5F3FF`
- **White Panels**: `#FFFFFF`
- **Pink Accent**: `#EC4899`
- **Success Green**: `#10B981`
- **Danger Red**: `#EF4444`

## Example Workflow

1. **Launch GUI**
   ```bash
   python app.py
   ```

2. **Load Model**
   - Click "📁 Load Model (.pkl)"
   - Select your trained model file (e.g., `phishing_model.pkl`)

3. **Upload CSV**
   - Click "📤 Upload CSV File"
   - Select your CSV file with email data
   - Preview will appear in results panel

4. **Analyze**
   - Click "🔍 Analyze Emails"
   - Watch progress bar
   - Results will appear when complete

5. **Export**
   - Review results
   - Click "💾 Export Results to CSV"
   - Save to desired location

## Requirements

Make sure you have installed all dependencies:
```bash
pip install -r requirements.txt
```

The GUI uses `customtkinter` for a modern look and feel.

## Tips

- **Large CSV files**: The GUI processes emails in a background thread, so the interface remains responsive
- **Model required**: You must train a model first using `train_model.py` before using the GUI
- **CSV format**: Use `example_training_data.csv` as a template for your CSV file format

## Troubleshooting

**GUI doesn't open:**
- Make sure `customtkinter` is installed: `pip install customtkinter`
- Check that all dependencies are installed: `pip install -r requirements.txt`

**Model won't load:**
- Ensure the model file was created using `train_model.py`
- Check file path is correct

**CSV upload fails:**
- Verify CSV has required columns: `email_body`, `email_subject`, `from_address`
- Check CSV file is not corrupted
- Ensure CSV is properly formatted (comma-separated)

**No predictions:**
- Make sure both model and CSV are loaded
- Check that model was trained successfully
- Verify CSV contains valid email data

