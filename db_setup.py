#!/usr/bin/env python3
"""
CORPCODE.xml 파일을 SQLite 데이터베이스로 변환하는 스크립트
"""

import sqlite3
import xml.etree.ElementTree as ET
import os
from pathlib import Path

class CorpCodeDBManager:
    def __init__(self, db_path="./data/corpcode.db"):
        """
        회사코드 데이터베이스 관리자 초기화
        
        Args:
            db_path (str): SQLite 데이터베이스 파일 경로
        """
        self.db_path = db_path
        self.ensure_data_dir()
        self.init_database()
    
    def ensure_data_dir(self):
        """data 디렉터리가 없으면 생성"""
        data_dir = Path(self.db_path).parent
        data_dir.mkdir(exist_ok=True)
    
    def init_database(self):
        """데이터베이스 테이블 초기화"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 회사코드 테이블 생성
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS companies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    corp_code TEXT UNIQUE NOT NULL,
                    corp_name TEXT NOT NULL,
                    corp_eng_name TEXT,
                    stock_code TEXT,
                    modify_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 검색 성능을 위한 인덱스 생성
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_corp_name ON companies(corp_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_corp_code ON companies(corp_code)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_code ON companies(stock_code)')
            
            conn.commit()
            print("✅ 데이터베이스 테이블 초기화 완료")
    
    def xml_to_database(self, xml_path="./data/CORPCODE.xml"):
        """
        XML 파일을 읽어서 데이터베이스에 저장
        
        Args:
            xml_path (str): CORPCODE.xml 파일 경로
        """
        if not os.path.exists(xml_path):
            print(f"❌ XML 파일을 찾을 수 없습니다: {xml_path}")
            print("먼저 corp_code_downloader.py를 실행하여 회사코드 파일을 다운로드하세요.")
            return False
        
        try:
            print("🔄 XML 파일을 읽는 중...")
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            companies = []
            
            # XML에서 회사 정보 추출
            for list_elem in root.findall('list'):
                corp_code = list_elem.find('corp_code').text if list_elem.find('corp_code') is not None else ''
                corp_name = list_elem.find('corp_name').text if list_elem.find('corp_name') is not None else ''
                corp_eng_name = list_elem.find('corp_eng_name').text if list_elem.find('corp_eng_name') is not None else ''
                stock_code = list_elem.find('stock_code').text if list_elem.find('stock_code') is not None else ''
                modify_date = list_elem.find('modify_date').text if list_elem.find('modify_date') is not None else ''
                
                companies.append((corp_code, corp_name, corp_eng_name, stock_code, modify_date))
            
            print(f"📊 총 {len(companies):,}개 회사 정보를 추출했습니다.")
            
            # 데이터베이스에 저장
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 기존 데이터 삭제
                cursor.execute('DELETE FROM companies')
                
                # 새 데이터 삽입
                cursor.executemany('''
                    INSERT INTO companies (corp_code, corp_name, corp_eng_name, stock_code, modify_date)
                    VALUES (?, ?, ?, ?, ?)
                ''', companies)
                
                conn.commit()
                
                # 결과 확인
                cursor.execute('SELECT COUNT(*) FROM companies')
                count = cursor.fetchone()[0]
                print(f"✅ 데이터베이스에 {count:,}개 회사 정보가 저장되었습니다.")
            
            return True
            
        except Exception as e:
            print(f"❌ 데이터베이스 변환 중 오류 발생: {str(e)}")
            return False
    
    def search_companies(self, query, limit=10):
        """
        회사명으로 회사 검색
        
        Args:
            query (str): 검색할 회사명
            limit (int): 반환할 최대 결과 수
        
        Returns:
            list: 검색 결과 리스트
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 회사명에 검색어가 포함된 회사들 검색 (대소문자 구분 없음)
            cursor.execute('''
                SELECT corp_code, corp_name, corp_eng_name, stock_code, modify_date
                FROM companies
                WHERE corp_name LIKE ? OR corp_eng_name LIKE ?
                ORDER BY 
                    CASE WHEN corp_name = ? THEN 0 ELSE 1 END,
                    LENGTH(corp_name),
                    corp_name
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', query, limit))
            
            results = cursor.fetchall()
            
            # 딕셔너리 형태로 변환
            companies = []
            for result in results:
                companies.append({
                    'corp_code': result[0],
                    'corp_name': result[1],
                    'corp_eng_name': result[2],
                    'stock_code': result[3],
                    'modify_date': result[4]
                })
            
            return companies
    
    def get_company_by_code(self, corp_code):
        """
        회사코드로 회사 정보 조회
        
        Args:
            corp_code (str): 회사코드 (8자리)
        
        Returns:
            dict: 회사 정보 또는 None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT corp_code, corp_name, corp_eng_name, stock_code, modify_date
                FROM companies
                WHERE corp_code = ?
            ''', (corp_code,))
            
            result = cursor.fetchone()
            
            if result:
                return {
                    'corp_code': result[0],
                    'corp_name': result[1],
                    'corp_eng_name': result[2],
                    'stock_code': result[3],
                    'modify_date': result[4]
                }
            return None
    
    def get_stats(self):
        """데이터베이스 통계 정보 반환"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM companies')
            total_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM companies WHERE stock_code != ""')
            listed_count = cursor.fetchone()[0]
            
            return {
                'total_companies': total_count,
                'listed_companies': listed_count,
                'unlisted_companies': total_count - listed_count
            }


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("🏢 회사코드 데이터베이스 설정")
    print("=" * 60)
    
    db_manager = CorpCodeDBManager()
    
    # XML을 데이터베이스로 변환
    if db_manager.xml_to_database():
        print("\n📈 데이터베이스 통계:")
        stats = db_manager.get_stats()
        print(f"   • 총 회사 수: {stats['total_companies']:,}개")
        print(f"   • 상장 회사: {stats['listed_companies']:,}개")
        print(f"   • 비상장 회사: {stats['unlisted_companies']:,}개")
        
        print("\n🔍 검색 테스트:")
        # 삼성 관련 회사 검색 테스트
        samsung_results = db_manager.search_companies("삼성", 3)
        for company in samsung_results:
            print(f"   • {company['corp_name']} (코드: {company['corp_code']}, 종목: {company['stock_code']})")
    else:
        print("❌ 데이터베이스 변환에 실패했습니다.")


if __name__ == "__main__":
    main()
