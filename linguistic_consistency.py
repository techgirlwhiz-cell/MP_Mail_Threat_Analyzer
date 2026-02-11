"""
Linguistic Consistency
Subject vs body sentiment, tone, and formality mismatches.
"""

import re

# Simple sentiment lexicon: positive/negative word lists (small subset)
POSITIVE = frozenset(
    'good great thank thanks happy pleased confirm verified success welcome '
    'congratulations approved secure safe trusted'.split()
)
NEGATIVE = frozenset(
    'urgent suspend suspended locked expired problem warning alert critical '
    'verify immediately action required fail failed error fix update'.split()
)

# Formal markers
FORMAL = frozenset(
    'sir madam regarding pursuant hereby therefore furthermore nevertheless '
    'accordingly sincerely respectfully'.split()
)
# Informal markers
INFORMAL = frozenset(
    'hey hi dude lol omg u r ur plz thx wanna gonna'.split()
)


def _sentiment_score(text: str) -> float:
    """Crude sentiment: positive words add, negative subtract; normalize to roughly -1..1."""
    if not text:
        return 0.0
    words = set(re.findall(r'[a-zA-Z]+', text.lower()))
    pos = len(words & POSITIVE)
    neg = len(words & NEGATIVE)
    total = pos + neg
    if total == 0:
        return 0.0
    return (pos - neg) / total


def _formality_score(text: str) -> float:
    """Formality: (formal_count - informal_count) / total; higher = more formal."""
    if not text:
        return 0.0
    words = re.findall(r'[a-zA-Z]+', text.lower())
    if not words:
        return 0.0
    formal_count = sum(1 for w in words if w in FORMAL)
    informal_count = sum(1 for w in words if w in INFORMAL)
    return (formal_count - informal_count) / max(1, len(words)) * 10  # scale


def extract_features(subject: str, body: str) -> dict:
    """
    Compare subject vs body: sentiment and formality/tone.
    Returns subject_body_sentiment_diff, subject_body_formality_diff (absolute differences).
    """
    subject = (subject or '').strip()
    body = (body or '').strip()

    sent_subj = _sentiment_score(subject)
    sent_body = _sentiment_score(body)
    form_subj = _formality_score(subject)
    form_body = _formality_score(body)

    return {
        'subject_body_sentiment_diff': abs(sent_subj - sent_body),
        'subject_body_formality_diff': abs(form_subj - form_body),
    }
