import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
    redirect_info = ""
    if redirect.get("redirect_count", 0) > 0:
        redirect_info = f"""
- 리다이렉션 {redirect['redirect_count']}회 발생
- 최종 도달 URL: {redirect['final_url']}
- 경로: {' → '.join(redirect['chain'])}
"""
    prompt = f"""
당신은 여행자를 위한 URL 보안 분석 전문가입니다.

[분석 결과]
- URL: {url}
- 판정: {"피싱 의심" if is_phishing else "정상"}
- 주요 위험 요소:
{chr(10).join(f"  · {feature}: 기여도 {value:+.2f}" for feature, value in top_features)}

위 정보를 바탕으로 여행자가 이해하기 쉽게 2~3문장으로 설명해주세요.
- 기술 용어 없이 일상적인 언어로 작성
- 왜 위험한지 또는 왜 안전한지 구체적으로 설명
- 리다이렉션이 있으면 언급
- 여행 중 주의사항 한 문장 포함
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()