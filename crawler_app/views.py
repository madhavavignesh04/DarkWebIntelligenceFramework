from django.shortcuts import render, redirect
from .models import CrawledPage
from .services.crawler import save_crawled_page, recursive_crawl


def dashboard(request):
    if request.method == "POST":
        url = request.POST.get("url")
        crawl_type = request.POST.get("crawl_type")

        if url:
            try:
                if crawl_type == "recursive":
                    recursive_crawl(url, max_depth=1)
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
