#!/usr/bin/env python3
"""
Open DART API를 사용하여 회사코드 파일을 다운로드하는 스크립트
"""

import os
import requests
import zipfile
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

class DartCorpCodeDownloader:
    def __init__(self):
        self.api_key = os.getenv('DART_API_KEY')
        self.base_url = "https://opendart.fss.or.kr/api/corpCode.xml"
        
        if not self.api_key or self.api_key == 'your_dart_api_key_here':
            raise ValueError("DART_API_KEY가 .env 파일에 설정되지 않았습니다.")
    
    def download_corp_code(self, output_dir="./data"):
        """
        회사코드 파일을 다운로드합니다.
        
        Args:
            output_dir (str): 다운로드된 파일을 저장할 디렉토리
        
        Returns:
            dict: 다운로드 결과 정보
        """
        try:
            # 출력 디렉토리 생성
            os.makedirs(output_dir, exist_ok=True)
            
            # API 요청
            params = {
                'crtfc_key': self.api_key
            }
            
            print("회사코드 파일을 다운로드 중...")
            response = requests.get(self.base_url, params=params)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'HTTP 오류: {response.status_code}'
                }
            
            # ZIP 파일로 저장
            zip_filename = os.path.join(output_dir, "CORPCODE.zip")
            with open(zip_filename, 'wb') as f:
                f.write(response.content)
            
            print(f"ZIP 파일 저장 완료: {zip_filename}")
            
            # ZIP 파일 압축 해제
            xml_filename = self.extract_zip(zip_filename, output_dir)
            
            # XML 파일 파싱하여 기본 정보 출력
            corp_info = self.parse_corp_xml(xml_filename)
            
            return {
                'success': True,
                'zip_file': zip_filename,
                'xml_file': xml_filename,
                'total_companies': corp_info['total_count'],
                'sample_companies': corp_info['sample_data']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_zip(self, zip_filename, output_dir):
        """ZIP 파일을 압축 해제합니다."""
        try:
            with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
                zip_ref.extractall(output_dir)
                # XML 파일명 찾기
                xml_files = [f for f in zip_ref.namelist() if f.endswith('.xml')]
                if xml_files:
                    xml_filename = os.path.join(output_dir, xml_files[0])
                    print(f"XML 파일 압축 해제 완료: {xml_filename}")
                    return xml_filename
                else:
                    raise ValueError("ZIP 파일에서 XML 파일을 찾을 수 없습니다.")
        except Exception as e:
            raise Exception(f"ZIP 파일 압축 해제 실패: {str(e)}")
    
    def parse_corp_xml(self, xml_filename, sample_count=5):
        """XML 파일을 파싱하여 회사 정보를 추출합니다."""
        try:
            tree = ET.parse(xml_filename)
            root = tree.getroot()
            
            companies = []
            total_count = 0
            
            for list_elem in root.findall('list'):
                corp_code = list_elem.find('corp_code').text if list_elem.find('corp_code') is not None else ''
                corp_name = list_elem.find('corp_name').text if list_elem.find('corp_name') is not None else ''
                stock_code = list_elem.find('stock_code').text if list_elem.find('stock_code') is not None else ''
                modify_date = list_elem.find('modify_date').text if list_elem.find('modify_date') is not None else ''
                
                companies.append({
                    'corp_code': corp_code,
                    'corp_name': corp_name,
                    'stock_code': stock_code,
                    'modify_date': modify_date
                })
                
                total_count += 1
                
                # 샘플 데이터만 출력
                if total_count <= sample_count:
                    print(f"회사코드: {corp_code}, 회사명: {corp_name}, 종목코드: {stock_code}")
            
            return {
                'total_count': total_count,
                'sample_data': companies[:sample_count],
                'all_data': companies
            }
            
        except Exception as e:
            raise Exception(f"XML 파일 파싱 실패: {str(e)}")
    
    def search_company(self, xml_filename, company_name):
        """특정 회사명으로 회사 정보를 검색합니다."""
        try:
            tree = ET.parse(xml_filename)
            root = tree.getroot()
            
            results = []
            
            for list_elem in root.findall('list'):
                corp_name = list_elem.find('corp_name').text if list_elem.find('corp_name') is not None else ''
                
                if company_name.lower() in corp_name.lower():
                    corp_code = list_elem.find('corp_code').text if list_elem.find('corp_code') is not None else ''
                    stock_code = list_elem.find('stock_code').text if list_elem.find('stock_code') is not None else ''
                    modify_date = list_elem.find('modify_date').text if list_elem.find('modify_date') is not None else ''
                    
                    results.append({
                        'corp_code': corp_code,
                        'corp_name': corp_name,
                        'stock_code': stock_code,
                        'modify_date': modify_date
                    })
            
            return results
            
        except Exception as e:
            raise Exception(f"회사 검색 실패: {str(e)}")


def main():
    """메인 실행 함수"""
    try:
        downloader = DartCorpCodeDownloader()
        
        print("=" * 50)
        print("Open DART 회사코드 다운로더")
        print("=" * 50)
        
        # 회사코드 파일 다운로드
        result = downloader.download_corp_code()
        
        if result['success']:
            print(f"\n✅ 다운로드 완료!")
            print(f"📁 ZIP 파일: {result['zip_file']}")
            print(f"📄 XML 파일: {result['xml_file']}")
            print(f"🏢 총 회사 수: {result['total_companies']:,}개")
            print("\n📊 샘플 회사 정보:")
            print("-" * 30)
            
            # 사용 예시: 특정 회사 검색
            print("\n🔍 삼성전자 검색 결과:")
            xml_file = result['xml_file']
            samsung_results = downloader.search_company(xml_file, "삼성전자")
            
            for company in samsung_results[:3]:  # 상위 3개만 출력
                print(f"- {company['corp_name']} (코드: {company['corp_code']}, 종목: {company['stock_code']})")
                
        else:
            print(f"❌ 다운로드 실패: {result['error']}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        print("\n💡 해결 방법:")
        print("1. .env 파일에 DART_API_KEY를 올바르게 설정했는지 확인")
        print("2. API 키가 유효한지 확인")
        print("3. 인터넷 연결 상태 확인")


if __name__ == "__main__":
    main()
