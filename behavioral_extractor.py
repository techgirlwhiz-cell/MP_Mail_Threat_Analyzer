"""
Behavioral Feature Extractor
Call-to-action intensity, time-pressure (urgency + deadlines), attachment-based risk.
"""

import re


CTA_VERBS = frozenset(
    'click verify update submit confirm login open check activate review '
    'respond reply register validate secure renew unlock restore'.split()
)
CTA_PHRASES = [
    'click here', 'act now', 'click below', 'verify now', 'update now',
    'submit now', 'confirm your', 'log in', 'sign in', 'open link',
    'download now', 'claim now', 'get started', 'take action', 'respond now',
]

DEADLINE_PATTERNS = [
    r'\bwithin\s+\d+\s*(hour|day|minute)s?\b',
    r'\bby\s+(tomorrow|tonight|midnight)\b',
    r'\bexpires?\s+(in|on)\b',
    r'\bdeadline\s*:\s*\d',
    r'\b(only|just)\s+\d+\s*(hour|day)s?\s+left\b',
    r'\blimited\s+time\b',
    r'\b(urgent|asap|immediately)\b',
]

# Attachment risk by extension
HIGH_RISK_EXT = frozenset(
    'exe scr bat cmd com pif vbs js wsf wsh jar ws cpl msc'.split()
)
MEDIUM_RISK_EXT = frozenset(
    'zip rar 7z doc docx xls xlsb xlsm pdf hta lnk'.split()
)


def extract_features(body: str, subject: str = '', attachments: list = None) -> dict:
    """
    Extract behavioral features: CTA intensity, time-pressure score, attachment risk.
    body: email body text
    subject: email subject (used for time-pressure)
    attachments: list of attachment dicts with 'filename' or 'name' or str
    """
    out = {
        'cta_intensity': 0.0,
        'time_pressure_score': 0.0,
        'attachment_risk_score': 0.0,
        'has_high_risk_attachment': 0,
    }
    text = f"{subject} {body}".lower()
    words = text.split()
    if not words:
        return out

    # CTA intensity: imperative verbs + CTA phrases, normalized by length
    cta_count = 0
    for w in re.findall(r'[a-zA-Z]+', text):
        if w in CTA_VERBS:
            cta_count += 1
    for phrase in CTA_PHRASES:
        cta_count += text.count(phrase)
    out['cta_intensity'] = min(1.0, cta_count / max(1, len(words) / 10))

    # Time-pressure: urgency + deadline patterns
    urgency_count = sum(1 for p in DEADLINE_PATTERNS if re.search(p, text, re.I))
    out['time_pressure_score'] = min(1.0, urgency_count * 0.25 + (1 if 'urgent' in text or 'asap' in text else 0) * 0.3)

    # Attachment risk
    if attachments:
        risk_sum = 0
        has_high = 0
        for att in attachments:
            name = ''
            if isinstance(att, dict):
                name = (att.get('filename') or att.get('name') or '').lower()
            else:
                name = str(att).lower()
            if not name:
                continue
            ext = name.split('.')[-1] if '.' in name else ''
            if ext in HIGH_RISK_EXT:
                risk_sum += 1.0
                has_high = 1
            elif ext in MEDIUM_RISK_EXT:
                risk_sum += 0.5
        out['attachment_risk_score'] = min(1.0, risk_sum)
        out['has_high_risk_attachment'] = has_high
    return out
