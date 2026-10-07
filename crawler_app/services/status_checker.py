import requests
from concurrent.futures import ThreadPoolExecutor


def check_url(url):
    try:
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "DarkWebIntelligenceFramework/1.0"
            }
        )

        return {
            "url": url,
            "status_code": response.status_code,
            "status": "Online"
        }

    except Exception as error:
        return {
            "url": url,
            "status_code": None,
            "status": "Offline",
            "error": str(error)
        }


def check_urls(urls, max_workers=5):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(check_url, urls))

    return results
