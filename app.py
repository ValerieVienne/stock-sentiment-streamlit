import streamlit as st
import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import time
from datetime import datetime, timedelta
import os
import praw
from pygooglenews import GoogleNews
from dotenv import load_dotenv


load_dotenv() # to load .env file
# Initialize Reddit API (you need credentials -> in .env file)
reddit = praw.Reddit(
    client_id=os.getenv('client_id'),
    client_secret=os.getenv('client_secret'),
    user_agent=os.getenv('user_agent')
)

# Get the UNIX timestamp for 7 days ago
seven_days_ago = time.time() - (7 * 24 * 60 * 60)


# Sentiment analyzer
analyzer = SentimentIntensityAnalyzer()


def get_yahoo_news_headlines(ticker):
    stock = yf.Ticker(ticker)
    #print(stock)
    news_items = stock.news
    #print(news_items[0])
    news_data = []
    for item in news_items[:10]:  # Limit to first 10 news
        click_url = item["content"].get("canonicalUrl", {})
        news_data.append({
            "headline": item["content"].get("title", "No title available"),
            "link": click_url.get('url', "#"),
            "summary": item["content"].get("summary", "No publisher")  # using publisher name instead of scraping
        })
    #print(news_data)
    return news_data


# Function to get Google News
def get_google_news(ticker):
    gn = GoogleNews(lang='en')
    search = gn.search(ticker)

    entries = search['entries']
    #print(entries)
    news_list = []
    for entry in entries[:20]:  # limit
        news_list.append({
            "headline": entry.get('title', ''),
            "link": entry.get('link', ''),
            "summary": entry.get('summary_1', '') #on purpose because summary has only text links
        })
    return news_list


# Function to get Reddit posts
def get_reddit_posts(ticker):
    subreddit = reddit.subreddit("stocks+investing+wallstreetbets+StockMarket+options+pennystocks")
    posts = subreddit.search(ticker, sort='new', limit=100)
    # Filter posts: high upvote ratio AND enough comments
    filtered_posts = [
        post for post in posts 
        if post.upvote_ratio >= 0.75 and post.num_comments >= 20 and post.created_utc >= seven_days_ago # ✅
    ]
    # Sort filtered posts by popularity (score + 2 * comments)
    sorted_posts = sorted(
        filtered_posts, 
        key=lambda post: post.score + (2 * post.num_comments), 
        reverse=True
    )
    # Select top 20 posts
    top_posts = sorted_posts[:20]

    news_list = []
    for post in top_posts:
        news_list.append({
            "headline": post.title,
            "link": f"https://www.reddit.com{post.permalink}",
            "summary": post.selftext[:200]  # shorten
        })
    return news_list


def analyze_sentiment(news_list):
    scores = []
    weights = []
    for news_item in news_list:
        text = f"{news_item['headline']} {news_item['summary']}"
        score = analyzer.polarity_scores(text)['compound']
        if abs(score) > 0.05:
            scores.append(score)
            weights.append(abs(score))  # Stronger scores have more weight
    if scores:
        weighted_avg = sum(s * w for s, w in zip(scores, weights)) / sum(weights)
    else:
        weighted_avg = 0
    return weighted_avg



def make_recommendation(score):
    if score > 0.3:
        return "Buy 😃🟢"
    elif score < -0.3:
        return "Sell 😞🔴"
    else:
        return "Hold 😐🟡"



def render_animated_sentiment_bar(score):
    """
    Renders an animated colored sentiment bar based on real sentiment score.
    """
    # Separate positive and negative widths
    positive_width = max(0, score) * 100
    negative_width = max(0, -score) * 100

    # Pick color
    if score > 0.3:
        bar_color = "linear-gradient(to right, #a8e6cf, #56ab2f)"  # Green
    elif score < -0.3:
        bar_color = "linear-gradient(to right, #ff758c, #ff7eb3)"  # Red
    else:
        bar_color = "linear-gradient(to right, #ffe259, #ffa751)"  # Yellow

    # Animated bar
    placeholder = st.empty()

    for percent in range(0, int(max(positive_width, negative_width))+1, 2):
        bar_html = f"""
            <div style="background: lightgray; border-radius: 10px; padding: 3px;">
                <div style="
                    width: {percent}%;
                    background: {bar_color};
                    padding: 10px;
                    border-radius: 7px;
                    text-align: center;
                    color: white;
                    font-weight: bold;
                    transition: width 0.5s;
                ">
                    {score:.2f}
                </div>
            </div>
        """
        placeholder.markdown(bar_html, unsafe_allow_html=True)
        time.sleep(0.02)

import time




# --- Streamlit UI ---
st.set_page_config(page_title="Stock Sentiment Tracker", layout="centered")

st.title("📈 Stock Sentiment Tracker")
st.write("Analyze latest news sentiment and get a quick Buy/Hold/Sell signal.")

# User input for ticker
ticker = st.text_input("Enter stock ticker (e.g., AAPL, TSLA):", value="AAPL")

# User selects Source
source = st.selectbox(
    "Select News Source",
    ("Yahoo News", "Google News", "Reddit")
)

if st.button("Analyze"):
    with st.spinner("Fetching news and analyzing..."):
        if source == "Google News":
            headlines = get_google_news(ticker)
        elif source == "Reddit":
            headlines = get_reddit_posts(ticker)
        elif source == "Yahoo News":
            headlines = get_yahoo_news_headlines(ticker)
        else:
            headlines = []

        if headlines:
            sentiment = analyze_sentiment(headlines)
            recommendation = make_recommendation(sentiment)

            st.subheader(f"📊 Sentiment Score:")
            render_animated_sentiment_bar(sentiment)
            st.success(f"💡 Recommendation: **{recommendation}**")

            
            st.markdown("### 📰 Latest Headlines & Summaries")

            for item in headlines:
                st.markdown(f"#### [{item['headline']}]({item['link']})")
                st.caption(item['summary'])
                st.markdown("---")

        else:
            st.error("Couldn't find news for this ticker.")
