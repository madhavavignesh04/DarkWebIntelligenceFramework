import os
from django.core.management.base import BaseCommand
from crawler_app.services.crawler import recursive_crawl


class Command(BaseCommand):
    help = "Automatically crawl configured seed URLs"

    def handle(self, *args, **options):
        seed_urls = os.getenv("CRAWL_SEED_URLS", "")
        urls = [url.strip() for url in seed_urls.split(",") if url.strip()]

        if not urls:
            self.stdout.write(
                self.style.WARNING("No seed URLs configured.")
            )
            return

        for url in urls:
            try:
                self.stdout.write(f"Starting crawl: {url}")
                recursive_crawl(url, max_depth=1, max_pages=10)
                self.stdout.write(self.style.SUCCESS(f"Finished: {url}"))
            except Exception as error:
                self.stderr.write(f"Failed to crawl {url}: {error}")
