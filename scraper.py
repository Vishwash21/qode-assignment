"""
scraper.py
- Provides two interfaces:
  1) sample data generator (default, recommended)
  2) optional live scraping using Selenium (experimental)
"""

from typing import List, Dict
import random
from datetime import datetime, timezone
import time
import logging

logger = logging.getLogger("scraper")

def sample_tweets_for(hashtag: str, n: int = 500, seed: int = 42) -> List[Dict]:
    random.seed(seed)
    out = []
    now = datetime.now(timezone.utc)
    patterns = [
        "Strong move in #{h}, looks {sent}. traders expect {dir}.",
        "#{h} showing {sent} momentum — watch levels. price likely {dir}.",
        "Short term {h} {sent}. intraday traders {dir} today.",
        "Market chatter about #{h}: {sent} — volume rising."
    ]
    for i in range(n):
        sent = random.choice(["bullish","bearish","neutral"])
        dirc = "up" if sent == "bullish" else ("down" if sent == "bearish" else random.choice(["up","down"]))
        content = random.choice(patterns).format(h=hashtag, sent=sent, dir=dirc)
        out.append({
            "username": f"user_{hashtag}_{i}",
            "timestamp": now.isoformat(),
            "content": content,
            "likes": random.randint(0, 500),
            "retweets": random.randint(0, 200),
            "replies": random.randint(0, 50),
            "hashtags": [hashtag],
            "mentions": []
        })
    logger.info("Generated %d sample tweets for %s", n, hashtag)
    return out

# ---- Optional live scraping (experimental) ----
# NOTE: Live scraping may fail because X/Twitter blocks unauthenticated access or uses heavy JS.
# If you want to try live, ensure ChromeDriver is installed and compatible, and set sample_mode=False
def _live_scrape_hashtag(hashtag: str, max_tweets: int = 500, headless: bool = True) -> List[Dict]:
    from bs4 import BeautifulSoup
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    import html, re

    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--lang=en-US")
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=opts)
    url = f"https://twitter.com/search?q=%23{hashtag}&f=live"
    driver.get(url)
    time.sleep(3)
    data = []
    seen = set()
    scrolls = 0
    last_height = driver.execute_script("return document.body.scrollHeight")

    while len(data) < max_tweets and scrolls < 30:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        articles = soup.find_all("article")
        for art in articles:
            try:
                text = art.get_text(" ", strip=True)
                text = html.unescape(text)
                if text in seen:
                    continue
                seen.add(text)
                time_tag = art.find("time")
                timestamp = time_tag["datetime"] if time_tag and time_tag.has_attr("datetime") else datetime.now(timezone.utc).isoformat()
                username_el = art.find("div", attrs={"dir":"ltr"})
                username = username_el.get_text(strip=True) if username_el else "unknown"
                hashtags = re.findall(r"#(\w+)", text)
                mentions = re.findall(r"@(\w+)", text)
                data.append({
                    "username": username,
                    "timestamp": timestamp,
                    "content": text,
                    "likes": 0, "retweets": 0, "replies": 0,
                    "hashtags": hashtags,
                    "mentions": mentions
                })
                if len(data) >= max_tweets:
                    break
            except Exception:
                continue
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5 + random.random()*0.5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            scrolls += 1
        else:
            scrolls = 0
        last_height = new_height

    driver.quit()
    logger.info("Live scraped %d tweets for %s (may be incomplete)", len(data), hashtag)
    return data

def scrape_multiple_hashtags(hashtags: List[str], max_per_hashtag: int = 500, sample_mode: bool = True, seed: int = 42) -> List[Dict]:
    all_records = []
    for h in hashtags:
        if sample_mode:
            recs = sample_tweets_for(h, n=max_per_hashtag, seed=seed)
        else:
            recs = _live_scrape_hashtag(h, max_tweets=max_per_hashtag)
        all_records.extend(recs)
    return all_records
