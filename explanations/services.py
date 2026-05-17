import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

FEATURE_LABELS = {
    "url_length":     "웹 주소가 비정상적으로 길어요",
    "special_chars":  "주소에 이상한 기호가 많아요",
    "domain_age":     "최근에 만들어진 사이트예요",
    "https_used":     "보안 연결이 되어 있어요",
    "redirect_count": "클릭하면 다른 곳으로 자동 이동해요",
    "known_domain":   "알려진 사이트 주소가 아니에요",
}

FEW_SHOT_EXAMPLES = """
[예시 1]
판정: 피싱 의심
의심 이유: 웹 주소가 비정상적으로 길어요 / 주소에 이상한 기호가 많아요
출력:
1. 이 링크는 항공사 예약 사이트처럼 보이지만, 주소가 수상할 정도로 길고 알아보기 힘든 기호들이 섞여 있어요.
2. 개인정보나 결제 정보를 훔치려는 가짜 사이트일 가능성이 높아요.
3. 클릭하지 말고 항공사 공식 앱이나 즐겨찾기에 저장된 주소로 직접 들어가세요.

[예시 2]
판정: 정상
의심 이유: 없음
출력:
1. 이 링크는 잘 알려진 호텔 예약 사이트로, 주소 형태도 정상적이고 안전하게 연결돼요.
2. 현재까지 위험한 신호가 발견되지 않은 안전한 링크예요.
3. 접속해도 괜찮지만, 결제 전에 주소창에 자물쇠 아이콘이 있는지 한 번만 확인해보세요.
"""

def generate_explanation(url: str, raw: dict) -> dict:
    shap_values = raw.get("shap_values", {})
    is_phishing = raw.get("is_phishing", False)
    redirect = raw.get("redirect", {})

    # 기여도 절댓값 기준 top 3 추출
    top_features = sorted(
        shap_values.items(),
        key=lambda x: abs(x[1]),
        reverse=True
    )[:3]

    # GPT로 자연어 설명 생성
    summary = _ask_gpt(url, is_phishing, top_features, redirect)

    return {
        "method": "shap+gpt",
        "top_features": top_features,
        "summary": summary,
        "redirect": redirect, 
    }


def _ask_gpt(url: str, is_phishing: bool, top_features: list, redirect: dict) -> str:
    # 위험 신호(val > 0)만 자연어로 변환, 수치 미노출
    feature_lines = "\n".join(
        f"  · {FEATURE_LABELS.get(feat, feat)}"
        for feat, val in top_features
        if val > 0
    )
    if not feature_lines:
        feature_lines = "  · 특별한 위험 신호가 발견되지 않았어요"

    redirect_note = ""
    if redirect.get("redirect_count", 0) > 0:
        redirect_note = "  · 링크를 클릭하면 전혀 다른 사이트로 자동으로 이동돼요"

    prompt = f"""
당신은 해외여행 중인 20-30대에게 링크 안전 여부를 알려주는 보안 전문가입니다. 

{FEW_SHOT_EXAMPLES}

[작성 규칙]
- 전문용어 절대 사용 금지 (SHAP, 도메인, 피처, 리다이렉션, HTTPS 등)
- 여행 상황에 맞는 표현 사용 (예약 사이트, 항공권, 호텔 등)
- 아래 3가지를 각각 1문장씩 작성
  1. 왜 위험한지 (또는 왜 안전한지)
  2. 한 줄 결론
  3. 지금 당장 할 행동

[실제 분석]
- 판정: {"피싱 의심" if is_phishing else "정상"}
- 의심 이유:
{feature_lines}
{redirect_note}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()