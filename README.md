# Qode Assignment — Advanced Market Sentiment Pipeline  
*A modular Python data pipeline for social sentiment analysis and market signal generation.*

---

## Overview

This project implements a real-time market intelligence pipeline that processes tweets and simulates social-media-driven market sentiment.

It is built in Python, fully modular, and designed for scalability and readability — demonstrating the ability to design end-to-end data systems.

### The Pipeline Includes:
1. **Data Collection** — via simulated sample data (default) or optional Selenium-based live scraping.  
2. **Data Processing** — cleaning, normalization, and deduplication with hashtag and mention extraction.  
3. **Sentiment & TF-IDF Analysis** — computes textual features and VADER sentiment scores.  
4. **Composite Signal Generation** — combines sentiment, engagement, and TF-IDF weights to produce trading signals.  
5. **Visualization & Outputs** — generates CSVs, correlation heatmaps, and signal scatter plots.

---

## Features

| Feature | Description |
|----------|-------------|
| Sentiment Analysis | Uses VADER (and optional transformer model) |
| Text Cleaning | Unicode normalization and removal of unwanted symbols |
| TF-IDF + PCA | Converts text to numeric features with dimensionality reduction |
| Efficient Storage | Outputs stored as Parquet + CSV |
| Visualization | Composite signal scatter and feature correlation heatmap |
| Config-Driven | All parameters (hashtags, limits, modes) managed via YAML |
| Modular Architecture | Separate modules for scraping, processing, analysis, and visualization |

---

## Quick Start

### 1. Create Virtual Environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
python -m nltk.downloader vader_lexicon
hashtags:
  - nifty50
  - sensex
  - intraday
  - banknifty
max_per_hashtag: 500
sample_mode: true
use_transformer_sentiment: false
output_dir: "../qode_output"
python -m src.main


outputs
qode_output/
├── data/
│   ├── clean_tweets_<timestamp>.parquet
│   └── analyzed_signals_<timestamp>.parquet
└── sample_output/
    ├── signals_sample_<timestamp>.csv
    ├── composite_<timestamp>.png
    └── corr_<timestamp>.png

 project structure
qode_assignment/
├── src/
│   ├── main.py
│   ├── scraper.py
│   ├── processor.py
│   ├── analyzer.py
│   ├── visualizer.py
│   ├── utils.py
│   ├── config.yaml
│   └── __init__.py
├── qode_output/
├── requirements.txt
└── README.md

Vishwas Tiwari
Mumbai (Virar)
Email: tiwarivishwash.in124@gmail.com
]
GitHub: https://github.com/vishwastiwari/qode-assignment
