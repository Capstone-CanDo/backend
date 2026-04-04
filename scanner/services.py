import httpx
import os

#FASTAPI 모델 연동 코드 
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8001")

def analyze_url(url: str) -> dict: 
    try:
        response = httpx.post(
            f"{FASTAPI_URL}/predict",
            json={"url": url},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()
    
    except httpx.TimeoutException:
        raise Exception("모델 서버 응답 시간 초과")
    except httpx.ConnectError:
        raise Exception("FastAPI 서버가 실행 중이지 않습니다.")