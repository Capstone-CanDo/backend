from django.db import models
from django.conf import settings

# Create your models here.
class ScanResult(models.Model):
    RISK_CHOICES = [("위험", "LOW"), ("안전", "HIGH")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="scan_results")
    travel = models.ForeignKey("travels.Travel", on_delete=models.SET_NULL, null=True, blank=True, related_name="scan_results")
    url = models.URLField(max_length=2048)
    is_phishing = models.CharField(max_length=10, choices=RISK_CHOICES)
    explanation = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    