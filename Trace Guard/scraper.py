import os
import re
import random
import time
import pandas as pd
import tweepy
import instaloader
from telethon import TelegramClient
from telethon.sessions import StringSession
import nest_asyncio
import asyncio
from config import Config

# Initialize
nest_asyncio.apply()

# Proxy setup
proxies = []
if os.path.exists('valid_proxies.txt'):
    with open('valid_proxies.txt', 'r') as f:
        proxies = [p.strip() for p in f.readlines() if p.strip()]

def get_proxy():
    return random.choice(proxies) if proxies else None

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

def scrape_twitter(username, limit=10):
    try:
        client = tweepy.Client(bearer_token=Config.TWITTER_BEARER_TOKEN)
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
        
        if proxies:
            L.context.proxy = get_proxy()
        
        try:
            L.login(Config.INSTA_USERNAME, Config.INSTA_PASSWORD)
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
                Config.TELEGRAM_API_ID,
                Config.TELEGRAM_API_HASH
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
        
        return asyncio.run(async_scraper())
        
    except Exception as e:
        return pd.DataFrame(), f"Telegram setup failed: {str(e)}"