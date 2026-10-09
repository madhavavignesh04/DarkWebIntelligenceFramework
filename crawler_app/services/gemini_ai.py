import re


def analyze_with_gemini(text):
    """
    Rule-based webpage analysis.
    No Gemini API required.
    """

    if not text or not text.strip():
        return "Summary: No webpage text available."

    text = text[:8000]
    lower_text = text.lower()

    # 1. Basic summary
    summary = re.sub(r"\s+", " ", text).strip()[:300]

    # 2. Category detection
    if any(word in lower_text for word in ["bitcoin", "crypto", "wallet"]):
        category = "Cryptocurrency"
    elif any(word in lower_text for word in ["login", "password", "credential"]):
        category = "Authentication"
    elif any(word in lower_text for word in ["malware", "ransomware", "exploit"]):
        category = "Cybersecurity"
    else:
        category = "General"

    # 3. Suspicious indicators
    indicators = []

    keywords = [
        "phishing",
        "stolen credentials",
        "malware",
        "ransomware",
        "exploit",
        "stolen data",
    ]

    for keyword in keywords:
        if keyword in lower_text:
            indicators.append(keyword)

    if indicators:
        risk = "High" if len(indicators) >= 3 else "Medium"
        indicator_text = ", ".join(indicators)
    else:
        risk = "Low"
        indicator_text = "No configured keywords detected"

    # 4. Risk explanation
    explanation = (
        f"Rule-based classification: {len(indicators)} configured "
        f"suspicious keyword(s) detected."
    )

    return (
        f"Summary: {summary}\n"
        f"Category: {category}\n"
        f"Suspicious Indicators: {indicator_text}\n"
        f"Risk Level: {risk}\n"
        f"Risk Explanation: {explanation}"
    )
         
