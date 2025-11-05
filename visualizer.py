"""
visualizer.py
- plotting utilities (correlation heatmap, timeseries sampling plot)
"""

import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger("visualizer")

def plot_composite_timeseries(df, out_path: str, sample_rate: int = 1):
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    x = np.arange(len(df))
    y = df['composite_signal'].values
    if sample_rate > 1:
        idx = x[::sample_rate]
    else:
        idx = x
    plt.figure(figsize=(8,4))
    plt.scatter(idx, y[idx], c=y[idx], cmap='coolwarm', s=8)
    plt.title("Composite Signal (sampled)")
    plt.xlabel("Index")
    plt.ylabel("Composite Signal")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    logger.info("Saved timeseries plot to %s", out_path)

def plot_correlation_heatmap(df, out_path: str):
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    cols = ['tfidf_signal','sentiment','engagement','composite_signal']
    present = [c for c in cols if c in df.columns]
    corr = df[present].corr()
    plt.figure(figsize=(6,4))
    sns.heatmap(corr, annot=True, cmap='coolwarm')
    plt.title("Feature Correlation")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    logger.info("Saved correlation heatmap to %s", out_path)
