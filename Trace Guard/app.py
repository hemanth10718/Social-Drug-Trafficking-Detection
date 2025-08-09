from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import pandas as pd
import tweepy
import instaloader
from telethon import TelegramClient, sync
from telethon.sessions import StringSession
import nest_asyncio
import asyncio
import os
import re
import random
import time
from transformers import pipeline
from fpdf import FPDF
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this for production

# ======== CONFIGURATION ======== (Directly in the file)
# Instagram credentials
INSTA_USERNAME = "your_instagram_username"  # Replace with your credentials
INSTA_PASSWORD = "your_instagram_password"

# Twitter credentials
TWITTER_BEARER_TOKEN = "your_twitter_bearer_token"

# Telegram credentials (get from https://my.telegram.org)
TELEGRAM_API_ID = 1234567  # Replace with your API ID
TELEGRAM_API_HASH = "your_telegram_api_hash"

# Proxy settings (if needed)
PROXIES = []
if os.path.exists('valid_proxies.txt'):
    with open('valid_proxies.txt', 'r') as f:
        PROXIES = [p.strip() for p in f.readlines() if p.strip()]

# ======== HELPER FUNCTIONS ========
def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

def get_proxy():
    return random.choice(PROXIES) if PROXIES else None

# ======== SCRAPER FUNCTIONS ========
def scrape_twitter(username, limit=10):
    try:
        client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
        user = client.get_user(username=username)
        
        if not user.data:
            return pd.DataFrame(), f"Twitter user @{username} not found"
        
        tweets = client.get_users_tweets(
            id=user.data.id,
            max_results=min(limit, 100),
            tweet_fields=['created_at', 'public_metrics', 'text']
        )
        
        if not tweets.data:
            return pd.DataFrame(), f"No tweets found for @{username}"
        
        data = [{
            "platform": "Twitter",
            "username": username,
            "id": tweet.id,
            "created_at": tweet.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "text": clean_text(tweet.text),
            "likes": tweet.public_metrics['like_count'],
            "retweets": tweet.public_metrics['retweet_count']
        } for tweet in tweets.data]
        
        return pd.DataFrame(data), None
    
    except Exception as e:
        return pd.DataFrame(), f"Twitter error: {str(e)}"

def scrape_instagram(username, limit=10):
    try:
        L = instaloader.Instaloader()
        
        if PROXIES:
            L.context.proxy = get_proxy()
        
        try:
            L.login(INSTA_USERNAME, INSTA_PASSWORD)
        except Exception as e:
            return pd.DataFrame(), f"Instagram login failed: {str(e)}"
        
        try:
            profile = instaloader.Profile.from_username(L.context, username)
        except Exception:
            return pd.DataFrame(), f"Instagram profile @{username} not found"
        
        posts = []
        for i, post in enumerate(profile.get_posts()):
            if i >= limit:
                break
                
            posts.append({
                "platform": "Instagram",
                "username": username,
                "id": post.shortcode,
                "created_at": post.date_utc.strftime("%Y-%m-%d %H:%M:%S"),
                "text": clean_text(post.caption),
                "likes": post.likes,
                "comments": post.comments
            })
            time.sleep(random.uniform(1, 3))
        
        return pd.DataFrame(posts), None
    
    except Exception as e:
        return pd.DataFrame(), f"Instagram error: {str(e)}"

def scrape_telegram(channel_username, limit=10):
    try:
        if not channel_username.startswith('@'):
            channel_username = '@' + channel_username
            
        async def async_scraper():
            client = TelegramClient(
                StringSession(),
                TELEGRAM_API_ID,
                TELEGRAM_API_HASH
            )
            
            await client.start()
            
            try:
                channel = await client.get_entity(channel_username)
                messages = []
                
                async for message in client.iter_messages(channel, limit=limit):
                    messages.append({
                        "platform": "Telegram",
                        "username": channel_username,
                        "id": message.id,
                        "created_at": message.date.strftime("%Y-%m-%d %H:%M:%S"),
                        "text": clean_text(message.text),
                        "views": getattr(message, 'views', None)
                    })
                
                return pd.DataFrame(messages), None
            except ValueError:
                return pd.DataFrame(), f"Channel not found: {channel_username}"
            except Exception as e:
                return pd.DataFrame(), f"Telegram error: {str(e)}"
            finally:
                await client.disconnect()
        
        nest_asyncio.apply()
        return asyncio.run(async_scraper())
        
    except Exception as e:
        return pd.DataFrame(), f"Telegram setup failed: {str(e)}"

# ======== REPORT FUNCTIONS ========
def check_suspicious(scraped_file, reference_file="reference_data.csv"):
    try:
        scraped = pd.read_csv(scraped_file)
        reference = pd.read_csv(reference_file)
        
        scraped_text = " ".join(scraped['text'].fillna('').apply(clean_text))
        reference_text = " ".join(reference['text'].fillna('').apply(clean_text))
        
        vectorizer = TfidfVectorizer(stop_words='english')
        vectors = vectorizer.fit_transform([scraped_text, reference_text])
        similarity = cosine_similarity(vectors[0], vectors[1])[0][0]
        
        return min(100, max(0, round(similarity * 100, 2)))
    
    except Exception:
        return 0.0

def generate_nlp_report(data_file, score, output_pdf):
    try:
        data = pd.read_csv(data_file)
        texts = " ".join(data['text'].fillna('').apply(clean_text))
        
        # Summary
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        summary = summarizer(texts[:1024], max_length=130, min_length=30)[0]['summary_text']
        
        # Word cloud
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(texts)
        wc_file = "temp_wc.png"
        wordcloud.to_file(wc_file)
        
        # PDF Report
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Social Media Activity Analysis Report", ln=1, align='C')
        
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"Suspicious Content Score: {score}%", ln=1)
        
        pdf.set_font("Arial", '', 12)
        pdf.multi_cell(0, 10, f"Key Findings:\n{summary}")
        
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Frequent Terms", ln=1)
        pdf.image(wc_file, x=10, y=30, w=190)
        
        pdf.output(output_pdf)
        os.remove(wc_file)
        return True
    
    except Exception:
        return False

# ======== FLASK ROUTES ========
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/instagram')
def instagram_analysis():
    return render_template('instagram.html')

@app.route('/twitter')
def twitter_analysis():
    return render_template('twitter.html')

@app.route('/telegram')
def telegram_analysis():
    return render_template('telegram.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    platform = request.form.get('platform')
    username = request.form.get('username').strip()
    limit = request.form.get('limit', default=10, type=int)
    
    limit = max(1, min(100, limit))  # Ensure between 1-100
    
    if not username:
        flash('Please enter a username')
        return redirect(url_for(f'{platform}_analysis'))
    
    try:
        if platform == 'twitter':
            data, error = scrape_twitter(username, limit)
        elif platform == 'instagram':
            data, error = scrape_instagram(username, limit)
        elif platform == 'telegram':
            data, error = scrape_telegram(username, limit)
        else:
            flash('Invalid platform selected')
            return redirect(url_for('home'))
        
        if error:
            flash(error)
            return redirect(url_for(f'{platform}_analysis'))
        
        if data.empty:
            flash('No data found for this user')
            return redirect(url_for(f'{platform}_analysis'))
        
        scraped_file = f"temp_{username}.csv"
        data.to_csv(scraped_file, index=False)
        
        score = check_suspicious(scraped_file)
        report_file = f"report_{username}.pdf"
        generate_nlp_report(scraped_file, score, report_file)
        
        os.remove(scraped_file)
        return render_template('report.html',
                           username=username,
                           platform=platform,
                           score=score,
                           report_file=report_file)
    
    except Exception as e:
        flash(f'Analysis failed: {str(e)}')
        return redirect(url_for(f'{platform}_analysis'))

@app.route('/download/<filename>')
def download_file(filename):
    if not os.path.exists(filename):
        flash('File not found')
        return redirect(url_for('home'))
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    # Verify Telegram credentials
    if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
        print("Error: Telegram API credentials not configured!")
    else:
        app.run(debug=True)