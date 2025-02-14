from flask import Flask, jsonify, request
import requests
import redis
import os
import json

app = Flask(__name__)

# Connect to Redis
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

API_KEY = os.getenv("NEWS_API_KEY")  # Store in .env file later
BASE_URL = "https://newsapi.org/v2/everything"

CACHE_TTL = 1800  # Cache for 30 minutes

def fetch_news(category):
    """Fetch news from API or return cached version"""
    cache_key = f"news:{category}"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        return json.loads(cached_data)  # Return cached response

    # Fetch from NewsAPI
    url = f"{BASE_URL}?q={category}&language=en&apiKey={API_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        redis_client.setex(cache_key, CACHE_TTL, json.dumps(data))  # Cache response
        return data
    
    return {"error": "Failed to fetch news"}

@app.route("/news", methods=["GET"])
def get_news():
    category = request.args.get("category", "tariff")
    news = fetch_news(category)
    return jsonify(news)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
