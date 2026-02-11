"""
Metadata Analyzer
Extracts features from email metadata (headers, structure, etc.)
"""

import re
from email.utils import parseaddr
import numpy as np


class MetadataAnalyzer:
    """Analyzes email metadata to extract phishing-related features."""
    
    def __init__(self):
        # Common email providers
        self.trusted_providers = ['gmail.com', 'outlook.com', 'yahoo.com', 'aol.com',
                                 'icloud.com', 'protonmail.com', 'hotmail.com']
    
    def extract_features(self, from_address, to_address="", reply_to="", 
                        subject="", headers=None):
        """
        Extract features from email metadata.
        
        Args:
            from_address: Sender email address
            to_address: Recipient email address
            reply_to: Reply-to address
            subject: Email subject
            headers: Dictionary of email headers (optional)
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        # From address features
        from_features = self._extract_address_features(from_address)
        features.update({f'from_{k}': v for k, v in from_features.items()})
        
        # Reply-to features
        reply_features = self._extract_address_features(reply_to) if reply_to else {}
        features.update({f'reply_to_{k}': v for k, v in reply_features.items()})
        
        # Address mismatch features
        mismatch_features = self._extract_mismatch_features(from_address, reply_to)
        features.update(mismatch_features)
        
        # Subject features
        subject_features = self._extract_subject_features(subject)
        features.update(subject_features)
        
        # Header features (if provided)
        if headers:
            header_features = self._extract_header_features(headers)
            features.update(header_features)
        
        return features
    
    def _extract_address_features(self, email_address):
        """Extract features from an email address."""
        features = {
            'address_length': 0,
            'local_part_length': 0,
            'domain_length': 0,
            'has_plus': 0,
            'has_dots': 0,
            'has_numbers': 0,
            'has_hyphens': 0,
            'has_underscores': 0,
            'is_trusted_provider': 0,
            'num_subdomains': 0,
            'suspicious_pattern': 0,
        }
        
        if not email_address:
            return features
        
        # Parse email address
        name, addr = parseaddr(email_address)
        if not addr:
            addr = email_address
        
        if '@' not in addr:
            return features
        
        local_part, domain = addr.split('@', 1)
        
        # Basic length features
        features['address_length'] = len(addr)
        features['local_part_length'] = len(local_part)
        features['domain_length'] = len(domain)
        
        # Character features
        features['has_plus'] = 1 if '+' in local_part else 0
        features['has_dots'] = 1 if '.' in local_part else 0
        features['has_numbers'] = 1 if any(c.isdigit() for c in local_part) else 0
        features['has_hyphens'] = 1 if '-' in local_part or '-' in domain else 0
        features['has_underscores'] = 1 if '_' in local_part else 0
        
        # Domain features
        features['is_trusted_provider'] = 1 if domain.lower() in self.trusted_providers else 0
        
        # Subdomain count
        subdomain_parts = domain.split('.')
        features['num_subdomains'] = max(0, len(subdomain_parts) - 2)  # Subtract domain and TLD
        
        # Suspicious patterns (random-looking local parts)
        if len(local_part) > 10:
            # Check for high randomness (many different characters)
            unique_chars = len(set(local_part))
            if unique_chars / len(local_part) > 0.7:  # More than 70% unique characters
                features['suspicious_pattern'] = 1
        
        return features
    
    def _extract_mismatch_features(self, from_address, reply_to):
        """Extract features related to address mismatches."""
        features = {
            'reply_to_mismatch': 0,
            'reply_to_empty': 0,
        }
        
        if not reply_to:
            features['reply_to_empty'] = 1
            return features
        
        # Extract domains
        _, from_addr = parseaddr(from_address)
        _, reply_addr = parseaddr(reply_to)
        
        if '@' in from_addr and '@' in reply_addr:
            from_domain = from_addr.split('@', 1)[1].lower()
            reply_domain = reply_addr.split('@', 1)[1].lower()
            
            if from_domain != reply_domain:
                features['reply_to_mismatch'] = 1
        
        return features
    
    def _extract_subject_features(self, subject):
        """Extract features from email subject."""
        features = {
            'subject_length': 0,
            'subject_word_count': 0,
            'subject_has_urgency': 0,
            'subject_has_question': 0,
            'subject_has_exclamation': 0,
            'subject_all_caps': 0,
            'subject_suspicious_words': 0,
        }
        
        if not subject:
            return features
        
        features['subject_length'] = len(subject)
        features['subject_word_count'] = len(subject.split())
        
        # Urgency indicators
        urgency_words = ['urgent', 'immediate', 'asap', 'important', 'action required', 'verify']
        subject_lower = subject.lower()
        features['subject_has_urgency'] = 1 if any(word in subject_lower for word in urgency_words) else 0
        
        # Punctuation
        features['subject_has_question'] = 1 if '?' in subject else 0
        features['subject_has_exclamation'] = 1 if '!' in subject else 0
        
        # All caps check
        if subject.isupper() and len(subject.split()) > 2:
            features['subject_all_caps'] = 1
        
        # Suspicious words
        suspicious_words = ['verify', 'confirm', 'update', 'suspended', 'locked', 'expire']
        features['subject_suspicious_words'] = sum(1 for word in suspicious_words if word in subject_lower)
        
        return features
    
    def _extract_header_features(self, headers):
        """Extract features from email headers."""
        features = {
            'has_spf': 0,
            'has_dkim': 0,
            'has_dmarc': 0,
            'has_mime_version': 0,
            'has_content_type': 0,
            'num_headers': 0,
        }
        
        if not headers:
            return features
        
        header_keys = [k.lower() for k in headers.keys()] if isinstance(headers, dict) else []
        
        # Security headers
        features['has_spf'] = 1 if any('spf' in k for k in header_keys) else 0
        features['has_dkim'] = 1 if any('dkim' in k for k in header_keys) else 0
        features['has_dmarc'] = 1 if any('dmarc' in k for k in header_keys) else 0
        
        # Content headers
        features['has_mime_version'] = 1 if any('mime-version' in k for k in header_keys) else 0
        features['has_content_type'] = 1 if any('content-type' in k for k in header_keys) else 0
        
        # Header count
        features['num_headers'] = len(header_keys)
        
        return features

