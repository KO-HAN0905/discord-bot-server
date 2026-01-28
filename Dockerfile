# Railway 배포용 Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY python_bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 복사
COPY python_bot/ /app/

# 포트 노출
EXPOSE 5000

# 환경 변수 설정
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=5000

# 애플리케이션 실행
CMD ["python", "main.py"]
