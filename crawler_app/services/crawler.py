import json
import os
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from crawler_app.models import CrawledPage
from crawler_app.services.nlp import analyze_text
from crawler_app.services.profiling import profile_content
from crawler_app.services.screenshot import capture_screenshot


# Tor proxy configuration
TOR_PROXIES = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050",
}


def get_proxies(url):
    parsed_url = urlparse(url)

    if parsed_url.hostname and parsed_url.hostname.endswith(".onion"):
        return TOR_PROXIES

    return None


def validate_url(url):
    parsed_url = urlparse(url)

    if parsed_url.scheme not in ("http", "https"):
        raise ValueError("Only HTTP and HTTPS URLs are supported.")

    if not parsed_url.hostname:
        raise ValueError("Invalid URL.")

    return parsed_url


def fetch_page(url):
    validate_url(url)

    response = requests.get(
        url,
        timeout=15,
        headers={
            "User-Agent": "DarkWebIntelligenceFramework/1.0"
        },
        proxies=get_proxies(url),
    )

    response.raise_for_status()

    return response.text


def analyze_content(content):
    # Existing NLP analysis
    nlp_result = analyze_text(content)

    # Existing rule-based risk profiling
    profile_result = profile_content(content)

    summary = (
        "Rule-based summary: " + content[:300]
        if content
        else "No webpage text available."
    )

    return {
        "category": nlp_result["category"],
        "sentiment": nlp_result["sentiment"],
        "entities": nlp_result["entities"],
        "risk_score": profile_result["risk_score"],
        "risk_level": profile_result["risk_level"],
        "detected": profile_result["detected"],
        "ai_summary": summary,
        "ai_category": nlp_result["category"],
        "ai_risk_reason": (
            "Rule-based risk profiling classified this page as "
            f"{profile_result['risk_level']} risk."
        ),
    }


def crawl_page(url):
    html = fetch_page(url)

    soup = BeautifulSoup(html, "html.parser")

    title = (
        soup.title.get_text(strip=True)
        if soup.title
        else ""
    )

    content = soup.get_text(" ", strip=True)

    analysis = analyze_content(content)

    return {
        "url": url,
        "title": title,
        "content": content,
        **analysis,
    }


def save_crawled_page(url):
    data = crawl_page(url)

    # Screenshot is optional.
    # A screenshot failure should not prevent saving the page.
    screenshot_path = ""

    try:
        os.makedirs("screenshots", exist_ok=True)

        filename = (
            f"screenshots/page_{CrawledPage.objects.count() + 1}.png"
        )

        screenshot_path = capture_screenshot(url, filename) or ""

    except Exception as error:
        print(f"Screenshot failed for {url}: {error}")

    page = CrawledPage.objects.create(
        url=data["url"],
        title=data["title"],
        content=data["content"],
        category=data["category"],
        sentiment=data["sentiment"],
        entities=json.dumps(data["entities"]),
        risk_score=data["risk_score"],
        risk_level=data["risk_level"],
        ai_summary=data["ai_summary"],
        ai_category=data["ai_category"],
        ai_risk_reason=data["ai_risk_reason"],
        screenshot_path=screenshot_path,
        status="Completed",
    )

    return page


def extract_links(url):
    html = fetch_page(url)

    soup = BeautifulSoup(html, "html.parser")

    base_host = urlparse(url).hostname
    links = set()

    for link in soup.find_all("a", href=True):
        full_url = urljoin(url, link["href"])
        parsed_link = urlparse(full_url)

        if (
            parsed_link.scheme in ("http", "https")
            and parsed_link.hostname == base_host
        ):
            links.add(full_url)

    return list(links)


def recursive_crawl(start_url, max_depth=1, max_pages=10):
    validate_url(start_url)

    visited = set()
    queue = [(start_url, 0)]

    while queue and len(visited) < max_pages:
        current_url, depth = queue.pop(0)

        if current_url in visited:
            continue

        if depth > max_depth:
            continue

        visited.add(current_url)

        try:
            save_crawled_page(current_url)
            print(f"Successfully crawled: {current_url}")

            if depth < max_depth:
                links = extract_links(current_url)

                for link in links:
                    if link not in visited and len(queue) < max_pages:
                        queue.append((link, depth + 1))

        except Exception as error:
            print(f"Error crawling {current_url}: {error}")

    return visited

