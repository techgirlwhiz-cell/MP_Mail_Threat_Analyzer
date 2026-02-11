"""
Email Threat Detector
Core ML/NLP module for detecting email threats.
Uses full FeatureExtractor, optional SHAP explainability, risk breakdown, and suspicious spans/URLs.
"""

import os
import re
from typing import Dict, Tuple, Optional, List, Any
import numpy as np

# Try to import joblib, but continue without it if not available
try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False
    print("Note: joblib not available. Using rule-based detection only.")

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    shap = None

from email_analyzer import EmailAnalyzer
from feature_extractor import FeatureExtractor
from url_analyzer import URLAnalyzer


class EmailThreatDetector:
    """
    Advanced ML/NLP-based email threat detection system.
    Uses full feature pipeline, ensemble model when available, SHAP, and risk breakdown.
    """
    
    def __init__(self, model_path: str = 'phishing_model.pkl'):
        """
        Initialize the threat detector.
        
        Args:
            model_path: Path to the trained ML model (joblib bundle with model, feature_extractor, scaler, feature_names)
        """
        self.model_path = model_path
        self.model_bundle = self._load_model()
        self.email_analyzer = EmailAnalyzer()
        self.feature_extractor = FeatureExtractor()
        self.url_analyzer = URLAnalyzer()
        self._shap_explainer = None
        
        # Threat categories
        self.threat_categories = {
            0: 'legitimate',
            1: 'phishing',
            2: 'spam',
            3: 'malware'
        }
    
    def _load_model(self):
        """Load the trained ML model bundle (dict with model, feature_extractor, scaler, feature_names) or legacy model."""
        if not JOBLIB_AVAILABLE:
            return None
        if os.path.exists(self.model_path):
            try:
                loaded = joblib.load(self.model_path)
                # Support both bundle dict and raw model (legacy)
                if isinstance(loaded, dict) and 'model' in loaded:
                    return loaded
                return {'model': loaded, 'feature_names': None, 'scaler': None}
            except Exception as e:
                print(f"Warning: Could not load model from {self.model_path}: {e}")
                return None
        return None
    
    @property
    def model(self):
        """Return the actual classifier from the bundle for backward compatibility."""
        if self.model_bundle is None:
            return None
        return self.model_bundle.get('model')
    
    def analyze_email(self, email_data: Dict) -> Dict:
        """
        Analyze an email for threats. Returns threat_score, risk_factors, risk_breakdown, suspicious_spans, suspicious_urls, feature_contributions.
        """
        # Extract all features using full pipeline (content, URL, metadata, semantic, grammar, behavioral)
        features = self._extract_all_features(email_data)
        
        # Perform detection
        if self.model is not None:
            threat_score, threat_type, feature_array, feature_names_used = self._ml_detection(features)
        else:
            threat_score, threat_type = self._rule_based_detection(features, email_data)
            feature_array = None
            feature_names_used = None
        
        risk_factors = self._identify_risk_factors(features, email_data)
        recommendations = self._generate_recommendations(threat_score, risk_factors)
        confidence = self._calculate_confidence(threat_score, risk_factors)
        
        # Risk breakdown (content / URL / metadata) and SHAP contributions
        risk_breakdown = self._compute_risk_breakdown(features, feature_array, feature_names_used)
        feature_contributions = []
        if feature_array is not None and feature_names_used and SHAP_AVAILABLE and self.model is not None:
            feature_contributions = self._get_shap_contributions(feature_array, feature_names_used)
            if not risk_breakdown and feature_contributions:
                risk_breakdown = self._risk_breakdown_from_shap(feature_contributions)
        
        if not risk_breakdown:
            risk_breakdown = self._rule_based_risk_breakdown(features)
        
        # Suspicious text spans (for highlighting in GUI)
        body = email_data.get('body', '')
        subject = email_data.get('subject', '')
        suspicious_spans = self._get_suspicious_spans(subject, body)
        
        # Suspicious URLs with reasons
        urls = email_data.get('urls', []) or []
        if not urls and body:
            urls = re.findall(r'https?://[^\s<>"\']+|www\.[^\s<>"\']+', body)
        suspicious_urls = self._get_suspicious_urls(urls)
        
        return {
            'is_threat': threat_score >= 0.5,
            'threat_score': threat_score,
            'threat_type': threat_type,
            'confidence': confidence,
            'risk_factors': risk_factors,
            'recommendations': recommendations,
            'features': features,
            'risk_breakdown': risk_breakdown,
            'suspicious_spans': suspicious_spans,
            'suspicious_urls': suspicious_urls,
            'feature_contributions': feature_contributions,
        }
    
    def _extract_all_features(self, email_data: Dict) -> Dict:
        """Extract all features using FeatureExtractor (content, URL, metadata, semantic, grammar, behavioral)."""
        # Normalize keys for FeatureExtractor (accepts body/subject/sender or email_body/email_subject/from_address)
        normalized = {
            'body': email_data.get('body', ''),
            'subject': email_data.get('subject', ''),
            'email_body': email_data.get('body', ''),
            'email_subject': email_data.get('subject', ''),
            'from_address': email_data.get('sender', ''),
            'sender': email_data.get('sender', ''),
            'to_address': email_data.get('to_address', ''),
            'reply_to': email_data.get('reply_to', ''),
            'urls': email_data.get('urls', []) or [],
            'attachments': email_data.get('attachments', []),
            'headers': email_data.get('headers'),
        }
        return self.feature_extractor.extract_features(normalized)
    
    def _features_to_array(self, features: Dict, feature_names: Optional[List[str]] = None) -> Tuple[np.ndarray, List[str]]:
        """Convert feature dict to array in feature_names order; fill 0 for missing. Returns (array, names_used)."""
        if feature_names:
            names_used = list(feature_names)
        else:
            # Legacy: fixed content-only list
            names_used = [
                'char_count', 'word_count', 'sentence_count', 'avg_word_length',
                'avg_sentence_length', 'uppercase_ratio', 'special_char_ratio',
                'phishing_keyword_count', 'phishing_keyword_ratio', 'high_risk_phrase_count',
                'url_count', 'ip_address_count', 'email_address_count', 'has_url', 'has_ip',
                'vocabulary_richness', 'max_word_frequency', 'max_word_frequency_ratio',
                'urgency_word_count', 'urgency_word_ratio', 'exclamation_count',
                'question_count', 'exclamation_ratio'
            ]
        arr = np.array([float(features.get(f, 0)) for f in names_used], dtype=np.float64)
        return arr, names_used
    
    def _ml_detection(self, features: Dict) -> Tuple[float, str, Optional[np.ndarray], Optional[List[str]]]:
        """ML-based detection. Returns (threat_score, threat_type, feature_array, feature_names)."""
        try:
            bundle = self.model_bundle
            feature_names = (bundle or {}).get('feature_names')
            scaler = (bundle or {}).get('scaler') if bundle else None
            
            feature_array, names_used = self._features_to_array(features, feature_names)
            if scaler is not None:
                feature_array = scaler.transform(feature_array.reshape(1, -1))[0]
            
            model = self.model
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba(feature_array.reshape(1, -1))[0]
                threat_score = float(proba[1] if len(proba) > 1 else proba[0])
            else:
                prediction = model.predict(feature_array.reshape(1, -1))[0]
                threat_score = float(prediction)
            
            if threat_score >= 0.7:
                threat_type = 'phishing'
            elif threat_score >= 0.5:
                threat_type = 'suspicious'
            else:
                threat_type = 'legitimate'
            
            return threat_score, threat_type, feature_array, names_used
            
        except Exception as e:
            print(f"ML detection error: {e}")
            sc, tt = self._rule_based_detection(features, {})
            return sc, tt, None, None
    
    def _rule_based_detection(self, features: Dict, email_data: Dict) -> Tuple[float, str]:
        """Fallback rule-based threat detection."""
        risk_score = 0.0
        
        pk = features.get('phishing_keyword_count', 0)
        if pk > 4:
            risk_score += 0.35
        elif pk > 2:
            risk_score += 0.25
        
        if features.get('high_risk_phrase_count', 0) > 0:
            risk_score += 0.25
        
        if features.get('url_count', 0) > 2:
            risk_score += 0.2
        elif features.get('url_count', 0) > 0:
            risk_score += 0.1
        
        if features.get('ip_address_count', 0) > 0:
            risk_score += 0.25
        
        if features.get('urgency_word_count', 0) > 2:
            risk_score += 0.2
        elif features.get('urgency_word_count', 0) > 0:
            risk_score += 0.1
        
        if features.get('exclamation_count', 0) > 3:
            risk_score += 0.15
        elif features.get('exclamation_count', 0) > 1:
            risk_score += 0.08
        
        # New features
        if features.get('grammar_anomaly_score', 0) > 0.5:
            risk_score += 0.1
        if features.get('brand_impersonation', 0) == 1 or features.get('url_brand_impersonation', 0) == 1:
            risk_score += 0.25
        if features.get('cta_intensity', 0) > 0.5:
            risk_score += 0.1
        if features.get('time_pressure_score', 0) > 0.5:
            risk_score += 0.1
        if features.get('has_high_risk_attachment', 0) == 1:
            risk_score += 0.2
        
        risk_score = min(1.0, risk_score)
        
        if risk_score >= 0.7:
            threat_type = 'phishing'
        elif risk_score >= 0.5:
            threat_type = 'suspicious'
        else:
            threat_type = 'legitimate'
        
        return risk_score, threat_type
    
    def _rule_based_detection(self, features: Dict, email_data: Dict) -> Tuple[float, str]:
        """Fallback rule-based threat detection."""
        risk_score = 0.0
        
        # Check for high-risk keywords (lowered bar so obvious phishing is caught)
        pk = features.get('phishing_keyword_count', 0)
        if pk > 4:
            risk_score += 0.35
        elif pk > 2:
            risk_score += 0.25
        
        if features.get('high_risk_phrase_count', 0) > 0:
            risk_score += 0.25
        
        # Check for suspicious patterns
        if features.get('url_count', 0) > 2:
            risk_score += 0.2
        elif features.get('url_count', 0) > 0:
            risk_score += 0.1
        
        if features.get('ip_address_count', 0) > 0:
            risk_score += 0.25
        
        # Check urgency indicators
        if features.get('urgency_word_count', 0) > 2:
            risk_score += 0.2
        elif features.get('urgency_word_count', 0) > 0:
            risk_score += 0.1
        
        if features.get('exclamation_count', 0) > 3:
            risk_score += 0.15
        elif features.get('exclamation_count', 0) > 1:
            risk_score += 0.08
        
        # Cap at 1.0
        risk_score = min(1.0, risk_score)
        
        # Determine threat type
        if risk_score >= 0.7:
            threat_type = 'phishing'
        elif risk_score >= 0.5:
            threat_type = 'suspicious'
        else:
            threat_type = 'legitimate'
        
        return risk_score, threat_type
    
    def _compute_risk_breakdown(self, features: Dict, feature_array: Optional[np.ndarray], feature_names: Optional[List[str]]) -> Dict[str, float]:
        """Compute content/url/metadata risk breakdown from SHAP or features. Returns dict with content, url, metadata keys."""
        return {}
    
    def _risk_breakdown_from_shap(self, contributions: List[Dict]) -> Dict[str, float]:
        """Aggregate SHAP contributions by prefix into content, url, metadata."""
        content_sum = url_sum = meta_sum = 0.0
        for c in contributions:
            name = (c.get('feature') or c.get('feature_name') or '').lower()
            val = float(c.get('contribution', 0) or 0)
            if name.startswith('url_'):
                url_sum += max(0, val)
            elif any(name.startswith(p) for p in ('from_', 'reply_to_', 'subject_')):
                meta_sum += max(0, val)
            else:
                content_sum += max(0, val)
        total = content_sum + url_sum + meta_sum
        if total <= 0:
            return {'content': 0, 'url': 0, 'metadata': 0}
        return {
            'content': round(content_sum / total, 3),
            'url': round(url_sum / total, 3),
            'metadata': round(meta_sum / total, 3),
        }
    
    def _rule_based_risk_breakdown(self, features: Dict) -> Dict[str, float]:
        """Simple risk breakdown from feature groups when SHAP not available."""
        c = 0.0
        if features.get('phishing_keyword_count', 0) > 0 or features.get('urgency_word_count', 0) > 0:
            c += 0.5
        if features.get('url_count', 0) > 0:
            c += 0.2
        u = 0.5 if (features.get('url_count', 0) > 0) else 0.0
        if features.get('url_brand_impersonation', 0) == 1 or features.get('brand_impersonation', 0) == 1:
            u += 0.5
        m = 0.2 if features.get('sender_has_number', 0) == 1 else 0.0
        total = c + u + m
        if total <= 0:
            return {'content': 0.33, 'url': 0.33, 'metadata': 0.34}
        return {'content': round(c / total, 3), 'url': round(u / total, 3), 'metadata': round(m / total, 3)}
    
    def _get_shap_contributions(self, feature_array: np.ndarray, feature_names: List[str], top_k: int = 15) -> List[Dict[str, Any]]:
        """Compute SHAP values for one instance; return top_k by absolute contribution."""
        if not SHAP_AVAILABLE or self.model is None:
            return []
        try:
            model = self.model
            X = feature_array.reshape(1, -1)
            # KernelExplainer works with any model; background = zeros so baseline is "no signal"
            background = np.zeros((1, len(feature_array)), dtype=np.float64)
            explainer = shap.KernelExplainer(model.predict_proba, background, nsamples=50)
            shap_vals = explainer.shap_values(X, nsamples=50)
            if isinstance(shap_vals, list):
                shap_vals = shap_vals[1] if len(shap_vals) > 1 else shap_vals[0]
            if shap_vals is None or getattr(shap_vals, 'size', 0) == 0:
                return []
            row = np.asarray(shap_vals).flatten()
            contributions = []
            for i, name in enumerate(feature_names):
                if i < len(row):
                    contributions.append({'feature': name, 'contribution': float(row[i])})
            contributions.sort(key=lambda x: -abs(x['contribution']))
            return contributions[:top_k]
        except Exception:
            return []
    
    def _get_suspicious_spans(self, subject: str, body: str) -> List[Dict[str, Any]]:
        """Return list of {start, end, reason} for subject+body (combined text). Offsets for body only by convention."""
        spans = []
        text = (subject or '') + '\n\n' + (body or '')
        if not text:
            return spans
        body_offset = len((subject or '') + '\n\n')
        
        # Phishing keywords and high-risk phrases
        keywords = ['urgent', 'verify', 'suspend', 'click here', 'verify now', 'account suspended', 'password expired', 'update payment']
        for kw in keywords:
            start = 0
            while True:
                idx = text.lower().find(kw, start)
                if idx == -1:
                    break
                spans.append({'start': idx, 'end': idx + len(kw), 'reason': 'Suspicious phrase'})
                start = idx + 1
        
        # URLs
        for m in re.finditer(r'https?://[^\s<>"\']+|www\.[^\s<>"\']+', text):
            spans.append({'start': m.start(), 'end': m.end(), 'reason': 'URL'})
        
        # Dedupe/merge overlapping? Keep simple: sort and return (frontend can handle)
        spans.sort(key=lambda s: s['start'])
        return spans[:50]
    
    def _get_suspicious_urls(self, urls: List[str]) -> List[Dict[str, str]]:
        """Return list of {url, reason} for URLs that look suspicious."""
        result = []
        for url in (urls or [])[:20]:
            if not url or not isinstance(url, str):
                continue
            reasons = []
            try:
                feats = self.url_analyzer.extract_features(url)
                if feats.get('brand_impersonation', 0) == 1:
                    reasons.append('Brand impersonation')
                if feats.get('is_suspicious_tld', 0) == 1:
                    reasons.append('Suspicious TLD')
                if feats.get('has_ip_address', 0) == 1:
                    reasons.append('IP address in URL')
                if feats.get('domain_age_days', 0) >= 0 and feats.get('domain_age_days', 0) < 90:
                    reasons.append('New or young domain')
                if feats.get('has_https_but_suspicious', 0) == 1:
                    reasons.append('HTTPS with suspicious host')
                if feats.get('deceptive_secure_language', 0) == 1:
                    reasons.append('Deceptive security language')
                if feats.get('shortened_url', 0) == 1:
                    reasons.append('URL shortener')
            except Exception:
                reasons.append('Could not analyze')
            result.append({'url': url[:200], 'reason': '; '.join(reasons) if reasons else 'None'})
        return result
    
    def _identify_risk_factors(self, features: Dict, email_data: Dict) -> list:
        """Identify specific risk factors in the email."""
        risk_factors = []
        
        # Check various risk indicators
        if features.get('phishing_keyword_count', 0) > 2:
            risk_factors.append('Multiple phishing keywords detected')
        
        if features.get('high_risk_phrase_count', 0) > 0:
            risk_factors.append('High-risk phrases found')
        
        if features.get('url_count', 0) > 5:
            risk_factors.append('Excessive number of URLs')
        
        if features.get('ip_address_count', 0) > 0:
            risk_factors.append('Direct IP addresses in links')
        
        if features.get('urgency_word_count', 0) > 3:
            risk_factors.append('Urgency manipulation detected')
        
        if features.get('exclamation_count', 0) > 3:
            risk_factors.append('Excessive punctuation (emotional manipulation)')
        
        sender = email_data.get('sender', '')
        if sender and any(c.isdigit() for c in sender.split('@')[0]):
            risk_factors.append('Suspicious sender address with numbers')
        
        if features.get('uppercase_ratio', 0) > 0.3:
            risk_factors.append('Excessive use of uppercase letters')
        
        if features.get('grammar_anomaly_score', 0) > 0.5:
            risk_factors.append('Grammar or spelling anomalies (possible machine-generated)')
        if features.get('brand_impersonation', 0) == 1 or features.get('url_brand_impersonation', 0) == 1:
            risk_factors.append('Possible brand impersonation in URL')
        if features.get('cta_intensity', 0) > 0.5:
            risk_factors.append('Strong call-to-action pressure')
        if features.get('time_pressure_score', 0) > 0.5:
            risk_factors.append('Time-pressure or urgency tactics')
        if features.get('has_high_risk_attachment', 0) == 1:
            risk_factors.append('High-risk attachment type detected')
        
        return risk_factors
    
    def _generate_recommendations(self, threat_score: float, risk_factors: list) -> list:
        """Generate recommendations based on threat analysis."""
        recommendations = []
        
        if threat_score >= 0.8:
            recommendations.append('⚠️ HIGH RISK - Do not interact with this email')
            recommendations.append('Do not click any links or download attachments')
            recommendations.append('Mark as spam or phishing immediately')
            recommendations.append('Consider reporting to your IT security team')
        elif threat_score >= 0.6:
            recommendations.append('⚡ MEDIUM RISK - Exercise extreme caution')
            recommendations.append('Verify sender identity through alternate channel')
            recommendations.append('Do not provide any personal information')
            recommendations.append('Hover over links to check destination before clicking')
        elif threat_score >= 0.4:
            recommendations.append('⚠️ LOW RISK - Be cautious')
            recommendations.append('Verify sender if requesting sensitive actions')
            recommendations.append('Check for official communication through legitimate channels')
        else:
            recommendations.append('✓ Email appears legitimate')
            recommendations.append('Always remain vigilant with unexpected requests')
        
        return recommendations
    
    def _calculate_confidence(self, threat_score: float, risk_factors: list) -> str:
        """Calculate confidence level of the detection."""
        # High confidence if clear indicators
        if threat_score >= 0.8 or len(risk_factors) >= 4:
            return 'high'
        elif threat_score >= 0.6 or len(risk_factors) >= 2:
            return 'medium'
        else:
            return 'low'
    
    def batch_analyze(self, emails: list) -> list:
        """
        Analyze multiple emails in batch.
        
        Args:
            emails: List of email data dictionaries
            
        Returns:
            List of analysis results
        """
        results = []
        for email in emails:
            try:
                result = self.analyze_email(email)
                results.append(result)
            except Exception as e:
                print(f"Error analyzing email: {e}")
                results.append({
                    'is_threat': False,
                    'threat_score': 0.0,
                    'error': str(e)
                })
        return results
