FROM python:3.11

# 작업 디렉토리 설정
WORKDIR /app

# requirements 먼저 복사 (캐시 활용)
COPY requirements.txt .

# 라이브러리 설치
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 전체 복사
COPY . .

# migrate & 서버 실행
CMD python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT