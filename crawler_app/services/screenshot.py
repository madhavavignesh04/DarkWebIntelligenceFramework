from playwright.sync_api import sync_playwright


def capture_screenshot(url, output_path):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page(
            viewport={"width": 1280, "height": 720}
        )

        page.goto(url, wait_until="domcontentloaded", timeout=30000)

        page.screenshot(
            path=output_path,
            full_page=True
        )

        browser.close()

    return output_path
