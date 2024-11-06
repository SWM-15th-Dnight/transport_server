# 1. 베이스 이미지 선택
FROM python:3.12-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 시간대 환경 변수 설정
ENV TZ=Asia/Seoul

# 시간대 정보 설치 및 패키지 업데이트
RUN apt-get update && apt-get install -y tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 3. 필요 파일 복사
COPY requirements.txt ./

ENV TZ=Asia/Seoul
RUN ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime && echo "Asia/Seoul" > /etc/timezone

# 4. 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 5. 앱 소스 코드 복사
COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5051"]