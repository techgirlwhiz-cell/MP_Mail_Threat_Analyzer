# Gmail Add-on Integration Guide

This guide explains how to integrate the phishing detection system as a Gmail add-on that automatically checks every incoming email.

## Overview

The Gmail add-on will:
- Automatically scan every incoming email
- Show phishing warnings in Gmail interface
- Allow users to register and authenticate
- Run predictions in the background
- Display results in Gmail sidebar

## Architecture Options

### Option 1: Google Apps Script (Easiest)

**Pros:**
- No server infrastructure needed
- Free tier available
- Easy deployment
- Direct Gmail API access

**Cons:**
- Limited Python ML model support (would need to convert to JavaScript or use API)
- Execution time limits
- Less flexible

### Option 2: Google Cloud Functions + Gmail API (Recommended)

**Pros:**
- Full Python support
- Can use existing ML models
- Scalable
- Better performance

**Cons:**
- Requires Google Cloud Platform setup
- Costs money at scale
- More complex setup

### Option 3: Hybrid Approach (Best for Production)

- **Frontend**: Gmail Add-on (Apps Script)
- **Backend**: Cloud Function or App Engine (Python)
- **ML Model**: Hosted on Cloud Functions or Cloud Run

## Implementation Steps

### Step 1: Set Up Google Cloud Project

1. **Create Google Cloud Project**
   ```bash
   # Install Google Cloud SDK
   gcloud projects create phishing-detector-addon
   gcloud config set project phishing-detector-addon
   ```

2. **Enable APIs**
   ```bash
   gcloud services enable gmail-api.googleapis.com
   gcloud services enable cloudfunctions.googleapis.com
   gcloud services enable appengine.googleapis.com
   ```

3. **Set Up OAuth 2.0**
   - Go to Google Cloud Console
   - APIs & Services > Credentials
   - Create OAuth 2.0 Client ID
   - Add authorized redirect URIs

### Step 2: Create Gmail Add-on (Apps Script)

Create a new Apps Script project for the Gmail add-on:

```javascript
// appsscript.json (manifest)
{
  "timeZone": "America/New_York",
  "dependencies": {
    "enabledAdvancedServices": [{
      "userSymbol": "Gmail",
      "version": "v1",
      "serviceId": "gmail"
    }]
  },
  "oauthScopes": [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify"
  ],
  "gmail": {
    "name": "Phishing Detector",
    "logoUrl": "https://your-domain.com/logo.png",
    "contextualTriggers": [{
      "unconditional": {}
    }],
    "openLinkUrlPrefixes": [
      "https://your-api-domain.com"
    ]
  }
}
```

```javascript
// Code.gs
function onGmailMessage(e) {
  // Get current email
  const messageId = e.gmail.messageId;
  const accessToken = e.gmail.accessToken;
  GmailApp.setCurrentMessageAccessToken(accessToken);
  
  const message = GmailApp.getMessageById(messageId);
  const subject = message.getSubject();
  const body = message.getPlainBody();
  const from = message.getFrom();
  
  // Call your ML API
  const prediction = checkPhishing(subject, body, from);
  
  // Create card with results
  return createPhishingCard(prediction);
}

function checkPhishing(subject, body, from) {
  // Call your Cloud Function API
  const apiUrl = 'https://your-region-your-project.cloudfunctions.net/predict';
  
  const payload = {
    email_body: body,
    email_subject: subject,
    from_address: from
  };
  
  const options = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload),
    headers: {
      'Authorization': 'Bearer ' + getAccessToken()
    }
  };
  
  const response = UrlFetchApp.fetch(apiUrl, options);
  return JSON.parse(response.getContentText());
}

function createPhishingCard(prediction) {
  const isPhishing = prediction.is_phishing === 1;
  const color = isPhishing ? '#EF4444' : '#10B981';
  const icon = isPhishing ? '🔴' : '🟢';
  
  return CardService.newCardBuilder()
    .setHeader(CardService.newCardHeader()
      .setTitle(`${icon} Phishing Detection Result`)
      .setSubtitle(`Confidence: ${(prediction.confidence * 100).toFixed(1)}%`))
    .addSection(CardService.newCardSection()
      .setHeader('Result')
      .addWidget(CardService.newTextParagraph()
        .setText(`This email is ${isPhishing ? 'LIKELY PHISHING' : 'LEGITIMATE'}`)))
    .build();
}
```

### Step 3: Deploy ML Model as Cloud Function

Create a Cloud Function to host your Python ML model:

```python
# main.py (Cloud Function)
import functions_framework
import joblib
import pandas as pd
from feature_extractor import FeatureExtractor
import os

# Load model (uploaded with function)
model = None
feature_extractor = None

def load_model():
    global model, feature_extractor
    if model is None:
        # Load from Cloud Storage or bundled with function
        model = joblib.load('model.pkl')
        feature_extractor = model.get('feature_extractor', FeatureExtractor())

@functions_framework.http
def predict(request):
    """HTTP Cloud Function to predict phishing."""
    load_model()
    
    request_json = request.get_json(silent=True)
    
    if not request_json:
        return {'error': 'No data provided'}, 400
    
    # Extract features
    email_data = {
        'email_body': request_json.get('email_body', ''),
        'email_subject': request_json.get('email_subject', ''),
        'from_address': request_json.get('from_address', ''),
    }
    
    features = feature_extractor.extract_features(email_data)
    features_df = pd.DataFrame([features])
    
    # Ensure feature order
    feature_names = model.get('feature_names')
    if feature_names:
        for col in feature_names:
            if col not in features_df.columns:
                features_df[col] = 0
        features_df = features_df[feature_names]
    
    features_df = features_df.fillna(0)
    
    # Scale if needed
    scaler = model.get('scaler')
    if scaler:
        features_df = pd.DataFrame(scaler.transform(features_df), columns=features_df.columns)
    
    # Predict
    ml_model = model['model']
    prediction = ml_model.predict(features_df)[0]
    probability = ml_model.predict_proba(features_df)[0][1] if hasattr(ml_model, 'predict_proba') else None
    
    return {
        'is_phishing': int(prediction),
        'label': 'Phishing' if prediction == 1 else 'Legitimate',
        'confidence': float(probability) if probability is not None else None
    }
```

**Deploy Cloud Function:**
```bash
gcloud functions deploy predict \
  --runtime python39 \
  --trigger-http \
  --allow-unauthenticated \
  --source . \
  --entry-point predict
```

### Step 4: Set Up User Registration

Create a user registration system:

```python
# user_registration.py (Cloud Function)
import functions_framework
from user_auth import UserAuth
import firebase_admin
from firebase_admin import firestore

db = firestore.client()
auth = UserAuth()

@functions_framework.http
def register_user(request):
    """Register new user for Gmail add-on."""
    request_json = request.get_json(silent=True)
    
    username = request_json.get('username')
    email = request_json.get('email')
    password = request_json.get('password')
    gmail_address = request_json.get('gmail_address')
    
    # Register user
    success, message = auth.register(username, password, email)
    
    if success:
        # Store Gmail address
        db.collection('users').document(username).set({
            'gmail_address': gmail_address,
            'registered_at': firestore.SERVER_TIMESTAMP,
            'active': True
        })
    
    return {'success': success, 'message': message}
```

### Step 5: Gmail Push Notifications (Auto-check Emails)

Set up Gmail push notifications to automatically check incoming emails:

```python
# gmail_watcher.py (Cloud Function)
import functions_framework
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import base64
import json

@functions_framework.http
def watch_gmail(request):
    """Set up Gmail watch for user."""
    request_json = request.get_json(silent=True)
    
    user_id = request_json.get('user_id')
    access_token = request_json.get('access_token')
    
    credentials = Credentials(token=access_token)
    service = build('gmail', 'v1', credentials=credentials)
    
    # Set up watch
    watch_request = {
        'topicName': 'projects/your-project/topics/gmail-notifications',
        'labelIds': ['INBOX']
    }
    
    result = service.users().watch(userId='me', body=watch_request).execute()
    
    return {'historyId': result.get('historyId')}
```

### Step 6: Pub/Sub Handler (Process Incoming Emails)

```python
# email_processor.py (Cloud Function)
import functions_framework
from google.cloud import pubsub_v1
import base64
import json

@functions_framework.cloud_event
def process_email(cloud_event):
    """Process incoming email from Pub/Sub."""
    # Decode message
    message_data = base64.b64decode(cloud_event.data['message']['data'])
    email_info = json.loads(message_data)
    
    # Get email details
    user_id = email_info['emailAddress']
    history_id = email_info['historyId']
    
    # Fetch new emails
    # Check each email with ML model
    # Store results
    # Send notification if phishing detected
    
    return 'OK'
```

## Deployment Checklist

- [ ] Create Google Cloud Project
- [ ] Enable required APIs
- [ ] Set up OAuth 2.0 credentials
- [ ] Deploy ML model as Cloud Function
- [ ] Create Gmail Add-on (Apps Script)
- [ ] Set up user registration system
- [ ] Configure Gmail push notifications
- [ ] Set up Pub/Sub for email processing
- [ ] Test end-to-end flow
- [ ] Submit to Gmail Add-on store

## Security Considerations

1. **Authentication**: Use OAuth 2.0 for Gmail access
2. **API Keys**: Store securely in Google Secret Manager
3. **Rate Limiting**: Implement to prevent abuse
4. **Data Privacy**: Don't store email content, only predictions
5. **User Consent**: Clear privacy policy and terms

## Cost Estimation

- **Cloud Functions**: ~$0.40 per million invocations
- **Gmail API**: Free tier: 1 billion quota units/day
- **Storage**: Minimal for user data
- **Total**: ~$5-20/month for small scale

## Next Steps

1. Set up Google Cloud Project
2. Deploy ML model as Cloud Function
3. Create Gmail Add-on manifest
4. Implement user registration
5. Test with your Gmail account
6. Submit for review

## Resources

- [Gmail Add-on Documentation](https://developers.google.com/gmail/add-ons)
- [Google Cloud Functions](https://cloud.google.com/functions)
- [Gmail API](https://developers.google.com/gmail/api)
- [Apps Script](https://developers.google.com/apps-script)

## Support

For implementation help, refer to the example code in the `gmail_addon/` directory.

