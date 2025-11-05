"""
analyzer.py
- TF-IDF, SVD, VADER sentiment
- Composite signal = weighted combination of sentiment, TF-IDF importance, engagement
- Optionally supports transformer-based sentiment (heavier)
"""
# Writen By Vishwash Tiwari

import logging
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import MinMaxScaler
from pathlib import Path
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

logger = logging.getLogger("analyzer")
nltk.download('vader_lexicon', quiet=True)

# Optional transformer path (disabled by default)
def compute_transformer_sentiment(texts, model_name="distilbert-base-uncased-finetuned-sst-2-english"):
    try:
        from transformers import pipeline
    except Exception as e:
        raise RuntimeError("Transformers not installed. Set use_transformer_sentiment to false in config.") from e
    sentiment = pipeline("sentiment-analysis", model=model_name)
    out = [sentiment(t[:512])[0] for t in texts]  # truncate long strings
    df = pd.DataFrame(out)
    # convert to compound-like numeric: POSITIVE -> score, NEGATIVE -> -score
    df['compound'] = df.apply(lambda r: r['score'] if r['label'].upper().startswith('POS') else -r['score'], axis=1)
    return df['compound'].values

def compute_tfidf_matrix(texts, max_features=2000):
    vectorizer = TfidfVectorizer(max_features=max_features, stop_words='english', ngram_range=(1,2))
    X = vectorizer.fit_transform(texts)
    logger.info("TF-IDF matrix shape: %s", X.shape)
    return X, vectorizer

def reduce_dimensionality(X, n_components=50):
    n_components = min(n_components, max(1, X.shape[1]-1))
    svd = TruncatedSVD(n_components=n_components, random_state=42)
    X_reduced = svd.fit_transform(X)
    logger.info("Reduced TF-IDF to %d components", X_reduced.shape[1])
    return X_reduced, svd

def compute_vader_sentiment(texts):
    sid = SentimentIntensityAnalyzer()
    scores = [sid.polarity_scores(t)['compound'] for t in texts]
    return np.array(scores)

def build_composite_signal(tfidf_vecs, sentiment_scores, likes, retweets, weights=(0.4,0.5,0.1)):
    """
    composite = w_tfidf * tfidf_score + w_sent * sentiment_score + w_eng * engagement_score
    engagement_score = normalized(likes + retweets)
    weights sum to 1
    """
    scaler = MinMaxScaler()
    tfidf_raw = np.mean(tfidf_vecs, axis=1)
    tfidf_scaled = scaler.fit_transform(tfidf_raw.reshape(-1,1)).reshape(-1)
    sent_scaled = scaler.fit_transform(sentiment_scores.reshape(-1,1)).reshape(-1)
    engagement = np.array(likes) + np.array(retweets)
    eng_scaled = scaler.fit_transform(engagement.reshape(-1,1)).reshape(-1)
    composite = weights[0]*tfidf_scaled + weights[1]*sent_scaled + weights[2]*eng_scaled
    return composite, tfidf_scaled, sent_scaled, eng_scaled

def analyze_dataframe(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    texts = df['content'].fillna("").astype(str).tolist()
    # TF-IDF
    X_tfidf, vectorizer = compute_tfidf_matrix(texts, max_features=config.get('tfidf_max_features', 2000))
    X_reduced, svd = reduce_dimensionality(X_tfidf, n_components=config.get('svd_components', 50))
    # Sentiment
    if config.get('use_transformer_sentiment', False):
        sentiment = compute_transformer_sentiment(texts)
    else:
        sentiment = compute_vader_sentiment(texts)
    # Engagement fields
    likes = df.get('likes', pd.Series([0]*len(df))).fillna(0).astype(int).values
    retweets = df.get('retweets', pd.Series([0]*len(df))).fillna(0).astype(int).values
    # Composite signal
    composite, tfidf_sig, sent_sig, eng_sig = build_composite_signal(X_reduced, sentiment, likes, retweets,
                                                                     weights=(0.4, 0.5, 0.1))
    out = df.copy().reset_index(drop=True)
    out['tfidf_signal'] = tfidf_sig
    out['sentiment'] = sent_sig
    out['engagement'] = eng_sig
    out['composite_signal'] = composite
    logger.info("Analysis complete for %d rows", len(out))
    return out
