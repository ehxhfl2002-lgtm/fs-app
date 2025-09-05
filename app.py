#!/usr/bin/env python3
"""
재무제표 시각화 웹 애플리케이션
"""

from flask import Flask, render_template, request, jsonify
import json
from db_setup import CorpCodeDBManager
from dart_financial_api import DartFinancialAPI
from financial_analyzer import FinancialAnalyzer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# 전역 객체 초기화
db_manager = CorpCodeDBManager()

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/api/search-companies', methods=['GET'])
def search_companies():
    """회사명 검색 API"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'success': False, 'error': '검색어를 입력해주세요.'})
        
        # 회사 검색
        companies = db_manager.search_companies(query, limit=20)
        
        return jsonify({
            'success': True,
            'companies': companies,
            'total': len(companies)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/company/<corp_code>')
def get_company_info(corp_code):
    """회사 정보 조회 API"""
    try:
        company = db_manager.get_company_by_code(corp_code)
        if not company:
            return jsonify({'success': False, 'error': '회사를 찾을 수 없습니다.'})
        
        return jsonify({
            'success': True,
            'company': company
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/financial-data/<corp_code>')
def get_financial_data(corp_code):
    """재무데이터 조회 API"""
    try:
        year = request.args.get('year', '2023')
        report_type = request.args.get('report_type', '11011')
        
        # API 키 확인
        try:
            api = DartFinancialAPI()
        except ValueError as e:
            return jsonify({
                'success': False, 
                'error': 'API 키가 설정되지 않았습니다. .env 파일에 DART_API_KEY를 설정해주세요.'
            })
        
        # 재무데이터 조회 (실패 시 자동으로 다른 연도/보고서 시도)
        result = api.get_financial_summary_with_fallback(corp_code, year, report_type)
        
        if result['success']:
            summary = result['summary']
            
            # 차트용 데이터 변환
            chart_data = prepare_chart_data(summary)
            
            return jsonify({
                'success': True,
                'summary': summary,
                'chart_data': chart_data
            })
        else:
            return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/multi-year-data/<corp_code>')
def get_multi_year_data(corp_code):
    """다년도 재무데이터 조회 API"""
    try:
        start_year = int(request.args.get('start_year', '2020'))
        end_year = int(request.args.get('end_year', '2023'))
        report_type = request.args.get('report_type', '11011')
        
        # API 키 확인
        try:
            api = DartFinancialAPI()
        except ValueError as e:
            return jsonify({
                'success': False, 
                'error': 'API 키가 설정되지 않았습니다. .env 파일에 DART_API_KEY를 설정해주세요.'
            })
        
        # 다년도 데이터 조회
        result = api.get_multi_year_data(corp_code, start_year, end_year, report_type)
        
        if result['success']:
            # 차트용 데이터 변환
            chart_data = prepare_multi_year_chart_data(result['data'])
            
            return jsonify({
                'success': True,
                'data': result['data'],
                'chart_data': chart_data,
                'errors': result.get('errors', [])
            })
        else:
            return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/analyze-financial/<corp_code>')
def analyze_financial(corp_code):
    """AI 재무분석 API"""
    try:
        year = request.args.get('year', '2023')
        report_type = request.args.get('report_type', '11011')
        
        # 회사 정보 조회
        company = db_manager.get_company_by_code(corp_code)
        if not company:
            return jsonify({'success': False, 'error': '회사를 찾을 수 없습니다.'})
        
        # DART API로 재무데이터 조회
        try:
            dart_api = DartFinancialAPI()
        except ValueError as e:
            return jsonify({
                'success': False, 
                'error': 'DART API 키가 설정되지 않았습니다.'
            })
        
        financial_result = dart_api.get_financial_summary_with_fallback(corp_code, year, report_type)
        
        if not financial_result['success']:
            return jsonify({
                'success': False, 
                'error': f'재무데이터 조회 실패: {financial_result["error"]}'
            })
        
        # Gemini AI로 분석
        try:
            analyzer = FinancialAnalyzer()
        except ValueError as e:
            return jsonify({
                'success': False, 
                'error': 'Gemini API 키가 설정되지 않았습니다. .env 파일에 GEMINI_API_KEY를 설정해주세요.'
            })
        except ImportError as e:
            return jsonify({
                'success': False, 
                'error': 'google-generativeai 패키지가 필요합니다. pip install google-generativeai로 설치해주세요.'
            })
        
        analysis_result = analyzer.analyze_financial_data(
            company['corp_name'], 
            financial_result['summary']
        )
        
        if analysis_result['success']:
            return jsonify({
                'success': True,
                'analysis': analysis_result['analysis'],
                'company_name': company['corp_name'],
                'year': year,
                'report_type': report_type
            })
        else:
            return jsonify(analysis_result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/analyze-trends/<corp_code>')
def analyze_trends(corp_code):
    """AI 다년도 추이 분석 API"""
    try:
        start_year = int(request.args.get('start_year', '2020'))
        end_year = int(request.args.get('end_year', '2023'))
        report_type = request.args.get('report_type', '11011')
        
        # 회사 정보 조회
        company = db_manager.get_company_by_code(corp_code)
        if not company:
            return jsonify({'success': False, 'error': '회사를 찾을 수 없습니다.'})
        
        # DART API로 다년도 데이터 조회
        try:
            dart_api = DartFinancialAPI()
        except ValueError as e:
            return jsonify({
                'success': False, 
                'error': 'DART API 키가 설정되지 않았습니다.'
            })
        
        multi_year_result = dart_api.get_multi_year_data(corp_code, start_year, end_year, report_type)
        
        if not multi_year_result['success']:
            return jsonify({
                'success': False, 
                'error': f'다년도 데이터 조회 실패: {multi_year_result.get("error", "알 수 없는 오류")}'
            })
        
        # Gemini AI로 추이 분석
        try:
            analyzer = FinancialAnalyzer()
        except ValueError as e:
            return jsonify({
                'success': False, 
                'error': 'Gemini API 키가 설정되지 않았습니다.'
            })
        except ImportError as e:
            return jsonify({
                'success': False, 
                'error': 'google-generativeai 패키지가 필요합니다.'
            })
        
        trend_analysis_result = analyzer.analyze_financial_trends(
            company['corp_name'], 
            multi_year_result['data']
        )
        
        if trend_analysis_result['success']:
            return jsonify({
                'success': True,
                'trend_analysis': trend_analysis_result['trend_analysis'],
                'company_name': company['corp_name'],
                'years': f"{start_year}-{end_year}",
                'report_type': report_type
            })
        else:
            return jsonify(trend_analysis_result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def prepare_chart_data(summary):
    """단일 연도 차트 데이터 준비"""
    chart_data = {
        'balance_sheet': {
            'labels': [],
            'current_data': [],
            'previous_data': []
        },
        'income_statement': {
            'labels': [],
            'current_data': [],
            'previous_data': []
        }
    }
    
    # 재무상태표 데이터
    bs = summary.get('balance_sheet', {})
    for key, value in bs.items():
        if isinstance(value, dict) and 'account' in value:
            chart_data['balance_sheet']['labels'].append(value['account'])
            chart_data['balance_sheet']['current_data'].append(value.get('current', 0))
            chart_data['balance_sheet']['previous_data'].append(value.get('previous', 0))
    
    # 손익계산서 데이터
    is_data = summary.get('income_statement', {})
    for key, value in is_data.items():
        if isinstance(value, dict) and 'account' in value:
            chart_data['income_statement']['labels'].append(value['account'])
            chart_data['income_statement']['current_data'].append(value.get('current', 0))
            chart_data['income_statement']['previous_data'].append(value.get('previous', 0))
    
    return chart_data

def prepare_multi_year_chart_data(data):
    """다년도 차트 데이터 준비"""
    return {
        'years': data['years'],
        'revenue_trend': {
            'labels': [str(year) for year in data['years']],
            'data': data['revenue']
        },
        'profit_trend': {
            'labels': [str(year) for year in data['years']],
            'operating_profit': data['operating_profit'],
            'net_profit': data['net_profit']
        },
        'balance_trend': {
            'labels': [str(year) for year in data['years']],
            'assets': data['total_assets'],
            'liabilities': data['total_liabilities'],
            'equity': data['total_equity']
        }
    }

@app.route('/dashboard/<corp_code>')
def dashboard(corp_code):
    """재무제표 대시보드 페이지"""
    # 회사 정보 조회
    company = db_manager.get_company_by_code(corp_code)
    if not company:
        return "회사를 찾을 수 없습니다.", 404
    
    return render_template('dashboard.html', company=company)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    import os
    
    # 데이터베이스 초기화 확인
    try:
        stats = db_manager.get_stats()
        if stats['total_companies'] == 0:
            print("⚠️  회사코드 데이터베이스가 비어있습니다.")
            print("   db_setup.py를 먼저 실행하여 데이터베이스를 초기화하세요.")
        else:
            print(f"✅ 데이터베이스 준비 완료: {stats['total_companies']:,}개 회사")
    except Exception as e:
        print(f"⚠️  데이터베이스 확인 오류: {e}")
    
    # 배포 환경 설정
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    app.run(debug=debug, host='0.0.0.0', port=port)
