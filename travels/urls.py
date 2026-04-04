from django.urls import path
from .views import *

app_name = 'travels'

urlpatterns = [
    path('info/', TravelListCreateView.as_view(), name="travel-info"),
    path('info/<int:pk>/', TravelDetailView.as_view(), name="travel-detail")
]