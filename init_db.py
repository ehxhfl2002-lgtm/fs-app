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
        from dotenv import load_dotenv
        import requests
        
        load_dotenv()
        
        api_key = os.getenv('DART_API_KEY')
        if not api_key or api_key == 'your_dart_api_key_here':
            print("❌ DART_API_KEY가 설정되지 않았습니다.")
            return False
        
        print("🔄 Open DART에서 회사코드 데이터를 다운로드 중...")
        
        # 데이터 디렉터리 생성
        os.makedirs('./data', exist_ok=True)
        
        # API 호출
        url = "https://opendart.fss.or.kr/api/corpCode.xml"
        params = {'crtfc_key': api_key}
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            # ZIP 파일 저장
            zip_path = './data/CORPCODE.zip'
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            # ZIP 파일 압축 해제
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall('./data')
            
            print("✅ 회사코드 데이터 다운로드 완료")
            return True
        else:
            print(f"❌ 다운로드 실패: HTTP {response.status_code}")
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
