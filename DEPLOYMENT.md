# 🚀 재무제표 시각화 웹앱 배포 가이드

## 📋 배포 전 체크리스트

- [x] Flask 앱 배포 설정 완료
- [x] 환경변수 설정 파일 준비
- [x] 데이터베이스 초기화 스크립트 준비
- [x] .gitignore 설정 완료
- [ ] API 키 발급 (DART + Gemini)
- [ ] GitHub 저장소 생성
- [ ] 배포 플랫폼 선택

## 🐙 GitHub 업로드

### 1. 로컬 Git 저장소 초기화
```bash
cd /Users/phm_100/Desktop/vibecoding-infren/FS-PROJECT
git init
git add .
git commit -m "Initial commit: 재무제표 시각화 웹앱"
```

### 2. GitHub 저장소 생성
1. [GitHub](https://github.com) 로그인
2. "New repository" 클릭
3. 저장소 이름: `financial-dashboard` (또는 원하는 이름)
4. Public 선택 (무료 배포를 위해)
5. "Create repository" 클릭

### 3. 원격 저장소 연결 및 푸시
```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

## 🌐 Render.com 배포 (추천!)

### 1. Render.com 가입
- [Render.com](https://render.com) 접속
- GitHub 계정으로 가입

### 2. 웹 서비스 생성
1. Dashboard에서 "New" → "Web Service" 클릭
2. GitHub 저장소 연결
3. 다음 설정 입력:
   - **Name**: `financial-dashboard`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`

### 3. 환경변수 설정
Environment 탭에서 다음 변수들 추가:
- `DART_API_KEY`: Open DART API 키
- `GEMINI_API_KEY`: Google Gemini API 키  
- `FLASK_ENV`: `production`

### 4. 배포 완료!
- 몇 분 후 `https://your-app-name.onrender.com`에서 접속 가능

## 🚄 Railway 배포

### 1. Railway 가입
- [Railway](https://railway.app) 접속
- GitHub 계정으로 가입

### 2. 프로젝트 생성
1. "New Project" 클릭
2. "Deploy from GitHub repo" 선택
3. 저장소 선택

### 3. 환경변수 설정
Variables 탭에서 API 키들 설정

### 4. 도메인 설정
Settings에서 Public Domain 생성

## ⚡ Vercel 배포 (정적 호스팅)

Vercel은 Python Flask를 직접 지원하지 않지만, Serverless Functions로 배포 가능합니다.

### 1. vercel.json 파일 생성
```json
{
  "functions": {
    "app.py": {
      "runtime": "python3.9"
    }
  },
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

### 2. Vercel CLI로 배포
```bash
npm i -g vercel
vercel
```

## 🔧 배포 후 설정

### 1. API 키 발급
- **Open DART**: [opendart.fss.or.kr](https://opendart.fss.or.kr)
- **Google Gemini**: [aistudio.google.com](https://aistudio.google.com)

### 2. 환경변수 설정
각 플랫폼의 Environment Variables 섹션에서:
```
DART_API_KEY=실제_다트_API_키
GEMINI_API_KEY=실제_제미나이_API_키
FLASK_ENV=production
```

### 3. 도메인 연결 (선택사항)
- 커스텀 도메인이 있다면 각 플랫폼에서 설정 가능
- 무료 서브도메인으로도 충분히 사용 가능

## 🐛 트러블슈팅

### 빌드 실패 시
1. `requirements.txt` 확인
2. Python 버전 확인 (`runtime.txt`)
3. 환경변수 설정 확인

### 앱 시작 실패 시
1. 포트 설정 확인 (`PORT` 환경변수)
2. API 키 설정 확인
3. 로그 확인

### 데이터베이스 오류 시
1. `init_db.py` 스크립트 실행 확인
2. DART API 키 유효성 확인
3. 네트워크 연결 확인

## 💡 배포 팁

1. **무료 한도**: Render는 750시간/월 무료 (충분함)
2. **잠들기**: 15분 비활성 시 앱이 잠들어감 (첫 접속 시 조금 느릴 수 있음)
3. **로그 모니터링**: 각 플랫폼에서 실시간 로그 확인 가능
4. **자동 배포**: GitHub push 시 자동으로 재배포됨

## 🎉 배포 완료!

배포가 완료되면:
- 웹 브라우저에서 배포된 URL 접속
- 회사 검색 기능 테스트
- AI 분석 기능 테스트 (API 키 필요)
- 모바일에서도 접속 테스트

문제가 있다면 플랫폼의 로그를 확인하거나 위 트러블슈팅 가이드를 참고하세요!
