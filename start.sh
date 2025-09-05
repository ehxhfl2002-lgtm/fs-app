#!/bin/bash

# 배포용 시작 스크립트

echo "🚀 재무제표 시각화 웹앱 시작 중..."

# 데이터베이스 초기화 (한 번만 실행)
if [ ! -f "./data/corp_codes.db" ]; then
    echo "📦 데이터베이스 초기화 중..."
    python init_db.py
else
    echo "✅ 데이터베이스 파일 확인됨"
fi

# 앱 시작
echo "🌐 웹앱 시작..."
python app.py
