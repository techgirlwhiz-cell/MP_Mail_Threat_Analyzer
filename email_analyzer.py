"""
Email Content Analyzer
Extracts NLP-based features from email content to detect phishing attempts.
"""

import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer
from bs4 import BeautifulSoup
import numpy as np

# Download required NLTK data
def _download_nltk_data():
    """Download required NLTK resources."""
    resources_to_download = []
    
    # Check and download punkt
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        resources_to_download.append('punkt')
    
    # Check and download punkt_tab (required in newer NLTK versions)
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        resources_to_download.append('punkt_tab')
    
    # Check and download stopwords
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        resources_to_download.append('stopwords')
    
    # Download missing resources
    for resource in resources_to_download:
        try:
            nltk.download(resource, quiet=True)
        except Exception as e:
            # If download fails, continue - might work at runtime
            pass

# Download NLTK data on import
_download_nltk_data()


class EmailAnalyzer:
    """Analyzes email content using NLP techniques to extract phishing-related features."""
    
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        
        # Phishing-related keywords
        self.phishing_keywords = [
            'urgent', 'verify', 'suspend', 'account', 'click', 'login', 'confirm',
            'update', 'password', 'security', 'bank', 'paypal', 'amazon', 'ebay',
            'irs', 'tax', 'suspended', 'locked', 'expire', 'immediately', 'action required',
            'verify your account', 'click here', 'verify now', 'limited time', 'act now'
        ]
        
        # Suspicious patterns
        self.suspicious_patterns = [
            r'http[s]?://[^\s]+',  # URLs
            r'www\.[^\s]+',  # www links
            r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',  # IP addresses
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # Email addresses
        ]
    
    def extract_features(self, email_body, email_subject=""):
        """
        Extract NLP features from email content.
        
        Args:
            email_body: The email body text
            email_subject: The email subject line
            
        Returns:
            Dictionary of extracted features
        """
        # Combine subject and body
        full_text = f"{email_subject} {email_body}".lower()
        
        # Remove HTML tags if present
        text = self._remove_html(full_text)
        
        # Extract features
        features = {}
        
        # Basic text statistics
        features['char_count'] = len(text)
        features['word_count'] = len(text.split())
        
        # Try to tokenize sentences, with fallback if NLTK resources are missing
        try:
            features['sentence_count'] = len(sent_tokenize(text))
        except LookupError:
            # Fallback: approximate sentence count by counting sentence-ending punctuation
            features['sentence_count'] = max(1, text.count('.') + text.count('!') + text.count('?'))
        except Exception:
            features['sentence_count'] = 1  # Default to 1 if all else fails
        
        features['avg_word_length'] = np.mean([len(word) for word in text.split()]) if text.split() else 0
        features['avg_sentence_length'] = features['word_count'] / features['sentence_count'] if features['sentence_count'] > 0 else 0
        
        # Uppercase ratio
        features['uppercase_ratio'] = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        
        # Special character ratio
        features['special_char_ratio'] = sum(1 for c in text if not c.isalnum() and not c.isspace()) / len(text) if text else 0
        
        # Phishing keyword features
        keyword_features = self._extract_keyword_features(text)
        features.update(keyword_features)
        
        # Suspicious pattern features
        pattern_features = self._extract_pattern_features(text)
        features.update(pattern_features)
        
        # Language complexity features
        complexity_features = self._extract_complexity_features(text)
        features.update(complexity_features)
        
        # Emotional urgency features
        urgency_features = self._extract_urgency_features(text)
        features.update(urgency_features)
        
        return features
    
    def _remove_html(self, text):
        """Remove HTML tags from text."""
        soup = BeautifulSoup(text, 'html.parser')
        return soup.get_text()
    
    def _extract_keyword_features(self, text):
        """Extract features related to phishing keywords."""
        features = {}
        
        # Count phishing keywords
        text_lower = text.lower()
        keyword_count = sum(1 for keyword in self.phishing_keywords if keyword in text_lower)
        features['phishing_keyword_count'] = keyword_count
        features['phishing_keyword_ratio'] = keyword_count / len(text.split()) if text.split() else 0
        
        # Check for specific high-risk phrases
        high_risk_phrases = [
            'verify your account', 'click here', 'verify now', 'account suspended',
            'password expired', 'update payment', 'confirm your identity'
        ]
        features['high_risk_phrase_count'] = sum(1 for phrase in high_risk_phrases if phrase in text_lower)
        
        return features
    
    def _extract_pattern_features(self, text):
        """Extract features related to suspicious patterns."""
        features = {}
        
        # Count URLs
        url_pattern = r'http[s]?://[^\s]+|www\.[^\s]+'
        urls = re.findall(url_pattern, text)
        features['url_count'] = len(urls)
        
        # Count IP addresses
        ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        ips = re.findall(ip_pattern, text)
        features['ip_address_count'] = len(ips)
        
        # Count email addresses
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        features['email_address_count'] = len(emails)
        
        # Has URL
        features['has_url'] = 1 if features['url_count'] > 0 else 0
        features['has_ip'] = 1 if features['ip_address_count'] > 0 else 0
        
        return features
    
    def _extract_complexity_features(self, text):
        """Extract features related to text complexity."""
        features = {}
        
        # Try to tokenize, with fallback if NLTK resources are missing
        try:
            tokens = word_tokenize(text.lower())
        except (LookupError, Exception):
            # Fallback: simple word splitting
            tokens = text.lower().split()
        
        tokens = [t for t in tokens if t.isalpha() and t not in self.stop_words]
        
        # Vocabulary richness (unique words / total words)
        if len(tokens) > 0:
            unique_words = len(set(tokens))
            features['vocabulary_richness'] = unique_words / len(tokens)
        else:
            features['vocabulary_richness'] = 0
        
        # Most common word frequency (indicator of template/repetitive text)
        if tokens:
            word_freq = {}
            for token in tokens:
                word_freq[token] = word_freq.get(token, 0) + 1
            features['max_word_frequency'] = max(word_freq.values()) if word_freq else 0
            features['max_word_frequency_ratio'] = features['max_word_frequency'] / len(tokens) if tokens else 0
        else:
            features['max_word_frequency'] = 0
            features['max_word_frequency_ratio'] = 0
        
        return features
    
    def _extract_urgency_features(self, text):
        """Extract features related to urgency and emotional manipulation."""
        features = {}
        
        urgency_words = ['urgent', 'immediate', 'asap', 'now', 'today', 'expire', 'expired',
                        'suspended', 'locked', 'verify', 'confirm', 'update', 'action required']
        
        text_lower = text.lower()
        urgency_count = sum(1 for word in urgency_words if word in text_lower)
        features['urgency_word_count'] = urgency_count
        features['urgency_word_ratio'] = urgency_count / len(text.split()) if text.split() else 0
        
        # Exclamation and question marks
        features['exclamation_count'] = text.count('!')
        features['question_count'] = text.count('?')
        features['exclamation_ratio'] = features['exclamation_count'] / len(text) if text else 0
        
        return features

