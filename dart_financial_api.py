#!/usr/bin/env python3
"""
Open DART API를 사용한 재무정보 조회 모듈
"""

import os
import requests
import pandas as pd
from dotenv import load_dotenv
from typing import Dict, List, Optional

# 환경변수 로드
load_dotenv()

class DartFinancialAPI:
    def __init__(self):
        """Open DART 재무정보 API 클래스 초기화"""
        self.api_key = os.getenv('DART_API_KEY')
        self.base_url = "https://opendart.fss.or.kr/api"
        
        if not self.api_key or self.api_key == 'your_dart_api_key_here':
            raise ValueError("DART_API_KEY가 .env 파일에 설정되지 않았습니다.")
    
    def get_financial_statements(self, corp_code: str, bsns_year: str, reprt_code: str = "11011") -> Dict:
        """
        단일회사 주요계정 재무정보 조회
        
        Args:
            corp_code (str): 회사코드 (8자리)
            bsns_year (str): 사업연도 (4자리, 예: "2023")
            reprt_code (str): 보고서코드
                - 11011: 사업보고서 (기본값)
                - 11012: 반기보고서
                - 11013: 1분기보고서
                - 11014: 3분기보고서
        
        Returns:
            Dict: API 응답 데이터
        """
        try:
            url = f"{self.base_url}/fnlttSinglAcnt.json"
            params = {
                'crtfc_key': self.api_key,
                'corp_code': corp_code,
                'bsns_year': bsns_year,
                'reprt_code': reprt_code
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # 에러 체크
            if data.get('status') != '000':
                error_code = data.get('status')
                error_message = data.get('message', '알 수 없는 오류')
                
                # 013 오류에 대한 상세 설명
                if error_code == '013':
                    detailed_error = f"조회된 데이터가 없습니다. 가능한 원인:\n"
                    detailed_error += f"• {bsns_year}년도 재무제표가 공시되지 않았을 수 있습니다\n"
                    detailed_error += f"• 회사코드 {corp_code}가 올바르지 않을 수 있습니다\n"
                    detailed_error += f"• 보고서 유형({reprt_code})에 해당하는 데이터가 없을 수 있습니다\n"
                    detailed_error += f"• 다른 연도나 보고서 유형을 시도해보세요"
                    
                    return {
                        'success': False,
                        'error': f"API 오류 {error_code}: {detailed_error}",
                        'error_code': error_code,
                        'suggestions': {
                            'try_other_years': [str(int(bsns_year)-1), str(int(bsns_year)-2)],
                            'try_other_reports': ['11012', '11013', '11014'] if reprt_code == '11011' else ['11011']
                        }
                    }
                
                return {
                    'success': False,
                    'error': f"API 오류 {error_code}: {error_message}",
                    'error_code': error_code
                }
            
            return {
                'success': True,
                'data': data
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f"API 요청 오류: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"처리 오류: {str(e)}"
            }
    
    def get_financial_summary_with_fallback(self, corp_code: str, bsns_year: str, reprt_code: str = "11011") -> Dict:
        """
        재무정보 조회 (실패 시 자동으로 다른 연도/보고서 유형 시도)
        """
        # 1차 시도: 요청된 연도와 보고서 유형
        result = self.get_financial_statements(corp_code, bsns_year, reprt_code)
        if result['success']:
            return self.get_financial_summary(corp_code, bsns_year, reprt_code)
        
        # 013 오류인 경우 자동으로 다른 옵션들 시도
        if result.get('error_code') == '013':
            # 2차 시도: 이전 연도들
            for year in [str(int(bsns_year)-1), str(int(bsns_year)-2)]:
                try:
                    fallback_result = self.get_financial_statements(corp_code, year, reprt_code)
                    if fallback_result['success']:
                        print(f"✅ {year}년도 데이터로 대체 조회 성공")
                        return self.get_financial_summary(corp_code, year, reprt_code)
                except:
                    continue
            
            # 3차 시도: 다른 보고서 유형 (원래 연도)
            other_reports = ['11012', '11013', '11014'] if reprt_code == '11011' else ['11011']
            for report in other_reports:
                try:
                    fallback_result = self.get_financial_statements(corp_code, bsns_year, report)
                    if fallback_result['success']:
                        print(f"✅ {report} 보고서로 대체 조회 성공")
                        return self.get_financial_summary(corp_code, bsns_year, report)
                except:
                    continue
        
        # 모든 시도 실패 시 원래 오류 반환
        return {
            'success': False,
            'error': result['error'],
            'error_code': result.get('error_code'),
            'suggestions': result.get('suggestions', {})
        }

    def get_financial_summary(self, corp_code: str, bsns_year: str, reprt_code: str = "11011") -> Dict:
        """
        재무제표 주요 지표 요약 정보 조회
        
        Args:
            corp_code (str): 회사코드
            bsns_year (str): 사업연도
            reprt_code (str): 보고서코드
        
        Returns:
            Dict: 주요 재무지표 요약
        """
        result = self.get_financial_statements(corp_code, bsns_year, reprt_code)
        
        if not result['success']:
            return result
        
        try:
            financial_data = result['data']['list']
            
            # 주요 계정과목 추출
            summary = {
                'basic_info': {},
                'balance_sheet': {},  # 재무상태표
                'income_statement': {},  # 손익계산서
                'raw_data': financial_data
            }
            
            for item in financial_data:
                account_name = item.get('account_nm', '')
                fs_div = item.get('fs_div', '')  # OFS: 개별, CFS: 연결
                sj_div = item.get('sj_div', '')  # BS: 재무상태표, IS: 손익계산서
                thstrm_amount = item.get('thstrm_amount', '0')
                frmtrm_amount = item.get('frmtrm_amount', '0')
                
                # 기본 정보 저장
                if not summary['basic_info']:
                    summary['basic_info'] = {
                        'corp_code': corp_code,
                        'bsns_year': bsns_year,
                        'reprt_code': reprt_code,
                        'stock_code': item.get('stock_code', ''),
                        'fs_nm': item.get('fs_nm', ''),
                        'currency': item.get('currency', 'KRW')
                    }
                
                # 숫자로 변환 (콤마 제거)
                try:
                    current_amount = int(thstrm_amount.replace(',', '')) if thstrm_amount and thstrm_amount != '-' else 0
                    previous_amount = int(frmtrm_amount.replace(',', '')) if frmtrm_amount and frmtrm_amount != '-' else 0
                except:
                    current_amount = 0
                    previous_amount = 0
                
                # 연결재무제표 우선 (CFS), 없으면 개별재무제표 (OFS)
                if fs_div == 'CFS' or (fs_div == 'OFS' and account_name not in [item['account'] for item in summary['balance_sheet'].values() if isinstance(item, dict)]):
                    
                    if sj_div == 'BS':  # 재무상태표
                        if '자산총계' in account_name or '자산' == account_name:
                            summary['balance_sheet']['total_assets'] = {
                                'account': account_name,
                                'current': current_amount,
                                'previous': previous_amount
                            }
                        elif '부채총계' in account_name or '부채' == account_name:
                            summary['balance_sheet']['total_liabilities'] = {
                                'account': account_name,
                                'current': current_amount,
                                'previous': previous_amount
                            }
                        elif '자본총계' in account_name or '자본' == account_name:
                            summary['balance_sheet']['total_equity'] = {
                                'account': account_name,
                                'current': current_amount,
                                'previous': previous_amount
                            }
                    
                    elif sj_div == 'IS':  # 손익계산서
                        if '매출액' in account_name:
                            summary['income_statement']['revenue'] = {
                                'account': account_name,
                                'current': current_amount,
                                'previous': previous_amount
                            }
                        elif '영업이익' in account_name:
                            summary['income_statement']['operating_profit'] = {
                                'account': account_name,
                                'current': current_amount,
                                'previous': previous_amount
                            }
                        elif '당기순이익' in account_name:
                            summary['income_statement']['net_profit'] = {
                                'account': account_name,
                                'current': current_amount,
                                'previous': previous_amount
                            }
            
            return {
                'success': True,
                'summary': summary
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"데이터 처리 오류: {str(e)}"
            }
    
    def get_multi_year_data(self, corp_code: str, start_year: int, end_year: int, reprt_code: str = "11011") -> Dict:
        """
        여러 연도의 재무데이터 조회
        
        Args:
            corp_code (str): 회사코드
            start_year (int): 시작 연도
            end_year (int): 종료 연도
            reprt_code (str): 보고서코드
        
        Returns:
            Dict: 다년도 재무데이터
        """
        multi_year_data = {
            'years': [],
            'revenue': [],
            'operating_profit': [],
            'net_profit': [],
            'total_assets': [],
            'total_liabilities': [],
            'total_equity': []
        }
        
        errors = []
        
        for year in range(start_year, end_year + 1):
            # fallback 메커니즘 사용하여 더 안정적인 데이터 조회
            result = self.get_financial_summary_with_fallback(corp_code, str(year), reprt_code)
            
            if result['success']:
                summary = result['summary']
                multi_year_data['years'].append(year)
                
                # 손익계산서 데이터
                multi_year_data['revenue'].append(
                    summary['income_statement'].get('revenue', {}).get('current', 0)
                )
                multi_year_data['operating_profit'].append(
                    summary['income_statement'].get('operating_profit', {}).get('current', 0)
                )
                multi_year_data['net_profit'].append(
                    summary['income_statement'].get('net_profit', {}).get('current', 0)
                )
                
                # 재무상태표 데이터
                multi_year_data['total_assets'].append(
                    summary['balance_sheet'].get('total_assets', {}).get('current', 0)
                )
                multi_year_data['total_liabilities'].append(
                    summary['balance_sheet'].get('total_liabilities', {}).get('current', 0)
                )
                multi_year_data['total_equity'].append(
                    summary['balance_sheet'].get('total_equity', {}).get('current', 0)
                )
            else:
                errors.append(f"{year}년: {result['error']}")
        
        return {
            'success': len(multi_year_data['years']) > 0,
            'data': multi_year_data,
            'errors': errors
        }
    
    @staticmethod
    def format_amount(amount):
        """금액을 읽기 쉬운 형태로 포맷팅"""
        if amount == 0:
            return "0"
        
        if abs(amount) >= 1_000_000_000_000:  # 조 단위
            return f"{amount / 1_000_000_000_000:.1f}조"
        elif abs(amount) >= 100_000_000:  # 억 단위
            return f"{amount / 100_000_000:.1f}억"
        elif abs(amount) >= 10_000:  # 만 단위
            return f"{amount / 10_000:.1f}만"
        else:
            return f"{amount:,}"
    
    @staticmethod
    def get_report_type_name(reprt_code):
        """보고서 코드를 이름으로 변환"""
        report_types = {
            '11011': '사업보고서',
            '11012': '반기보고서', 
            '11013': '1분기보고서',
            '11014': '3분기보고서'
        }
        return report_types.get(reprt_code, '알 수 없음')


# 테스트 함수
def test_api():
    """API 테스트 함수"""
    try:
        api = DartFinancialAPI()
        
        # 삼성전자 재무정보 조회 테스트 (회사코드: 00126380)
        print("🔍 삼성전자 2023년 재무정보 조회 테스트...")
        result = api.get_financial_summary("00126380", "2023")
        
        if result['success']:
            summary = result['summary']
            print("✅ 조회 성공!")
            print(f"📊 {summary['basic_info']['fs_nm']}")
            
            # 재무상태표
            bs = summary['balance_sheet']
            print("\n📈 재무상태표:")
            if 'total_assets' in bs:
                print(f"  자산총계: {api.format_amount(bs['total_assets']['current'])}")
            if 'total_liabilities' in bs:
                print(f"  부채총계: {api.format_amount(bs['total_liabilities']['current'])}")
            if 'total_equity' in bs:
                print(f"  자본총계: {api.format_amount(bs['total_equity']['current'])}")
            
            # 손익계산서
            is_data = summary['income_statement']
            print("\n💰 손익계산서:")
            if 'revenue' in is_data:
                print(f"  매출액: {api.format_amount(is_data['revenue']['current'])}")
            if 'operating_profit' in is_data:
                print(f"  영업이익: {api.format_amount(is_data['operating_profit']['current'])}")
            if 'net_profit' in is_data:
                print(f"  당기순이익: {api.format_amount(is_data['net_profit']['current'])}")
        else:
            print(f"❌ 조회 실패: {result['error']}")
    
    except Exception as e:
        print(f"❌ 테스트 오류: {str(e)}")


if __name__ == "__main__":
    test_api()
