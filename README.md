# Qode Assignment — Advanced Pipeline (Sample-first, optional live scraping)

## Overview
This project demonstrates a real-time market intelligence pipeline:
- Collect tweets (simulated or optional live scraping)
- Clean, deduplicate, store (Parquet)
- Generate TF-IDF + Sentiment-based signals
- Produce visualizations and deliverables

## Quick Start
1. Create venv (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/Mac
   .venv\Scripts\activate      # Windows
