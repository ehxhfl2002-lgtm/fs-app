#!/usr/bin/env python3
"""
Gemini API를 사용한 재무제표 분석 모듈
"""

import os
import json
from typing import Dict, Optional
from dotenv import load_dotenv

try:
    import google.generativeai as genai
except ImportError:
    genai = None
    print("google-generativeai 패키지가 설치되지 않았습니다. pip install google-generativeai 로 설치해주세요.")

# 환경변수 로드
load_dotenv()

class FinancialAnalyzer:
    def __init__(self):
        """Gemini API를 사용한 재무분석기 초기화"""
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.api_key or self.api_key == 'your_gemini_api_key_here':
            raise ValueError("GEMINI_API_KEY가 .env 파일에 설정되지 않았습니다.")
        
        if genai is None:
            raise ImportError("google-generativeai 패키지가 필요합니다.")
        
        # Gemini API 설정
        genai.configure(api_key=self.api_key)
        
        # 사용 가능한 모델 확인 및 설정
        model_options = [
            'gemini-1.5-flash',
            'models/gemini-1.5-flash',
            'gemini-2.0-flash',
            'models/gemini-2.0-flash',
            'gemini-1.5-pro',
            'models/gemini-1.5-pro'
        ]
        
        self.model = None
        last_error = None
        
        for model_name in model_options:
            try:
                self.model = genai.GenerativeModel(model_name)
                print(f"✅ Gemini 모델 초기화 성공: {model_name}")
                break
            except Exception as e:
                last_error = e
                print(f"⚠️ 모델 {model_name} 초기화 실패: {e}")
                continue
        
        if self.model is None:
            print(f"❌ 모든 모델 초기화 실패. 마지막 오류: {last_error}")
            # 사용 가능한 모델 목록 출력
            try:
                models = genai.list_models()
                print("사용 가능한 모델 목록:")
                for model in models:
                    if 'generateContent' in model.supported_generation_methods:
                        print(f"  - {model.name}")
            except:
                pass
            raise ValueError("Gemini 모델을 초기화할 수 없습니다.")
    
    def analyze_financial_data(self, company_name: str, financial_summary: Dict) -> Dict:
        """
        재무제표 데이터를 분석하여 쉬운 설명을 생성
        
        Args:
            company_name (str): 회사명
            financial_summary (dict): 재무제표 요약 데이터
        
        Returns:
            dict: 분석 결과
        """
        try:
            # 재무데이터 준비
            analysis_data = self._prepare_analysis_data(company_name, financial_summary)
            
            # 프롬프트 생성
            prompt = self._create_analysis_prompt(analysis_data)
            
            # Gemini API 호출
            try:
                response = self.model.generate_content(prompt)
                
                # 응답 확인
                if not hasattr(response, 'text') or not response.text:
                    raise ValueError("Gemini에서 유효한 응답을 받지 못했습니다.")
                
                # 응답 파싱
                analysis_result = self._parse_response(response.text)
                
            except Exception as api_error:
                # API 호출 관련 상세 에러 정보 제공
                error_msg = str(api_error)
                if "404" in error_msg and "models" in error_msg:
                    error_msg = "사용 중인 Gemini 모델이 더 이상 지원되지 않습니다. 모델 업데이트가 필요합니다."
                elif "quota" in error_msg.lower():
                    error_msg = "Gemini API 할당량이 초과되었습니다. 잠시 후 다시 시도해주세요."
                elif "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
                    error_msg = "Gemini API 키가 유효하지 않습니다. API 키를 확인해주세요."
                
                raise Exception(f"Gemini API 호출 실패: {error_msg}")
            
            return {
                'success': True,
                'analysis': analysis_result,
                'company_name': company_name
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'분석 중 오류 발생: {str(e)}'
            }
    
    def analyze_financial_trends(self, company_name: str, multi_year_data: Dict) -> Dict:
        """
        다년도 재무 추이를 분석
        
        Args:
            company_name (str): 회사명
            multi_year_data (dict): 다년도 재무데이터
        
        Returns:
            dict: 추이 분석 결과
        """
        try:
            # 추이 데이터 준비
            trend_data = self._prepare_trend_data(company_name, multi_year_data)
            
            # 추이 분석 프롬프트 생성
            prompt = self._create_trend_analysis_prompt(trend_data)
            
            # Gemini API 호출
            try:
                response = self.model.generate_content(prompt)
                
                # 응답 확인
                if not hasattr(response, 'text') or not response.text:
                    raise ValueError("Gemini에서 유효한 응답을 받지 못했습니다.")
                
                # 응답 파싱
                trend_analysis = self._parse_trend_response(response.text)
                
            except Exception as api_error:
                # API 호출 관련 상세 에러 정보 제공
                error_msg = str(api_error)
                if "404" in error_msg and "models" in error_msg:
                    error_msg = "사용 중인 Gemini 모델이 더 이상 지원되지 않습니다. 모델 업데이트가 필요합니다."
                elif "quota" in error_msg.lower():
                    error_msg = "Gemini API 할당량이 초과되었습니다. 잠시 후 다시 시도해주세요."
                elif "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
                    error_msg = "Gemini API 키가 유효하지 않습니다. API 키를 확인해주세요."
                
                raise Exception(f"Gemini API 호출 실패: {error_msg}")
            
            return {
                'success': True,
                'trend_analysis': trend_analysis,
                'company_name': company_name
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'추이 분석 중 오류 발생: {str(e)}'
            }
    
    def _prepare_analysis_data(self, company_name: str, summary: Dict) -> Dict:
        """분석용 데이터 준비"""
        basic_info = summary.get('basic_info', {})
        balance_sheet = summary.get('balance_sheet', {})
        income_statement = summary.get('income_statement', {})
        
        # 금액을 억원 단위로 변환
        def to_billion(amount):
            if amount == 0:
                return 0
            return round(amount / 100_000_000, 1)
        
        return {
            'company_name': company_name,
            'year': basic_info.get('bsns_year', ''),
            'currency': basic_info.get('currency', 'KRW'),
            'fs_type': basic_info.get('fs_nm', ''),
            'balance_sheet': {
                'total_assets': {
                    'current': to_billion(balance_sheet.get('total_assets', {}).get('current', 0)),
                    'previous': to_billion(balance_sheet.get('total_assets', {}).get('previous', 0))
                },
                'total_liabilities': {
                    'current': to_billion(balance_sheet.get('total_liabilities', {}).get('current', 0)),
                    'previous': to_billion(balance_sheet.get('total_liabilities', {}).get('previous', 0))
                },
                'total_equity': {
                    'current': to_billion(balance_sheet.get('total_equity', {}).get('current', 0)),
                    'previous': to_billion(balance_sheet.get('total_equity', {}).get('previous', 0))
                }
            },
            'income_statement': {
                'revenue': {
                    'current': to_billion(income_statement.get('revenue', {}).get('current', 0)),
                    'previous': to_billion(income_statement.get('revenue', {}).get('previous', 0))
                },
                'operating_profit': {
                    'current': to_billion(income_statement.get('operating_profit', {}).get('current', 0)),
                    'previous': to_billion(income_statement.get('operating_profit', {}).get('previous', 0))
                },
                'net_profit': {
                    'current': to_billion(income_statement.get('net_profit', {}).get('current', 0)),
                    'previous': to_billion(income_statement.get('net_profit', {}).get('previous', 0))
                }
            }
        }
    
    def _create_analysis_prompt(self, data: Dict) -> str:
        """재무분석용 프롬프트 생성"""
        return f"""
다음은 {data['company_name']}의 {data['year']}년 재무제표 데이터입니다. 
일반인도 쉽게 이해할 수 있도록 친근하고 명확한 언어로 분석해주세요.

## 재무상태표 (단위: 억원)
- 자산총계: 당기 {data['balance_sheet']['total_assets']['current']}억, 전기 {data['balance_sheet']['total_assets']['previous']}억
- 부채총계: 당기 {data['balance_sheet']['total_liabilities']['current']}억, 전기 {data['balance_sheet']['total_liabilities']['previous']}억  
- 자본총계: 당기 {data['balance_sheet']['total_equity']['current']}억, 전기 {data['balance_sheet']['total_equity']['previous']}억

## 손익계산서 (단위: 억원)
- 매출액: 당기 {data['income_statement']['revenue']['current']}억, 전기 {data['income_statement']['revenue']['previous']}억
- 영업이익: 당기 {data['income_statement']['operating_profit']['current']}억, 전기 {data['income_statement']['operating_profit']['previous']}억
- 당기순이익: 당기 {data['income_statement']['net_profit']['current']}억, 전기 {data['income_statement']['net_profit']['previous']}억

다음 형식으로 분석해주세요:

**📊 재무 건전성**
[자산, 부채, 자본의 구조를 보고 회사의 재무 안정성을 평가해주세요]

**💰 수익성 분석**  
[매출액, 영업이익, 순이익을 통해 회사의 수익창출 능력을 분석해주세요]

**📈 성장성 분석**
[전년 대비 변화율을 계산하고 성장 여부를 평가해주세요]

**⚠️ 주의사항**
[투자자가 주목해야 할 리스크나 특이사항이 있다면 알려주세요]

**🎯 한줄 요약**
[이 회사의 재무상태를 한 문장으로 요약해주세요]

분석할 때 다음사항을 고려해주세요:
- 백분율 변화율도 함께 계산해서 알려주세요
- 업계 일반적인 수준과 비교해서 설명해주세요  
- 투자 관점에서 긍정적/부정적 요소를 균형있게 제시해주세요
- 전문용어는 쉬운 말로 풀어서 설명해주세요
"""
    
    def _prepare_trend_data(self, company_name: str, data: Dict) -> Dict:
        """추이 분석용 데이터 준비"""
        def to_billion_list(amounts):
            return [round(amount / 100_000_000, 1) if amount > 0 else 0 for amount in amounts]
        
        return {
            'company_name': company_name,
            'years': data['years'],
            'revenue': to_billion_list(data['revenue']),
            'operating_profit': to_billion_list(data['operating_profit']),
            'net_profit': to_billion_list(data['net_profit']),
            'total_assets': to_billion_list(data['total_assets']),
            'total_equity': to_billion_list(data['total_equity'])
        }
    
    def _create_trend_analysis_prompt(self, data: Dict) -> str:
        """추이 분석용 프롬프트 생성"""
        years_str = ', '.join(map(str, data['years']))
        revenue_str = ', '.join(map(str, data['revenue']))
        op_profit_str = ', '.join(map(str, data['operating_profit']))
        net_profit_str = ', '.join(map(str, data['net_profit']))
        assets_str = ', '.join(map(str, data['total_assets']))
        equity_str = ', '.join(map(str, data['total_equity']))
        
        return f"""
다음은 {data['company_name']}의 {len(data['years'])}년간 재무 추이 데이터입니다.
일반인도 쉽게 이해할 수 있도록 분석해주세요.

## 다년도 재무 추이 (단위: 억원)
연도: {years_str}
매출액: {revenue_str}
영업이익: {op_profit_str}  
당기순이익: {net_profit_str}
자산총계: {assets_str}
자본총계: {equity_str}

다음 형식으로 분석해주세요:

**📈 매출 성장 추이**
[매출액의 연도별 변화를 분석하고 성장 패턴을 설명해주세요]

**💡 수익성 변화**
[영업이익과 순이익의 추이를 통해 수익성 변화를 분석해주세요]

**🏗️ 자산 규모 변화**  
[자산과 자본의 성장을 통해 회사 규모 확장을 평가해주세요]

**🎯 성장률 분석**
[연평균 성장률(CAGR)을 계산해서 알려주세요]

**🔮 미래 전망**
[지금까지의 추이를 바탕으로 향후 전망을 제시해주세요]

**📋 종합 평가**  
[이 회사의 {len(data['years'])}년간 성과를 종합적으로 평가해주세요]

분석 시 고려사항:
- 구체적인 증감률과 절대 금액을 함께 제시해주세요
- 일시적 변동과 지속적 트렌드를 구분해주세요
- 업계 상황이나 경제 환경 변화도 고려해주세요
- 투자자 관점에서 의미있는 인사이트를 제공해주세요
"""
    
    def _parse_response(self, response_text: str) -> Dict:
        """Gemini 응답을 파싱하여 구조화"""
        sections = {
            'financial_health': '',
            'profitability': '',
            'growth': '',
            'warnings': '',
            'summary': ''
        }
        
        try:
            # 섹션별로 내용 추출
            lines = response_text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if '재무 건전성' in line:
                    current_section = 'financial_health'
                elif '수익성 분석' in line:
                    current_section = 'profitability'
                elif '성장성 분석' in line:
                    current_section = 'growth'
                elif '주의사항' in line:
                    current_section = 'warnings'
                elif '한줄 요약' in line:
                    current_section = 'summary'
                elif current_section and line:
                    sections[current_section] += line + '\n'
            
            # 전체 텍스트도 저장
            sections['full_text'] = response_text
            
        except Exception as e:
            # 파싱 실패 시 전체 텍스트만 반환
            sections = {
                'full_text': response_text,
                'parsing_error': str(e)
            }
        
        return sections
    
    def _parse_trend_response(self, response_text: str) -> Dict:
        """추이 분석 응답 파싱"""
        sections = {
            'revenue_trend': '',
            'profitability_change': '',
            'asset_growth': '',
            'growth_rate': '',
            'future_outlook': '',
            'overall_evaluation': ''
        }
        
        try:
            lines = response_text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if '매출 성장 추이' in line:
                    current_section = 'revenue_trend'
                elif '수익성 변화' in line:
                    current_section = 'profitability_change'
                elif '자산 규모 변화' in line:
                    current_section = 'asset_growth'
                elif '성장률 분석' in line:
                    current_section = 'growth_rate'
                elif '미래 전망' in line:
                    current_section = 'future_outlook'
                elif '종합 평가' in line:
                    current_section = 'overall_evaluation'
                elif current_section and line:
                    sections[current_section] += line + '\n'
            
            sections['full_text'] = response_text
            
        except Exception as e:
            sections = {
                'full_text': response_text,
                'parsing_error': str(e)
            }
        
        return sections


# 사용 가능한 모델 확인 함수
def list_available_models():
    """사용 가능한 Gemini 모델 목록 출력"""
    try:
        # 환경변수 로드
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key or api_key == 'your_gemini_api_key_here':
            print("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
            return
        
        if genai is None:
            print("❌ google-generativeai 패키지가 설치되지 않았습니다.")
            return
        
        genai.configure(api_key=api_key)
        
        print("🔍 사용 가능한 Gemini 모델 조회 중...")
        models = genai.list_models()
        
        print("\n📋 사용 가능한 모델 목록:")
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                print(f"  ✅ {model.name}")
                print(f"     설명: {getattr(model, 'description', 'N/A')}")
        
    except Exception as e:
        print(f"❌ 모델 목록 조회 실패: {str(e)}")

# 테스트 함수
def test_analyzer():
    """분석기 테스트"""
    try:
        print("🔍 사용 가능한 모델 확인 중...")
        list_available_models()
        
        print("\n🔧 분석기 초기화 중...")
        analyzer = FinancialAnalyzer()
        print("✅ Gemini API 연결 성공!")
        
        # 테스트용 더미 데이터
        test_data = {
            'basic_info': {'bsns_year': '2023', 'currency': 'KRW'},
            'balance_sheet': {
                'total_assets': {'current': 50000000000000, 'previous': 48000000000000},
                'total_liabilities': {'current': 30000000000000, 'previous': 29000000000000},
                'total_equity': {'current': 20000000000000, 'previous': 19000000000000}
            },
            'income_statement': {
                'revenue': {'current': 20000000000000, 'previous': 18000000000000},
                'operating_profit': {'current': 3000000000000, 'previous': 2800000000000},
                'net_profit': {'current': 2500000000000, 'previous': 2300000000000}
            }
        }
        
        print("🔍 테스트 분석 시작...")
        result = analyzer.analyze_financial_data("테스트회사", test_data)
        
        if result['success']:
            print("✅ 분석 완료!")
            print("📋 분석 결과:")
            summary = result['analysis'].get('summary', result['analysis'].get('full_text', '요약 없음'))
            print(summary[:200] + "..." if len(summary) > 200 else summary)
        else:
            print(f"❌ 분석 실패: {result['error']}")
            
    except Exception as e:
        print(f"❌ 테스트 오류: {str(e)}")


if __name__ == "__main__":
    test_analyzer()
