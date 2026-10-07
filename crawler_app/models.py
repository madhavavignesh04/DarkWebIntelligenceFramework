from django.db import models


class CrawledPage(models.Model):
    url = models.URLField(max_length=500)
    title = models.CharField(max_length=300, blank=True)
    content = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    sentiment = models.CharField(max_length=50, blank=True)
    entities = models.TextField(blank=True)
    status = models.CharField(max_length=50, default="Pending")
    risk_score = models.IntegerField(default=0)
    risk_level = models.CharField(max_length=20, default="Low")
    ai_summary = models.TextField(blank=True)
    ai_category = models.CharField(max_length=100, blank=True)
    ai_risk_reason = models.TextField(blank=True)
    screenshot_path = models.CharField(max_length=500, blank=True)
    crawled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or self.url
