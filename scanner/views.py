from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from .models import ScanResult
from .serializers import ScanRequestSerializer, ScanResultSerializer
from .services import analyze_url
from explanations.services import generate_explanation

# Create your views here.
class ScanView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ScanRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        url = serializer.validated_data["url"]
        travel_id = serializer.validated_data.get("travel_id")

        # 모델 실행
        try:
            raw = analyze_url(url)
        except Exception as e:
            return Response(
                {"error": "모델 실행 오류", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 2. XAI 설명 생성
        try:
            explanation = generate_explanation(url, raw)
        except Exception:
            explanation = None  # GPT 실패해도 스캔 결과는 저장

        # DB 저장
        scan = ScanResult.objects.create(
            user=request.user,
            travel_id=travel_id,
            url=url,
            is_phishing=raw["is_phishing"],
            explanation=explanation, 
        )

        return Response(
            ScanResultSerializer(scan).data,
            status=status.HTTP_201_CREATED,
        )

class ScanHistoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ScanResultSerializer

    def get_queryset(self):
        qs = ScanResult.objects.filter(user=self.request.user)

        # 쿼리파라미터로 필터링
        travel_id = self.request.query_params.get("travel_id")
        risk_level = self.request.query_params.get("risk_level")
        is_phishing = self.request.query_params.get("is_phishing")

        if travel_id:
            qs = qs.filter(travel_id=travel_id)
        if risk_level:
            qs = qs.filter(risk_level=risk_level)
        if is_phishing is not None:
            qs = qs.filter(is_phishing=is_phishing.lower() == "true")

        return qs
    
class ScanResultDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ScanResultSerializer

    def get_queryset(self):
        return ScanResult.objects.filter(user=self.request.user)

