# LYNK Backend

## Project Overview

LYNK Backend는 해외여행자를 대상으로 QR 코드 기반 피싱(Quishing) 공격을 예방하기 위한 Django 서버입니다.

본 서버는 사용자 관리, 여행 정보 관리, URL 분석 요청 처리, SHAP 기반 설명 제공, 웹페이지 번역 및 위험 문구 탐지 기능을 담당하며, 머신러닝 기반 악성 URL 분석은 별도의 FastAPI AI 서버와 연동하여 수행합니다.

---

## Tech Stack

### Backend
- Python 3.11
- Django
- Django REST Framework

### Database
- PostgreSQL

### External Service
- FastAPI-based AI Server
- Google Cloud Translation API

### Deployment
- Docker

---

## Project Structure

```text
backend
├── .env_example          # 환경 변수 예시 파일
├── .github               # GitHub Actions 및 저장소 설정
├── accounts              # 사용자 계정 및 인증 관련 기능
├── configs               # 프로젝트 전역 설정
├── explanations          # SHAP 기반 위험도 설명 생성 기능
├── scanner               # URL 분석 및 QR 스캔 관련 기능
├── travels               # 여행 정보 및 여행 설정 관리 기능
├── utils                 # 공통 유틸리티 모듈
├── Dockerfile            # Docker 이미지 생성 설정
├── manage.py             # Django 실행 파일
├── requirements.txt      # Python 패키지 의존성 목록
└── README.md
```

### Module Description

| Module | Description |
|----------|----------|
| accounts | 사용자 계정 관리 및 인증 기능 |
| scanner | URL 분석 및 악성 URL 탐지 기능 |
| explanations | SHAP 기반 위험도 설명 생성 기능 |
| travels | 여행 국가 및 여행 정보 관리 기능 |
| configs | Django 프로젝트 설정 |
| utils | 공통 기능 및 유틸리티 |

---

## Prerequisites

다음 소프트웨어가 설치되어 있어야 합니다.

- Python 3.11 이상
- pip
- Git
- PostgreSQL
- Docker (선택)

---

## Installation

### 1. Repository Clone

```bash
git clone https://github.com/Capstone-CanDo/backend.git
cd backend
```

### 2. Virtual Environment

가상환경을 생성합니다.

```bash
python -m venv venv
```

#### Mac/Linux

```bash
source venv/bin/activate
```

#### Windows

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

필요한 패키지를 설치합니다.

```bash
pip install -r requirements.txt
```

### 4. Environment Variables

`.env_example` 파일을 참고하여 `.env` 파일을 생성합니다.

AI 분석 기능을 사용하기 위해 FastAPI 기반 AI 서버가 먼저 실행되어 있어야 하며, `.env` 파일의 `FASTAPI_URL` 값을 AI 서버 주소로 설정해야 합니다.

예시:

```env
SECRET_KEY=
DEBUG=

FASTAPI_URL=
OPENAI_API_KEY=
```

---

## Database

PostgreSQL 데이터베이스를 생성한 후 `.env` 파일에 데이터베이스 연결 정보를 설정합니다.

예시:

```env
PGDATABASE=
PGUSER=
PGPASSWORD=
PGHOST=
PGPORT=
```

---

## Build

Docker 이미지를 생성합니다.

```bash
docker build -t lynk-backend .
```

---

## Run Server

### AI Server

본 프로젝트는 별도의 FastAPI 기반 AI 서버와 연동됩니다.

AI 서버를 먼저 실행한 후 `.env` 파일의 `FASTAPI_URL` 값을 설정해야 정상적으로 URL 분석 기능을 사용할 수 있습니다.

예시:

```env
FASTAPI_URL=http://localhost:8001
```

### Local Environment

데이터베이스 마이그레이션을 수행합니다.

```bash
python manage.py migrate
```

서버를 실행합니다.

```bash
python manage.py runserver
```

기본 실행 주소:

```text
http://127.0.0.1:8000
```

---

## Docker Run

Docker 컨테이너를 실행합니다.

```bash
docker run -p 8000:8000 lynk-backend
```

---

## Test

테스트를 실행합니다.

```bash
python manage.py test
```

---

## Open Source Libraries

본 프로젝트는 다음과 같은 오픈소스 라이브러리를 활용합니다.

- Django
- Django REST Framework
- PostgreSQL
- OpenAI API
- Google Cloud Translation API
- Docker

---
