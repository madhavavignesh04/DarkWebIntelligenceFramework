import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from crawler_app.services.gemini_ai import analyze_with_gemini
from crawler_app.models import CrawledPage
from crawler_app.services.nlp import analyze_text
from crawler_app.services.profiling import profile_content
from crawler_app.services.screenshot import capture_screenshot


TOR_PROXIES = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050",
}


def get_proxies(url):
    if ".onion" in url:
        return TOR_PROXIES
    return None


def crawl_page(url):
    response = requests.get(
        url,
        timeout=15,
        headers={"User-Agent": "DarkWebIntelligenceFramework/1.0"},
        proxies=get_proxies(url),
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.title.get_text(strip=True) if soup.title else ""
    content = soup.get_text(" ", strip=True)

    nlp_result = analyze_text(content)
    profile_result = profile_content(content)
    ai_result = analyze_with_gemini(content)

    return {
        "url": url,
        "title": title,
        "content": content,
        "category": nlp_result["category"],
        "sentiment": nlp_result["sentiment"],
        "entities": nlp_result["entities"],
        "risk_score": profile_result["risk_score"],
        "risk_level": profile_result["risk_level"],
        "detected": profile_result["detected"],          
        "ai_summary": ai_result,
        "ai_category": nlp_result["category"],
       "ai_risk_reason": (
    "Gemini AI analysis completed successfully."
    if not ai_result.startswith("Gemini AI temporarily unavailable.")
    else "Gemini AI is temporarily unavailable. Rule-based risk profiling was used."
),
        
    }


def save_crawled_page(url):
    data = crawl_page(url)

    screenshot_path = capture_screenshot(
        url,
        f"screenshots/page_{CrawledPage.objects.count() + 1}.png"
    )

    page = CrawledPage.objects.create(
        url=data["url"],
        title=data["title"],
        content=data["content"],
        category=data["category"],
        sentiment=data["sentiment"],
        entities=json.dumps(data["entities"]),
        risk_score=data["risk_score"],
        risk_level=data["risk_level"],
        ai_summary=data.get("ai_summary", ""),
        ai_category=data.get("ai_category", ""),
        ai_risk_reason=data.get("ai_risk_reason", ""),
        screenshot_path=screenshot_path,
        status="Completed",
    )

    return page


def extract_links(url):
    response = requests.get(
        url,
        timeout=15,
        headers={"User-Agent": "DarkWebIntelligenceFramework/1.0"},
        proxies=get_proxies(url),
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    links = []

    for link in soup.find_all("a", href=True):
        full_url = urljoin(url, link["href"])

        if full_url.startswith(("http://", "https://")):
            links.append(full_url)

    return list(set(links))


def recursive_crawl(start_url, max_depth=2):
    visited = set()
    queue = [(start_url, 0)]

    while queue:
        current_url, depth = queue.pop(0)

        if current_url in visited:
            continue

        if depth > max_depth:
            continue

        visited.add(current_url)

        try:
            save_crawled_page(current_url)

            links = extract_links(current_url)

            for link in links:
                if link not in visited:
                    queue.append((link, depth + 1))

        except Exception as error:
            print(f"Error crawling {current_url}: {error}")

    return visited

