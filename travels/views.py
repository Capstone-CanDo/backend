from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Travel
from .serializers import TravelSerializer

# Create your views here.
class TravelListCreateView(generics.ListCreateAPIView):
    serializer_class = TravelSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TravelDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TravelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Travel.objects.filter(user=self.request.user)
