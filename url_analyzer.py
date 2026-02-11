"""
URL Analyzer
Extracts features from URLs to detect phishing attempts.
Includes WHOIS-based domain age, brand impersonation, and deceptive security indicators.
"""

import re
import time
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs
import numpy as np
import tldextract

# Optional WHOIS (with cache and timeout)
_whois_cache = {}
_WHOIS_CACHE_TTL = 86400  # 24 hours
_WHOIS_TIMEOUT = 3

try:
    import whois
except ImportError:
    whois = None

# Brand impersonation: brand name -> canonical domain (without TLD for matching)
BRAND_CANONICAL = {
    'paypal': 'paypal',
    'amazon': 'amazon',
    'microsoft': 'microsoft',
    'apple': 'apple',
    'google': 'google',
    'facebook': 'facebook',
    'netflix': 'netflix',
    'bankofamerica': 'bankofamerica',
    'chase': 'chase',
    'wellsfargo': 'wellsfargo',
    'ebay': 'ebay',
    'linkedin': 'linkedin',
    'twitter': 'twitter',
    'x.com': 'x',
    'instagram': 'instagram',
    'dropbox': 'dropbox',
    'adobe': 'adobe',
    'dhl': 'dhl',
    'fedex': 'fedex',
    'ups': 'ups',
}
SECURE_DECEPTIVE_WORDS = ['secure', 'safe', 'verified', 'official', 'ssl', 'trusted']


class URLAnalyzer:
    """Analyzes URLs to extract phishing-related features."""
    
    def __init__(self):
        # Common phishing domains and suspicious TLDs
        self.suspicious_tlds = ['tk', 'ml', 'ga', 'cf', 'gq', 'xyz', 'top', 'click']
        self.trusted_domains = ['google', 'microsoft', 'amazon', 'paypal', 'apple', 'facebook',
                               'twitter', 'linkedin', 'github', 'stackoverflow']
    
    def extract_features(self, url):
        """
        Extract features from a URL.
        
        Args:
            url: The URL string to analyze
            
        Returns:
            Dictionary of extracted features
        """
        if not url or url == '':
            return self._empty_features()
        
        # Parse URL
        parsed = urlparse(url)
        extracted = tldextract.extract(url)
        
        features = {}
        
        # Basic URL features
        features['url_length'] = len(url)
        features['domain_length'] = len(extracted.domain)
        features['path_length'] = len(parsed.path)
        features['query_length'] = len(parsed.query)
        
        # Component counts
        features['num_dots'] = url.count('.')
        features['num_hyphens'] = url.count('-')
        features['num_underscores'] = url.count('_')
        features['num_slashes'] = url.count('/')
        features['num_question_marks'] = url.count('?')
        features['num_equals'] = url.count('=')
        features['num_ampersands'] = url.count('&')
        features['num_percent'] = url.count('%')
        
        # URL structure features
        features['has_https'] = 1 if parsed.scheme == 'https' else 0
        features['has_port'] = 1 if parsed.port is not None else 0
        features['has_path'] = 1 if parsed.path and parsed.path != '/' else 0
        features['has_query'] = 1 if parsed.query else 0
        features['has_fragment'] = 1 if parsed.fragment else 0
        
        # Domain features
        domain_features = self._extract_domain_features(extracted, parsed)
        features.update(domain_features)
        
        # Path features
        path_features = self._extract_path_features(parsed.path)
        features.update(path_features)
        
        # Query features
        query_features = self._extract_query_features(parsed.query)
        features.update(query_features)
        
        # Suspicious pattern features
        suspicious_features = self._extract_suspicious_patterns(url)
        features.update(suspicious_features)
        
        # WHOIS-based domain age and registration recency
        whois_features = self._extract_whois_features(extracted, url)
        features.update(whois_features)
        
        # Brand impersonation
        features['brand_impersonation'] = self._check_brand_impersonation(extracted, url)
        
        # Deceptive security: HTTPS + suspicious, and "secure" language in path/query
        features['has_https_but_suspicious'] = 1 if (
            features.get('has_https', 0) == 1 and
            (features.get('is_suspicious_tld', 0) == 1 or features.get('has_ip_address', 0) == 1)
        ) else 0
        path_query = ((parsed.path or '') + ' ' + (parsed.query or '')).lower()
        features['deceptive_secure_language'] = 1 if any(
            w in path_query for w in SECURE_DECEPTIVE_WORDS
        ) else 0
        
        return features
    
    def _extract_whois_features(self, extracted, url):
        """Domain age and recent update from WHOIS (cached, with timeout)."""
        features = {'domain_age_days': 0, 'domain_recently_updated': 0}
        domain = (extracted.domain or '') + '.' + (extracted.suffix or '')
        if not domain or extracted.suffix in ('', 'local'):
            return features
        cache_key = domain.lower()
        now = time.time()
        if cache_key in _whois_cache:
            entry = _whois_cache[cache_key]
            if now - entry['ts'] < _WHOIS_CACHE_TTL:
                features['domain_age_days'] = entry.get('age_days', 0)
                features['domain_recently_updated'] = entry.get('recently_updated', 0)
                return features
        if whois is None:
            return features
        try:
            from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
            with ThreadPoolExecutor(max_workers=1) as ex:
                fut = ex.submit(whois.whois, domain)
                w = fut.result(timeout=_WHOIS_TIMEOUT)
        except Exception:
            _whois_cache[cache_key] = {'ts': now, 'age_days': 0, 'recently_updated': 0}
            return features
        age_days = 0
        recently_updated = 0
        try:
            creation = w.creation_date
            if creation:
                if isinstance(creation, list):
                    creation = creation[0]
                if creation.tzinfo is None:
                    creation = creation.replace(tzinfo=timezone.utc)
                age_days = max(0, (datetime.now(timezone.utc) - creation).days)
            updated = w.updated_date
            if updated:
                if isinstance(updated, list):
                    updated = updated[0]
                if updated.tzinfo is None:
                    updated = updated.replace(tzinfo=timezone.utc)
                if (datetime.now(timezone.utc) - updated).days <= 90:
                    recently_updated = 1
        except Exception:
            pass
        _whois_cache[cache_key] = {'ts': now, 'age_days': age_days, 'recently_updated': recently_updated}
        features['domain_age_days'] = age_days
        features['domain_recently_updated'] = recently_updated
        return features
    
    def _check_brand_impersonation(self, extracted, url):
        """Return 1 if URL contains a known brand name but second-level domain is not the canonical one."""
        domain_lower = (extracted.domain or '').lower()
        url_lower = url.lower()
        for brand, canonical in BRAND_CANONICAL.items():
            if brand not in url_lower:
                continue
            # URL mentions brand but the registered domain is not the official brand domain
            if domain_lower != canonical:
                return 1
        return 0
    
    def _empty_features(self):
        """Return empty feature dictionary for missing URLs."""
        return {
            'url_length': 0,
            'domain_length': 0,
            'path_length': 0,
            'query_length': 0,
            'num_dots': 0,
            'num_hyphens': 0,
            'num_underscores': 0,
            'num_slashes': 0,
            'num_question_marks': 0,
            'num_equals': 0,
            'num_ampersands': 0,
            'num_percent': 0,
            'has_https': 0,
            'has_port': 0,
            'has_path': 0,
            'has_query': 0,
            'has_fragment': 0,
            'is_suspicious_tld': 0,
            'domain_entropy': 0,
            'has_ip_address': 0,
            'num_subdomains': 0,
            'path_entropy': 0,
            'num_path_segments': 0,
            'has_suspicious_path': 0,
            'num_query_params': 0,
            'has_suspicious_query': 0,
            'shortened_url': 0,
            'has_typosquatting': 0,
            'domain_age_days': 0,
            'domain_recently_updated': 0,
            'brand_impersonation': 0,
            'has_https_but_suspicious': 0,
            'deceptive_secure_language': 0,
        }
    
    def _extract_domain_features(self, extracted, parsed):
        """Extract features related to the domain."""
        features = {}
        
        # TLD features
        features['is_suspicious_tld'] = 1 if extracted.suffix.lower() in self.suspicious_tlds else 0
        
        # Domain entropy (randomness indicator)
        domain = extracted.domain
        if domain:
            char_counts = {}
            for char in domain:
                char_counts[char] = char_counts.get(char, 0) + 1
            entropy = -sum((count / len(domain)) * np.log2(count / len(domain)) 
                          for count in char_counts.values()) if domain else 0
            features['domain_entropy'] = entropy
        else:
            features['domain_entropy'] = 0
        
        # Check if domain is an IP address
        features['has_ip_address'] = 1 if self._is_ip_address(domain) else 0
        
        # Subdomain count
        subdomain = extracted.subdomain
        features['num_subdomains'] = len([s for s in subdomain.split('.') if s]) if subdomain else 0
        
        return features
    
    def _extract_path_features(self, path):
        """Extract features from URL path."""
        features = {}
        
        if not path or path == '/':
            features['path_entropy'] = 0
            features['num_path_segments'] = 0
            features['has_suspicious_path'] = 0
            return features
        
        # Path entropy
        path_text = path.replace('/', '').replace('-', '').replace('_', '')
        if path_text:
            char_counts = {}
            for char in path_text:
                char_counts[char] = char_counts.get(char, 0) + 1
            entropy = -sum((count / len(path_text)) * np.log2(count / len(path_text))
                          for count in char_counts.values()) if path_text else 0
            features['path_entropy'] = entropy
        else:
            features['path_entropy'] = 0
        
        # Number of path segments
        segments = [s for s in path.split('/') if s]
        features['num_path_segments'] = len(segments)
        
        # Suspicious path patterns
        suspicious_patterns = ['login', 'verify', 'account', 'confirm', 'update', 'secure']
        path_lower = path.lower()
        features['has_suspicious_path'] = 1 if any(pattern in path_lower for pattern in suspicious_patterns) else 0
        
        return features
    
    def _extract_query_features(self, query):
        """Extract features from URL query parameters."""
        features = {}
        
        if not query:
            features['num_query_params'] = 0
            features['has_suspicious_query'] = 0
            return features
        
        # Number of query parameters
        params = parse_qs(query)
        features['num_query_params'] = len(params)
        
        # Suspicious query parameter names
        suspicious_params = ['token', 'key', 'id', 'user', 'pass', 'password', 'login', 'auth']
        query_lower = query.lower()
        features['has_suspicious_query'] = 1 if any(param in query_lower for param in suspicious_params) else 0
        
        return features
    
    def _extract_suspicious_patterns(self, url):
        """Extract features related to suspicious URL patterns."""
        features = {}
        
        # Check for URL shorteners
        shorteners = ['bit.ly', 'tinyurl', 't.co', 'goo.gl', 'ow.ly', 'short.link']
        url_lower = url.lower()
        features['shortened_url'] = 1 if any(shortener in url_lower for shortener in shorteners) else 0
        
        # Check for typosquatting (common typos in domain names)
        # This is a simplified check - could be enhanced with fuzzy matching
        features['has_typosquatting'] = 0  # Placeholder - would need domain comparison
        
        return features
    
    def _is_ip_address(self, domain):
        """Check if domain is an IP address."""
        ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        if re.match(ip_pattern, domain):
            parts = domain.split('.')
            return all(0 <= int(part) <= 255 for part in parts)
        return False

