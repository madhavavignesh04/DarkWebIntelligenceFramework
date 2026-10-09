from django.shortcuts import render, redirect
from django.db.models import Count
from django.db.models.functions import TruncDate

from .models import CrawledPage
from .services.crawler import save_crawled_page, recursive_crawl


def dashboard(request):
    if request.method == "POST":
        url = request.POST.get("url", "").strip()
        crawl_type = request.POST.get("crawl_type", "single")

        if url:
            try:
                if crawl_type == "recursive":
                    max_pages = int(request.POST.get("max_pages", 10))
                    max_depth = int(request.POST.get("max_depth", 1))

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

    risk_data = list(
        pages.values("risk_level")
        .annotate(count=Count("id"))
        .order_by("risk_level")
    )

    category_data = list(
        pages.values("category")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    daily_data = list(
        pages.annotate(day=TruncDate("crawled_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )

    context = {
        "total_pages": pages.count(),
        "high_risk": pages.filter(risk_level="High").count(),
        "medium_risk": pages.filter(risk_level="Medium").count(),
        "low_risk": pages.filter(risk_level="Low").count(),

        "risk_labels": [
            item["risk_level"] or "Unknown"
            for item in risk_data
        ],
        "risk_values": [
            item["count"]
            for item in risk_data
        ],

        "category_labels": [
            item["category"] or "Unknown"
            for item in category_data
        ],
        "category_values": [
            item["count"]
            for item in category_data
        ],

        "daily_labels": [
            item["day"].strftime("%d %b")
            for item in daily_data
            if item["day"]
        ],
        "daily_values": [
            item["count"]
            for item in daily_data
            if item["day"]
        ],
    }

    return render(
        request,
        "crawler_app/analytics.html",
        context,
    )
    
