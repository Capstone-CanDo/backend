from rest_framework import serializers
from .models import ScanResult

class ScanRequestSerializer(serializers.Serializer):
    url = serializers.URLField()
    travel_id = serializers.IntegerField(required=False, allow_null=True)

class ScanResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanResult
        fields = [
            "id", "url", "is_phishing", "explanation", "travel", "created_at"
        ]
        read_only_fields = fields
        