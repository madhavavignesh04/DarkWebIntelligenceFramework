from google import genai
import os
import time

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)


def analyze_with_gemini(text):

    prompt = f"""
You are an AI analyst for an academic cybersecurity research system.

Analyze only the supplied webpage text.

Give:
1. Short summary
2. Main category
3. Suspicious indicators
4. Brief risk explanation

Do not provide instructions for illegal activity,
credential theft, malware use, or evasion.

Webpage text:
{text[:8000]}
"""

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
            )

            return response.text

        except Exception as error:

            error_text = str(error)

            if "503" in error_text or "UNAVAILABLE" in error_text:
                if attempt < 2:
                    time.sleep(5 * (2 ** attempt))
                    continue

            return "Gemini AI temporarily unavailable."
