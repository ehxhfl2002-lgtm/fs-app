#!/usr/bin/env python3
"""
배포 환경에서 데이터베이스 초기화 스크립트
"""

import os
import urllib.request
import zipfile
from db_setup import CorpCodeDBManager

def download_corpcode_data():
    """
    배포 환경에서 Open DART 회사코드 데이터 다운로드
    """
    try:
        import requests
        
        # 환경변수 로딩 (배포 환경 고려)
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass  # 배포 환경에서는 dotenv가 없을 수 있음
        
        api_key = os.getenv('DART_API_KEY')
        if not api_key or api_key == 'your_dart_api_key_here':
            print(f"❌ DART_API_KEY가 설정되지 않았습니다. 현재 값: {api_key}")
            return False
        
        print(f"✅ DART_API_KEY 확인됨: {api_key[:8]}...")  # 앞 8자만 표시
        
        print("🔄 Open DART에서 회사코드 데이터를 다운로드 중...")
        
        # 데이터 디렉터리 생성
        os.makedirs('./data', exist_ok=True)
        
        # API 호출
        url = "https://opendart.fss.or.kr/api/corpCode.xml"
        params = {'crtfc_key': api_key}
        
        response = requests.get(url, params=params, timeout=30)
        
        print(f"🔍 API 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            # 응답 내용 확인
            if len(response.content) < 1000:
                print(f"⚠️ 응답 내용이 너무 짧습니다: {response.content[:200]}...")
                return False
            
            # ZIP 파일 저장
            zip_path = './data/CORPCODE.zip'
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            print(f"📁 ZIP 파일 크기: {len(response.content):,} bytes")
            
            # ZIP 파일 압축 해제
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall('./data')
                print("✅ 회사코드 데이터 다운로드 완료")
                return True
            except zipfile.BadZipFile:
                print(f"❌ ZIP 파일이 손상되었습니다. 내용: {response.content[:200]}...")
                return False
        else:
            print(f"❌ 다운로드 실패: HTTP {response.status_code}")
            print(f"📄 응답 내용: {response.text[:500]}...")
            return False
    
    except Exception as e:
        print(f"❌ 다운로드 오류: {str(e)}")
        return False

def init_database():
    """데이터베이스 초기화"""
    try:
        print("🔧 데이터베이스 초기화 중...")
        
        # 회사코드 데이터 다운로드
        if not download_corpcode_data():
            print("❌ 회사코드 데이터 다운로드 실패")
            return False
        
        # 데이터베이스 설정
        db_manager = CorpCodeDBManager()
        
        # XML을 데이터베이스로 변환
        if db_manager.xml_to_database('./data/CORPCODE.xml'):
            stats = db_manager.get_stats()
            print(f"✅ 데이터베이스 초기화 완료: {stats['total_companies']:,}개 회사")
            return True
        else:
            print("❌ 데이터베이스 변환 실패")
            return False
    
    except Exception as e:
        print(f"❌ 데이터베이스 초기화 오류: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 배포용 데이터베이스 초기화")
    print("=" * 50)
    
    if init_database():
        print("🎉 초기화 성공!")
    else:
        print("💥 초기화 실패!")
        exit(1)
