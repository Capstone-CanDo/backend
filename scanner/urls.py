from django.urls import path
from .views import *

app_name = 'scanner'

urlpatterns = [
    path('scan/', ScanView.as_view(), name="url-scan"),
    path('scan-history/', ScanHistoryView.as_view(), name="scan-history"),
    path('scan-history/<int:pk>/', ScanResultDetailView.as_view(), name="scan-detail-history")
]