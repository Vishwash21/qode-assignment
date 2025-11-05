"""
processor.py
- Cleaning, normalization, deduplication
- Parquet write/read helpers
"""

import re
import pandas as pd
from pathlib import Path
import unicodedata
import logging

logger = logging.getLogger("processor")

def normalize_unicode(text: str) -> str:
    if text is None:
        return ""
    return unicodedata.normalize("NFKC", text)

def clean_text(text: str) -> str:
    text = normalize_unicode(text)
    text = re.sub(r"http\S+", " ", text)            # remove URLs
    text = re.sub(r"[^0-9A-Za-z#@ \u0900-\u097F]", " ", text)  # keep basic letters and Devanagari
    text = re.sub(r"\s+", " ", text).strip()
    return text.lower()

def build_dataframe(records: list) -> pd.DataFrame:
    df = pd.DataFrame(records)
    if df.empty:
        logger.warning("No records to build DataFrame.")
        return df
    df['content'] = df['content'].astype(str).apply(clean_text)
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce', utc=True)
    else:
        df['timestamp'] = pd.Timestamp.utcnow()
    # extract hashtags/mentions if missing
    if 'hashtags' not in df.columns:
        df['hashtags'] = df['content'].apply(lambda x: re.findall(r"#(\w+)", x))
    if 'mentions' not in df.columns:
        df['mentions'] = df['content'].apply(lambda x: re.findall(r"@(\w+)", x))
    before = len(df)
    df = df.drop_duplicates(subset=['content']).reset_index(drop=True)
    after = len(df)
    logger.info("Deduplicated tweets: %d -> %d", before, after)
    return df

def write_parquet(df: pd.DataFrame, out_path: str):
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(p, index=False)
    logger.info("Wrote %d rows to %s", len(df), out_path)

def read_parquet(path: str) -> pd.DataFrame:
    return pd.read_parquet(path)
