from django.shortcuts import render, redirect
from .models import CrawledPage
from .services.crawler import save_crawled_page, recursive_crawl


def dashboard(request):
    error_message = None

    if request.method == "POST":
        url = request.POST.get("url", "").strip()
        crawl_type = request.POST.get("crawl_type", "single")

        if url:
            try:
                if crawl_type == "recursive":
                    max_pages = int(request.POST.get("max_pages", 10))
                    max_depth = int(request.POST.get("max_depth", 1))

                    # Keep crawling within safe limits
                    max_pages = max(1, min(max_pages, 50))
                    max_depth = max(0, min(max_depth, 3))

                    recursive_crawl(
                        url,
                        max_depth=max_depth,
                        max_pages=max_pages,
                    )
                else:
                    save_crawled_page(url)

            except Exception as error:
                print("Crawl error:", error)

        return redirect("dashboard")

    pages = CrawledPage.objects.order_by("-id")

    context = {
        "pages": pages,
        "total_pages": pages.count(),
        "high_risk": pages.filter(risk_level="High").count(),
        "medium_risk": pages.filter(risk_level="Medium").count(),
        "low_risk": pages.filter(risk_level="Low").count(),
    }

    return render(request, "crawler_app/dashboard.html", context)


def analytics(request):
    pages = CrawledPage.objects.all()

    context = {
        "total_pages": pages.count(),
        "high_risk": pages.filter(risk_level="High").count(),
        "medium_risk": pages.filter(risk_level="Medium").count(),
        "low_risk": pages.filter(risk_level="Low").count(),
    }

    return render(request, "crawler_app/analytics.html", context)
    
