"""
main.py - orchestrates scraping -> processing -> analysis -> visualization
Run as: python -m src.main
"""

import logging
from pathlib import Path
import argparse
import sys
import os
from datetime import datetime

# ensure package imports work when running as module
sys.path.append(os.path.dirname(__file__))

from utils import setup_logging, load_config, ensure_output_dirs
from scraper import scrape_multiple_hashtags
from processor import build_dataframe, write_parquet
from analyzer import analyze_dataframe
from visualizer import plot_composite_timeseries, plot_correlation_heatmap

def run_pipeline(cfg):
    hashtags = cfg.get('hashtags', ['nifty50','sensex','intraday','banknifty'])
    max_per = cfg.get('max_per_hashtag', 500)
    sample_mode = cfg.get('sample_mode', True)
    out_dir = Path(cfg.get('output_dir', "../qode_output"))
    ensure_output_dirs(out_dir)

    logging.info("Starting scrape (sample_mode=%s) for %s", sample_mode, hashtags)
    records = scrape_multiple_hashtags(hashtags, max_per, sample_mode=sample_mode, seed=cfg.get('random_seed',42))
    if not records:
        logging.warning("No records scraped. Exiting.")
        return

    logging.info("Processing records into DataFrame")
    df = build_dataframe(records)
    if df.empty:
        logging.warning("No records after processing. Exiting.")
        return

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M")
    raw_path = out_dir / "data" / f"clean_tweets_{timestamp}.parquet"
    write_parquet(df, str(raw_path))

    logging.info("Analyzing DataFrame")
    analyzed = analyze_dataframe(df, cfg)

    analyzed_path = out_dir / "data" / f"analyzed_signals_{timestamp}.parquet"
    write_parquet(analyzed, str(analyzed_path))

    # Visuals
    plot_composite_timeseries(analyzed, str(out_dir / "sample_output" / f"composite_{timestamp}.png"),
                             sample_rate=max(1, len(analyzed)//2000))
    plot_correlation_heatmap(analyzed, str(out_dir / "sample_output" / f"corr_{timestamp}.png"))

    # Save small CSV sample
    sample_csv = out_dir / "sample_output" / f"signals_sample_{timestamp}.csv"
    analyzed.head(2000).to_csv(sample_csv, index=False)
    logging.info("Saved sample CSV to %s", sample_csv)

    logging.info("Pipeline complete. Outputs in %s", out_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(Path(__file__).parent / "config.yaml"))
    args = parser.parse_args()

    setup_logging()
    cfg = load_config(args.config)
    run_pipeline(cfg)
