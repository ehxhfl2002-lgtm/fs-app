# Open DART 회사코드 다운로더

Open DART API를 사용하여 공시대상회사의 고유번호가 포함된 회사코드 파일을 다운로드하는 Python 스크립트입니다.

## 🚀 시작하기

### 1. 환경 설정

```bash
# 필요한 패키지 설치
pip install -r requirements.txt
```

### 2. API 키 설정

1. [Open DART](https://opendart.fss.or.kr/) 사이트에서 API 키를 발급받으세요
2. `.env.example` 파일을 복사하여 `.env` 파일을 생성하세요
3. `.env` 파일에 발급받은 API 키를 입력하세요

```bash
cp .env.example .env
```

`.env` 파일 내용:
```
# Open DART API 인증키
DART_API_KEY=your_actual_api_key_here
```

### 3. 스크립트 실행

```bash
python corp_code_downloader.py
```

## 📋 주요 기능

- ✅ Open DART API를 통한 회사코드 ZIP 파일 다운로드
- ✅ ZIP 파일 자동 압축 해제
- ✅ XML 파일 파싱 및 회사 정보 추출
- ✅ 특정 회사명으로 검색 기능
- ✅ 환경변수를 통한 안전한 API 키 관리

## 📊 출력 정보

- 공시대상회사의 고유번호 (8자리)
- 정식회사명칭
- 영문정식회사명칭
- 종목코드 (상장회사의 경우, 6자리)
- 최종변경일자 (YYYYMMDD)

## 🔧 사용 예시

```python
from corp_code_downloader import DartCorpCodeDownloader

# 다운로더 초기화
downloader = DartCorpCodeDownloader()

# 회사코드 파일 다운로드
result = downloader.download_corp_code()

# 특정 회사 검색
if result['success']:
    companies = downloader.search_company(result['xml_file'], "삼성전자")
    for company in companies:
        print(f"{company['corp_name']} - {company['corp_code']}")
```

## 🚨 에러 코드

| 코드 | 설명 |
|------|------|
| 000 | 정상 |
| 010 | 등록되지 않은 키입니다 |
| 011 | 사용할 수 없는 키입니다 |
| 012 | 접근할 수 없는 IP입니다 |
| 013 | 조회된 데이터가 없습니다 |
| 020 | 요청 제한을 초과하였습니다 |

## 📁 파일 구조

```
FS-PROJECT/
├── corp_code_downloader.py    # 메인 스크립트
├── requirements.txt           # 필요한 패키지 목록
├── .env                      # API 키 (git에서 제외됨)
├── .env.example              # API 키 템플릿
├── .gitignore               # Git 무시 파일 목록
├── README.md                # 사용법 설명서
└── downloads/               # 다운로드된 파일들이 저장되는 폴더
    ├── CORPCODE.zip         # 다운로드된 ZIP 파일
    └── CORPCODE.xml         # 압축 해제된 XML 파일
```

## 🚀 배포

### Render.com 무료 배포

1. **GitHub에 프로젝트 업로드**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Render.com 설정**
   - [Render.com](https://render.com) 가입
   - "New Web Service" 선택
   - GitHub 저장소 연결
   - 빌드 명령어: `pip install -r requirements.txt`
   - 시작 명령어: `python app.py`

3. **환경변수 설정**
   - `DART_API_KEY`: Open DART API 키
   - `GEMINI_API_KEY`: Google Gemini API 키
   - `FLASK_ENV`: `production`

### Railway 배포

1. **Railway CLI 설치**
   ```bash
   npm install -g @railway/cli
   ```

2. **배포 명령어**
   ```bash
   railway login
   railway init
   railway up
   ```

## 🔒 보안

- `.env` 파일은 `.gitignore`에 포함되어 Git에 업로드되지 않습니다
- API 키는 절대 코드에 직접 입력하지 마세요
- 배포 시 플랫폼의 환경변수 설정 기능을 사용하세요
