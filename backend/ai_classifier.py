"""
ai_classifier.py
-----------------
A simple, fully offline, keyword-based "AI" Lead Classifier (the AI Bonus
requirement). It looks at the free-text requirement the lead submitted and:

  1. Assigns a CATEGORY by scoring the text against keyword lists for each
     category and picking the category with the highest match count.
     Falls back to "General" if nothing matches.

  2. Assigns a PRIORITY (High / Medium / Low) based on urgency-signalling
     keywords, with a length-based heuristic as a tiebreaker.

This is intentionally rule-based rather than calling an external AI/LLM API,
so the whole system keeps working fully on localhost with zero extra
dependencies or API keys.
"""
from typing import Tuple

# Keywords for each category. Order doesn't matter; categories are scored
# by counting how many of their keywords appear in the requirement text.
CATEGORY_KEYWORDS = {
    "AI Automation": [
        "ai", "artificial intelligence", "automation", "automate", "chatbot",
        "bot", "rpa", "workflow automation", "intelligent automation",
        "gpt", "llm", "voice assistant", "process automation",
    ],
    "Web Development": [
        "website", "web app", "web application", "web development",
        "frontend", "front-end", "backend", "back-end", "full stack",
        "fullstack", "react", "next.js", "wordpress", "e-commerce",
        "ecommerce", "landing page", "cms", "web portal", "webpage",
    ],
    "Mobile App": [
        "mobile app", "mobile application", "android app", "ios app",
        "android", "ios", "flutter", "react native", "mobile development",
        "app development", "play store", "app store", "smartphone app",
    ],
    "Machine Learning": [
        "machine learning", "ml model", "predictive model", "model training",
        "neural network", "deep learning", "computer vision", "nlp",
        "natural language processing", "recommendation system",
        "forecasting model", "image recognition",
    ],
    "Data Analytics": [
        "data analysis", "data analytics", "analytics", "business intelligence",
        "bi dashboard", "data visualization", "reporting tool", "data science",
        "data pipeline", "etl", "dashboarding", "data warehouse", "insights",
    ],
}

# Keywords that signal an urgent / high-value lead.
HIGH_PRIORITY_KEYWORDS = [
    "urgent", "asap", "immediately", "critical", "emergency", "enterprise",
    "large scale", "large-scale", "big project", "high budget", "deadline",
    "production", "launch soon", "right away", "as soon as possible",
]

# Keywords that signal a low-intent / exploratory lead.
LOW_PRIORITY_KEYWORDS = [
    "just exploring", "just curious", "maybe", "thinking about", "not sure",
    "someday", "in the future", "just browsing", "no rush", "casual inquiry",
    "just asking",
]


def classify_lead(requirement: str) -> Tuple[str, str]:
    """
    Classify a lead's requirement text.
    Returns a tuple of (category, priority).
    """
    text = (requirement or "").lower()

    # ---- Category classification: highest keyword-match count wins ----
    best_category = "General"
    best_score = 0
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > best_score:
            best_score = score
            best_category = category

    # ---- Priority classification ----
    if any(kw in text for kw in HIGH_PRIORITY_KEYWORDS):
        priority = "High"
    elif any(kw in text for kw in LOW_PRIORITY_KEYWORDS):
        priority = "Low"
    else:
        # No explicit urgency signal: use requirement detail/length as a
        # lightweight proxy for seriousness of intent.
        word_count = len(text.split())
        priority = "Medium" if word_count >= 4 else "Low"

    return best_category, priority
