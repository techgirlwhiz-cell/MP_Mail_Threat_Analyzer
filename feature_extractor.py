"""
Main Feature Extractor
Combines features from email content, URLs, and metadata.
"""

import pandas as pd
from email_analyzer import EmailAnalyzer
from url_analyzer import URLAnalyzer
from metadata_analyzer import MetadataAnalyzer
import re

try:
    from semantic_analyzer import extract_features as semantic_extract_features
except ImportError:
    semantic_extract_features = None
try:
    from grammar_analyzer import extract_features as grammar_extract_features
except ImportError:
    grammar_extract_features = None
try:
    from linguistic_consistency import extract_features as linguistic_extract_features
except ImportError:
    linguistic_extract_features = None
try:
    from behavioral_extractor import extract_features as behavioral_extract_features
except ImportError:
    behavioral_extract_features = None


def _get_body_subject(email_data):
    """Normalize body/subject from either email_body/email_subject or body/subject."""
    body = email_data.get('email_body') or email_data.get('body', '')
    subject = email_data.get('email_subject') or email_data.get('subject', '')
    return body, subject


class FeatureExtractor:
    """Main feature extractor that combines all analysis modules."""
    
    def __init__(self):
        self.email_analyzer = EmailAnalyzer()
        self.url_analyzer = URLAnalyzer()
        self.metadata_analyzer = MetadataAnalyzer()
    
    def extract_features(self, email_data):
        """
        Extract all features from email data.
        
        Args:
            email_data: Dictionary or pandas Series with keys:
                - 'email_body' or 'body': Email body text
                - 'email_subject' or 'subject': Email subject
                - 'from_address' or 'sender': Sender email address
                - 'to_address': Recipient email address (optional)
                - 'reply_to': Reply-to address (optional)
                - 'urls': List of URLs or single URL string (optional)
                - 'headers': Dictionary of email headers (optional)
                
        Returns:
            Dictionary of all extracted features
        """
        body, subject = _get_body_subject(email_data)
        from_address = email_data.get('from_address') or email_data.get('sender', '')
        
        # Extract URLs from email body if not provided
        urls = email_data.get('urls', [])
        if not urls:
            urls = self._extract_urls_from_text(body)
        
        # Extract email content features
        email_features = self.email_analyzer.extract_features(body, subject)
        
        # Semantic features (optional)
        if semantic_extract_features is not None:
            try:
                semantic_features = semantic_extract_features(subject, body)
                email_features.update(semantic_features)
            except Exception:
                pass
        
        # Grammar/spelling anomaly (optional)
        if grammar_extract_features is not None:
            try:
                full_text = f"{subject} {body}"
                grammar_features = grammar_extract_features(full_text)
                email_features.update(grammar_features)
            except Exception:
                pass
        
        # Linguistic consistency subject vs body (optional)
        if linguistic_extract_features is not None:
            try:
                consistency_features = linguistic_extract_features(subject, body)
                email_features.update(consistency_features)
            except Exception:
                pass
        
        # Behavioral: CTA intensity, time-pressure, attachment risk (optional)
        if behavioral_extract_features is not None:
            try:
                attachments = email_data.get('attachments') or []
                behavioral_features = behavioral_extract_features(body, subject, attachments)
                email_features.update(behavioral_features)
            except Exception:
                pass
        
        # Extract metadata features
        metadata_features = self.metadata_analyzer.extract_features(
            from_address,
            email_data.get('to_address', ''),
            email_data.get('reply_to', ''),
            subject,
            email_data.get('headers')
        )
        
        # Extract URL features (aggregate if multiple URLs)
        url_features = self._extract_url_features(urls)
        
        # Combine all features
        all_features = {}
        all_features.update(email_features)
        all_features.update(metadata_features)
        all_features.update(url_features)
        
        return all_features
    
    def extract_features_batch(self, email_data_list):
        """
        Extract features from a list of emails.
        
        Args:
            email_data_list: List of email data dictionaries
            
        Returns:
            DataFrame with extracted features
        """
        features_list = []
        for email_data in email_data_list:
            features = self.extract_features(email_data)
            features_list.append(features)
        
        return pd.DataFrame(features_list)
    
    def _extract_urls_from_text(self, text):
        """Extract URLs from text."""
        if not text:
            return []
        
        # Pattern for URLs
        url_pattern = r'http[s]?://[^\s<>"\'\)]+|www\.[^\s<>"\'\)]+'
        urls = re.findall(url_pattern, text)
        return urls
    
    def _extract_url_features(self, urls):
        """Extract and aggregate URL features."""
        if not urls:
            # Return empty features with url_ prefix
            empty_features = self.url_analyzer.extract_features('')
            return {f'url_{k}': v for k, v in empty_features.items()}
        
        # Convert to list if single URL
        if isinstance(urls, str):
            urls = [urls]
        
        # Extract features for each URL
        url_feature_list = []
        for url in urls:
            features = self.url_analyzer.extract_features(url)
            url_feature_list.append(features)
        
        # Aggregate features (take max/average for multiple URLs)
        if not url_feature_list:
            empty_features = self.url_analyzer.extract_features('')
            return {f'url_{k}': v for k, v in empty_features.items()}
        
        aggregated = {}
        
        # If single URL, use individual features with url_ prefix
        if len(urls) == 1:
            for key, value in url_feature_list[0].items():
                aggregated[f'url_{key}'] = value
        else:
            # Multiple URLs: aggregate features
            for key in url_feature_list[0].keys():
                values = [f[key] for f in url_feature_list]
                
                # For counts and flags, use max
                if 'count' in key or 'has_' in key or 'is_' in key or 'num_' in key:
                    aggregated[f'url_max_{key}'] = max(values)
                    aggregated[f'url_avg_{key}'] = sum(values) / len(values) if values else 0
                # For lengths and ratios, use average
                else:
                    aggregated[f'url_avg_{key}'] = sum(values) / len(values) if values else 0
                    aggregated[f'url_max_{key}'] = max(values)
        
        # Add count of URLs
        aggregated['url_count'] = len(urls)
        
        return aggregated

