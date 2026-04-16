# 📈 Stock Sentiment Tracker

A real-time stock sentiment analysis tool that pulls news and social media data from three sources, runs NLP sentiment scoring, and delivers a Buy / Hold / Sell recommendation with an animated visual indicator — all in a clean Streamlit interface.

> **Portfolio project** by [Valérie Vienne](https://valerie-vienne.com) — demonstrating multi-source data aggregation, NLP sentiment analysis, and interactive data visualisation.

---

## Live Demo

🔗 [Open on Streamlit Cloud](https://stock-sentiment-streamlit.onrender.com/)

---

## What it does

Enter any stock ticker (e.g. `AAPL`, `TSLA`, `NVDA`), choose a news source, and the app:

1. Fetches recent headlines and summaries from **Yahoo Finance**, **Google News**, or **Reddit**
2. Runs each headline + summary through **VADER** sentiment analysis
3. Computes a **weighted average sentiment score** — stronger signals carry more weight
4. Displays an **animated sentiment bar** (green / yellow / red) with the score
5. Returns a clear **Buy 🟢 / Hold 🟡 / Sell 🔴** recommendation
6. Lists all fetched headlines with links for manual review

---

## Architecture

```
User input: ticker + source
        │
        ▼
Source dispatcher
├── Yahoo Finance  → get_yahoo_news_headlines()  via yfinance
├── Google News    → get_google_news()            via gnews
└── Reddit         → get_reddit_posts()           via praw
        │
        ▼
analyze_sentiment()
  → VADER polarity scores per headline + summary
  → weighted average (|score| = weight)
  → filters out near-neutral noise (|score| < 0.05)
        │
        ▼
make_recommendation()
  → score > 0.3  → Buy  🟢
  → score < -0.3 → Sell 🔴
  → otherwise    → Hold 🟡
        │
        ▼
render_animated_sentiment_bar()
  → animated fill with gradient colour
  → headlines listed with links
```

---

## Project Structure

```
stock-sentiment-streamlit/
├── app.py               # main Streamlit app
├── requirements.txt     # dependencies
├── .env                 # Reddit API credentials — never commit this
├── .gitignore           # keeps .env off GitHub
└── README.md
```

---

## Key Components

### `get_yahoo_news_headlines()` — Yahoo Finance source
Uses `yfinance` to pull the 10 most recent news items for a ticker. Extracts title, canonical URL, and summary from the structured content object.

### `get_google_news()` — Google News source
Uses `gnews` to search for up to 20 recent articles mentioning the ticker. Returns title, URL, and article text. Note: the `text` field is used instead of `summary` because the summary field contains only link text.

### `get_reddit_posts()` — Reddit source
Searches 6 major finance subreddits (`stocks`, `investing`, `wallstreetbets`, `StockMarket`, `options`, `pennystocks`) for the ticker. Applies a quality filter before analysis:
- `upvote_ratio >= 0.75` — community-approved posts only
- `num_comments >= 20` — meaningful discussion only
- `created_utc >= seven_days_ago` — last 7 days only

Then sorts by a popularity score (`post.score + 2 × comments`) and takes the top 20. This prevents viral but low-quality posts from skewing the sentiment.

### `analyze_sentiment()` — VADER NLP scoring
Runs VADER's `polarity_scores()` on the combined headline + summary text for each item. Uses a **weighted average** where the weight is the absolute value of the compound score — so a score of `0.9` has 9× more influence than a score of `0.1`. Items with `|score| < 0.05` are excluded as noise.

```python
weighted_avg = sum(s * w for s, w in zip(scores, weights)) / sum(weights)
```

### `render_animated_sentiment_bar()` — visual output
Animates a progress bar filling from 0 to the sentiment score percentage using a `for` loop with `st.empty()`. Colour gradient changes based on the recommendation threshold:
- Green gradient for bullish (score > 0.3)
- Red gradient for bearish (score < -0.3)
- Yellow gradient for neutral

---

## Sentiment Thresholds

| Score range | Signal | Colour |
|---|---|---|
| > 0.3 | Buy 😃 | 🟢 Green |
| -0.3 to 0.3 | Hold 😐 | 🟡 Yellow |
| < -0.3 | Sell 😞 | 🔴 Red |

These thresholds follow standard VADER compound score conventions for financial text.

---

## Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/ValerieVienne/stock-sentiment-streamlit.git
cd stock-sentiment-streamlit

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up Reddit API credentials
# Create a .env file in the project root:
echo 'client_id=YOUR_REDDIT_CLIENT_ID' >> .env
echo 'client_secret=YOUR_REDDIT_CLIENT_SECRET' >> .env
echo 'user_agent=YOUR_APP_NAME' >> .env

# 5. Run
streamlit run app.py
```

App opens at `http://localhost:8501`.

### Getting Reddit API credentials

1. Go to [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
2. Click "Create App" → choose "script"
3. Copy `client_id` (under the app name) and `client_secret`
4. Set `user_agent` to any descriptive string e.g. `"stock-sentiment-app/1.0"`

---

## Tech Stack

| Tool | Role |
|---|---|
| Streamlit | UI framework |
| yfinance | Yahoo Finance news feed |
| gnews | Google News scraper |
| praw | Reddit API client |
| vaderSentiment | NLP sentiment scoring |
| python-dotenv | Environment variable management |

---

## Disclaimer

This tool is for educational and portfolio demonstration purposes only. Sentiment scores are based on publicly available text data and NLP heuristics — they are not financial advice and should not be used as the sole basis for investment decisions.

---

## Author

**Valérie Vienne** — AI Automation Engineer  
[valerie-vienne.com](https://valerie-vienne.com) · [GitHub](https://github.com/ValerieVienne)  
Available for freelance on [Upwork](https://upwork.com)

---

## Credits

This project was co-created with [Claude AI](https://claude.ai) (Anthropic) — used for documentation and architecture description.
