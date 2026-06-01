import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

FEATURE_LABELS = {
    # Length-based
    "len_url":        "웹 주소 전체가 비정상적으로 길어요",
    "len_hostname":   "사이트 이름 부분이 비정상적으로 길어요",
    "len_TLD":        "주소 끝부분(.com 등)이 이상하게 길어요",
    "len_path":       "주소의 경로 부분이 비정상적으로 길어요",
    "url_depth":      "주소가 여러 단계로 깊게 중첩돼 있어요",
    "len_first_dir":  "첫 번째 경로 이름이 비정상적으로 길어요",

    # Count-based
    "num_http":       "주소에 'http'가 여러 번 반복돼요",
    "num_https":      "보안 연결 없이 일반 http로만 연결돼요",
    "num_www":        "주소에 'www'가 여러 번 반복돼요",
    "num_@":          "주소에 '@' 기호가 있어요",
    "num_?":          "주소에 '?' 기호가 여러 번 포함돼 있어요",
    "num_&":          "주소에 '&' 기호가 여러 번 포함돼 있어요",
    "num_%":          "주소에 '%' 인코딩이 여러 번 사용됐어요",
    "num_#":          "주소에 '#' 기호가 여러 번 포함돼 있어요",
    "num_.":          "주소에 점(.)이 비정상적으로 많아요",
    "num_=":          "주소에 '=' 기호가 여러 번 포함돼 있어요",
    "num__":          "주소에 밑줄(_)이 여러 번 사용됐어요",
    "num_-":          "주소에 하이픈(-)이 비정상적으로 많아요",
    "num_hostname_-": "사이트 이름에 하이픈(-)이 여러 번 들어가 있어요",
    "num_subdomains": "주소 앞에 단계가 여러 겹 붙어 있어요",
    "num_digits":     "주소에 숫자가 비정상적으로 많이 섞여 있어요",
    "num_letters":    "주소의 문자 구성이 이상해요",

    # Existence-based
    "is_ip":          "사이트 이름 대신 숫자 주소(IP)로 직접 연결돼요",
    "is_short_url":   "주소가 단축 URL로 실제 목적지를 숨기고 있어요",
}

FEATURE_CONTEXT = {
    "len_url":        "피싱 사이트는 정상 주소처럼 보이려고 불필요한 문자를 잔뜩 붙여요.",
    "len_hostname":   "신뢰할 수 있는 사이트 이름처럼 보이게 하려고 길게 만드는 경우가 많아요.",
    "len_TLD":        "'.com' 대신 '.com-login.xyz' 같은 식으로 끝부분을 위장해요.",
    "len_path":       "경로가 길면 실제 목적지를 숨기기 쉬워요.",
    "url_depth":      "단계가 많을수록 어느 사이트인지 파악하기 어렵게 만들어요.",
    "len_first_dir":  "첫 경로를 길게 만들어 주소 전체를 복잡하게 위장해요.",
    "num_http":       "'http'를 주소 중간에 넣어 실제 출처를 숨기는 수법이에요.",
    "num_https":      "보안 연결이 없으면 주고받는 정보가 그대로 노출될 수 있어요.",
    "num_www":        "'www'를 반복해 진짜 사이트처럼 보이게 위장하는 수법이에요.",
    "num_@":          "'@' 앞부분은 무시되기 때문에 실제 접속 주소를 숨길 수 있어요.",
    "num_%":          "문자를 %로 인코딩해서 주소를 읽기 어렵게 만들어요.",
    "num_.":          "점이 많으면 주소 구조를 복잡하게 만들어 출처를 숨길 수 있어요.",
    "num_-":          "하이픈을 여러 개 써서 공식 사이트 이름처럼 보이게 위장해요.",
    "num_hostname_-": "사이트 이름에 하이픈이 많으면 공식 도메인을 흉내낸 경우가 많아요.",
    "num_subdomains": "앞에 단계를 여러 겹 붙여 신뢰할 수 있는 주소처럼 보이게 해요.",
    "num_digits":     "숫자가 많으면 자동 생성된 임시 사이트일 가능성이 높아요.",
    "is_ip":          "IP 주소로 직접 연결하면 사이트 신원을 확인하기가 어려워요.",
    "is_short_url":   "단축 URL은 실제 주소를 숨기기 때문에 어디로 가는지 알 수 없어요.",
}

FEW_SHOT_EXAMPLES = """
[예시 - 피싱 의심]
발견된 특징: 주소 길이 매우 김 / 특수문자 다수
출력:
1. 주소가 비정상적으로 길고 '-'와 숫자가 뒤섞여 있어서, 정상 사이트 주소처럼 보이기 어려워요.
2. 이런 패턴은 가짜 사이트가 진짜처럼 보이려고 쓰는 방식이에요.
3. 지금 바로 닫고, 필요한 서비스라면 검색해서 공식 사이트로 직접 들어가세요.
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

    risk_features = [(f, v) for f, v in top_features if v > 0]
    
    if risk_features:
        feature_lines = "\n".join(
            f"  · {FEATURE_LABELS.get(feat, feat)}"
            for feat, v in risk_features
        )
    else:
        # 안전 URL이면 안전 신호를 대신 사용
        safe_features = [(f, v) for f, v in top_features if v < 0]
        feature_lines = "\n".join(
            f"  · {FEATURE_LABELS.get(feat, feat)}"
            for feat, v in safe_features
        )
    # GPT로 자연어 설명 생성
    summary = _ask_gpt(url, is_phishing, top_features, redirect)

    return {
        "method": "shap+gpt",
        "top_features": top_features,
        "summary": summary,
        "redirect": redirect, 
    }


def _ask_gpt(url: str, is_phishing: bool, top_features: list, redirect: dict) -> str:
    # 피처 값을 좀 더 구체적으로 넘기기
    feature_lines = "\n".join(
        f"  · {FEATURE_LABELS.get(feat, feat)} (강도: {'높음' if abs(val) > 0.3 else '낮음'})"
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
- 전문용어 절대 사용 금지
- 반드시 이 링크에서 실제로 발견된 구체적인 특징을 언급할 것
  (예: "주소에 숫자와 특수문자가 섞여 있어요", "클릭 후 3번이나 다른 주소로 이동해요")
- 막연한 일반론("피싱일 수 있어요") 금지 — 이 링크에만 해당하는 설명을 쓸 것
- 어떤 사이트인지 추측하거나 단정하지 말 것
- 3문장: 이 링크에서 발견된 것 → 그래서 어떤 위험인지 → 지금 할 행동

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