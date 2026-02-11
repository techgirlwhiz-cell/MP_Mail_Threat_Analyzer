"""
Grammar and Spelling Anomaly Detection
Lightweight heuristics to identify low-quality or machine-generated phishing content.
"""

import re


# Common English words (subset) - unknown words ratio signals spelling/grammar anomalies
COMMON_WORDS = frozenset(
    'a an the is are was were be been being have has had do does did will would '
    'could should may might must shall can need dare ought used to of in for on '
    'with at by from as into through during before after above below to up out '
    'about again then so when what which who this that these those i you he she '
    'it we they your our their my his her its me us them and but or nor yet '
    'both either neither not only just also back if than until while although '
    'because since when where after before once until whenever wherever whether '
    'hello please thank thanks dear sir madam account verify click update login '
    'password secure confirm bank payment card information'.split()
)


def extract_features(text: str) -> dict:
    """
    Extract grammar/spelling anomaly features (0-1 scores).
    Returns grammar_anomaly_score, spelling_anomaly_score.
    """
    if not text or not text.strip():
        return {'grammar_anomaly_score': 0.0, 'spelling_anomaly_score': 0.0}

    text = text.strip()
    words = re.findall(r'[a-zA-Z]+', text.lower())
    if not words:
        return {'grammar_anomaly_score': 0.0, 'spelling_anomaly_score': 0.0}

    # Spelling heuristic: high ratio of words not in common set
    unknown = sum(1 for w in words if w not in COMMON_WORDS and len(w) > 1)
    spelling_anomaly = min(1.0, (unknown / len(words)) * 1.5)  # scale so not every rare word = 1

    # Grammar-style heuristics: unusual punctuation, repeated chars, all-caps words
    char_count = len(text)
    # Repeated character sequences (e.g. "pleeease", "!!!")
    repeated = len(re.findall(r'(.)\1{2,}', text))
    repeated_ratio = repeated / max(1, char_count / 50)
    # Unusual punctuation density (many ! or ?)
    exclam_quest = text.count('!') + text.count('?')
    punct_ratio = exclam_quest / max(1, len(words))
    # Very short or very long words ratio
    short_words = sum(1 for w in words if len(w) <= 2)
    long_words = sum(1 for w in words if len(w) > 12)
    word_weird = (short_words / len(words) * 0.5 + min(1.0, long_words / max(1, len(words)) * 5)) / 2
    grammar_anomaly = min(1.0, repeated_ratio * 0.4 + min(1.0, punct_ratio) * 0.4 + word_weird * 0.3)

    return {
        'grammar_anomaly_score': round(grammar_anomaly, 4),
        'spelling_anomaly_score': round(spelling_anomaly, 4),
    }
