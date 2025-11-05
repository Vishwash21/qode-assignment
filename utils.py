"""
utils.py - logging + I/O helpers
"""

import logging
from pathlib import Path
import yaml
import os

def setup_logging(logfile: str = "qode.log"):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")
    # console
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    # file
    fh = logging.FileHandler(logfile)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

def load_config(path: str = "config.yaml"):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    with open(p, "r") as f:
        return yaml.safe_load(f)

def ensure_output_dirs(base_dir: str):
    p = Path(base_dir)
    (p / "data").mkdir(parents=True, exist_ok=True)
    (p / "sample_output").mkdir(parents=True, exist_ok=True)
