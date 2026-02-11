"""
Semantic Analyzer
Transformer-based text embeddings for phishing detection (semantic meaning beyond keywords).
Uses sentence-transformers when available; gracefully degrades when not installed.
"""

import numpy as np

# Optional: sentence-transformers (heavy dependency)
_SENTENCE_TRANSFORMERS_AVAILABLE = False
_model = None

def _load_model():
    global _model, _SENTENCE_TRANSFORMERS_AVAILABLE
    if _model is not None:
        return _model
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        _SENTENCE_TRANSFORMERS_AVAILABLE = True
        return _model
    except Exception:
        _SENTENCE_TRANSFORMERS_AVAILABLE = False
        return None


# Embedding dimension after reduction (original all-MiniLM-L6-v2 is 384)
SEMANTIC_FEATURE_DIM = 32


def extract_features(subject: str, body: str) -> dict:
    """
    Extract semantic embedding features from email subject and body.
    Returns dict with keys semantic_1, ..., semantic_k (k = SEMANTIC_FEATURE_DIM).
    If sentence-transformers is unavailable, returns zeros for all semantic_* keys.
    """
    out = {}
    model = _load_model()
    if not model or not _SENTENCE_TRANSFORMERS_AVAILABLE:
        for i in range(1, SEMANTIC_FEATURE_DIM + 1):
            out[f'semantic_{i}'] = 0.0
        return out

    try:
        subject = (subject or '').strip() or ' '
        body = (body or '').strip() or ' '
        # Encode subject and body separately, then mean-pool for a single vector
        emb_subject = model.encode([subject], show_progress_bar=False)[0]
        emb_body = model.encode([body], show_progress_bar=False)[0]
        combined = (np.asarray(emb_subject) + np.asarray(emb_body)) / 2.0
        # Use first SEMANTIC_FEATURE_DIM dimensions as features (reduction)
        reduced = combined[:SEMANTIC_FEATURE_DIM]
        for i, val in enumerate(reduced, start=1):
            out[f'semantic_{i}'] = float(val)
        return out
    except Exception:
        for i in range(1, SEMANTIC_FEATURE_DIM + 1):
            out[f'semantic_{i}'] = 0.0
        return out


def is_available() -> bool:
    """Return True if sentence-transformers is loaded and usable."""
    _load_model()
    return _SENTENCE_TRANSFORMERS_AVAILABLE
