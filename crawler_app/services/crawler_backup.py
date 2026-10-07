import json
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from crawler_app.models import CrawledPage
from crawler_app.services.nlp import analyze_text


def crawl_page(url):
    response = requests.get(
        url,
        timeout=10,
        headers={"User-Agent": "DarkWebIntelligenceFramework/1.0"}
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.title.get_text(strip=True) if soup.title else ""
    content = soup.get_text(" ", strip=True)

    nlp_result = analyze_text(content)

    return {
        "url": url,
        "title": title,
        "content": content,
        "category": nlp_result["category"],
        "sentiment": nlp_result["sentiment"],
        "entities": nlp_result["entities"],
    }


def save_crawled_page(url):
    data = crawl_page(url)

    page = CrawledPage.objects.create(
        url=data["url"],
        title=data["title"],
        content=data["content"],
        category=data["category"],
        sentiment=data["sentiment"],
        entities=json.dumps(data["entities"]),
        status="Completed",
    )

    return page


def extract_links(url):
    response = requests.get(
        url,
        timeout=10,
        headers={"User-Agent": "DarkWebIntelligenceFramework/1.0"}
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
