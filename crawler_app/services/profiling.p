SUSPICIOUS_KEYWORDS = {
    "credentials": [
        "password",
        "username",
        "login",
        "credential",
        "account"
    ],
    "malware": [
        "malware",
        "ransomware",
        "trojan",
        "virus"
    ],
    "financial": [
        "credit card",
        "bank account",
        "bitcoin",
        "crypto",
        "wallet"
    ],
}


def profile_content(text):
    text = text.lower()

    detected = []

    for category, keywords in SUSPICIOUS_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                detected.append({
                    "category": category,
                    "keyword": keyword
                })

    risk_score = min(len(detected) * 10, 100)

    if risk_score >= 70:
        risk_level = "High"
    elif risk_score >= 30:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "detected": detected
    }
