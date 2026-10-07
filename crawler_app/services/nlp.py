import spacy
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

nltk.download("vader_lexicon")

nlp = spacy.load("en_core_web_sm")
sia = SentimentIntensityAnalyzer()


def analyze_text(text):
    doc = nlp(text)

    entities = [
        {
            "text": ent.text,
            "label": ent.label_
        }
        for ent in doc.ents
    ]

    sentiment_score = sia.polarity_scores(text)["compound"]

    if sentiment_score >= 0.05:
        sentiment = "Positive"
    elif sentiment_score <= -0.05:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    return {
        "sentiment": sentiment,
        "entities": entities
    }


def classify_category(text):
    text = text.lower()

    if any(word in text for word in ["bitcoin", "crypto", "wallet", "payment"]):
        return "Cryptocurrency"

    if any(word in text for word in ["login", "password", "account", "credential"]):
        return "Credentials"

    if any(word in text for word in ["malware", "virus", "ransomware", "trojan"]):
        return "Malware"

    if any(word in text for word in ["market", "shop", "product", "price"]):
        return "Marketplace"

    return "General"


def analyze_text(text):
    doc = nlp(text)

    entities = [
        {
            "text": ent.text,
            "label": ent.label_
        }
        for ent in doc.ents
    ]

    sentiment_score = sia.polarity_scores(text)["compound"]

    if sentiment_score >= 0.05:
        sentiment = "Positive"
    elif sentiment_score <= -0.05:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    category = classify_category(text)

    return {
        "sentiment": sentiment,
        "entities": entities,
        "category": category,
    }
