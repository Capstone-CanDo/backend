from rest_framework import serializers
from .models import Travel

class TravelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Travel
        fields = ["id", "destination", "start_date", "end_date", "created_at"]
        read_only_fields = ["id", "created_at"]

        