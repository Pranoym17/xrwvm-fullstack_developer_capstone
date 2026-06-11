import json
import os
from pathlib import Path
import requests
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv(
    'backend_url', default="http://localhost:3030")
sentiment_analyzer_url = os.getenv(
    'sentiment_analyzer_url',
    default="http://localhost:5050/")

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "database" / "data"


def _load_json(filename, key):
    with open(DATA_DIR / filename, encoding="utf-8") as json_file:
        return json.load(json_file)[key]


def _fallback_get(endpoint):
    dealers = _load_json("dealerships.json", "dealerships")
    reviews = _load_json("reviews.json", "reviews")

    if endpoint == "/fetchDealers":
        return dealers
    if endpoint.startswith("/fetchDealers/"):
        state = endpoint.rsplit("/", 1)[1]
        if state == "All":
            return dealers
        return [dealer for dealer in dealers if dealer["state"] == state]
    if endpoint.startswith("/fetchDealer/"):
        dealer_id = int(endpoint.rsplit("/", 1)[1])
        return [dealer for dealer in dealers if dealer["id"] == dealer_id]
    if endpoint.startswith("/fetchReviews/dealer/"):
        dealer_id = int(endpoint.rsplit("/", 1)[1])
        return [review for review in reviews if review["dealership"] == dealer_id]
    if endpoint == "/fetchReviews":
        return reviews
    return {}


def get_request(endpoint, **kwargs):
    request_url = backend_url + endpoint
    try:
        response = requests.get(request_url, params=kwargs, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return _fallback_get(endpoint)


def analyze_review_sentiments(text):
    request_url = sentiment_analyzer_url + "analyze/" + text
    try:
        response = requests.get(request_url, timeout=5)
        response.raise_for_status()
        return response.json().get("sentiment", "neutral")
    except requests.RequestException:
        lowered = text.lower()
        if any(word in lowered for word in ["fantastic", "great", "excellent", "good"]):
            return "positive"
        if any(word in lowered for word in ["bad", "poor", "terrible", "awful"]):
            return "negative"
        return "neutral"


def post_review(data_dict):
    try:
        response = requests.post(
            backend_url + "/insert_review",
            json=data_dict,
            timeout=5,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return data_dict
