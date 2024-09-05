# 1. 베이스 이미지 선택
FROM python:3.12-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 필요 파일 복사
COPY requirements.txt ./

# 4. 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 5. 앱 소스 코드 복사
COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5051"]