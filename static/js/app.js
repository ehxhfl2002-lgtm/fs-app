// 재무제표 시각화 웹앱 공통 JavaScript

// 전역 변수
window.AppConfig = {
    charts: {},
    formatters: {}
};

// 숫자 포맷팅 함수
window.AppConfig.formatters.formatAmount = function(amount) {
    if (amount === 0 || amount === null || amount === undefined) return "0";
    
    const absAmount = Math.abs(amount);
    const sign = amount < 0 ? '-' : '';
    
    if (absAmount >= 1_000_000_000_000) {
        return sign + (absAmount / 1_000_000_000_000).toFixed(1) + "조";
    } else if (absAmount >= 100_000_000) {
        return sign + (absAmount / 100_000_000).toFixed(1) + "억";
    } else if (absAmount >= 10_000) {
        return sign + (absAmount / 10_000).toFixed(1) + "만";
    } else {
        return sign + absAmount.toLocaleString();
    }
};

// 퍼센트 포맷팅 함수
window.AppConfig.formatters.formatPercent = function(value, decimals = 1) {
    if (value === null || value === undefined) return "0%";
    return value.toFixed(decimals) + "%";
};

// 날짜 포맷팅 함수
window.AppConfig.formatters.formatDate = function(dateString) {
    if (!dateString) return "";
    
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('ko-KR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    } catch (error) {
        return dateString;
    }
};

// 차트 색상 팔레트
window.AppConfig.colors = {
    primary: '#007bff',
    success: '#28a745',
    info: '#17a2b8',
    warning: '#ffc107',
    danger: '#dc3545',
    secondary: '#6c757d',
    
    // 차트용 색상 배열
    chartColors: [
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 99, 132, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(255, 206, 86, 0.8)',
        'rgba(153, 102, 255, 0.8)',
        'rgba(255, 159, 64, 0.8)'
    ],
    
    // 테두리 색상 배열
    borderColors: [
        'rgba(54, 162, 235, 1)',
        'rgba(255, 99, 132, 1)',
        'rgba(75, 192, 192, 1)',
        'rgba(255, 206, 86, 1)',
        'rgba(153, 102, 255, 1)',
        'rgba(255, 159, 64, 1)'
    ]
};

// 공통 차트 옵션
window.AppConfig.chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'top',
            labels: {
                usePointStyle: true,
                padding: 20
            }
        }
    },
    scales: {
        y: {
            beginAtZero: true,
            grid: {
                color: 'rgba(0,0,0,0.1)'
            },
            ticks: {
                callback: function(value) {
                    return window.AppConfig.formatters.formatAmount(value);
                }
            }
        },
        x: {
            grid: {
                color: 'rgba(0,0,0,0.1)'
            }
        }
    }
};

// 차트 생성 헬퍼 함수
window.AppConfig.createChart = function(canvasId, type, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas element with id '${canvasId}' not found`);
        return null;
    }
    
    // 기존 차트가 있으면 제거
    if (window.AppConfig.charts[canvasId]) {
        window.AppConfig.charts[canvasId].destroy();
    }
    
    // 기본 옵션과 사용자 옵션 병합
    const mergedOptions = {
        ...window.AppConfig.chartOptions,
        ...options,
        plugins: {
            ...window.AppConfig.chartOptions.plugins,
            ...(options.plugins || {}),
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const label = context.dataset.label || '';
                        const value = window.AppConfig.formatters.formatAmount(context.parsed.y);
                        return label + ': ' + value;
                    }
                },
                ...(options.plugins?.tooltip || {})
            }
        }
    };
    
    // 차트 생성
    const chart = new Chart(ctx.getContext('2d'), {
        type: type,
        data: data,
        options: mergedOptions
    });
    
    // 차트 인스턴스 저장
    window.AppConfig.charts[canvasId] = chart;
    
    return chart;
};

// 모든 차트 제거 함수
window.AppConfig.destroyAllCharts = function() {
    Object.keys(window.AppConfig.charts).forEach(chartId => {
        if (window.AppConfig.charts[chartId]) {
            window.AppConfig.charts[chartId].destroy();
            delete window.AppConfig.charts[chartId];
        }
    });
};

// API 호출 헬퍼 함수
window.AppConfig.api = {
    // GET 요청
    get: async function(url) {
        try {
            const response = await fetch(url);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API GET 오류:', error);
            throw error;
        }
    },
    
    // POST 요청
    post: async function(url, body) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(body)
            });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API POST 오류:', error);
            throw error;
        }
    }
};

// 로딩 상태 관리
window.AppConfig.ui = {
    showLoading: function(elementId = 'loading') {
        const element = document.getElementById(elementId);
        if (element) {
            element.classList.remove('d-none');
        }
    },
    
    hideLoading: function(elementId = 'loading') {
        const element = document.getElementById(elementId);
        if (element) {
            element.classList.add('d-none');
        }
    },
    
    showError: function(message, elementId = 'error-message') {
        const errorDiv = document.getElementById(elementId);
        const errorText = errorDiv?.querySelector('#error-text');
        
        if (errorDiv && errorText) {
            errorText.textContent = message;
            errorDiv.classList.remove('d-none');
        } else {
            alert(message); // fallback
        }
    },
    
    hideError: function(elementId = 'error-message') {
        const element = document.getElementById(elementId);
        if (element) {
            element.classList.add('d-none');
        }
    },
    
    // 토스트 알림 (Bootstrap 토스트 사용)
    showToast: function(message, type = 'info') {
        // 간단한 알림을 위한 함수 (추후 확장 가능)
        console.log(`${type.toUpperCase()}: ${message}`);
    }
};

// 유틸리티 함수들
window.AppConfig.utils = {
    // 디바운스 함수
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // 배열에서 최대값 찾기
    getMaxValue: function(arrays) {
        const allValues = arrays.flat().filter(v => v !== null && v !== undefined);
        return Math.max(...allValues);
    },
    
    // 배열에서 최소값 찾기
    getMinValue: function(arrays) {
        const allValues = arrays.flat().filter(v => v !== null && v !== undefined);
        return Math.min(...allValues);
    },
    
    // 객체 깊은 복사
    deepClone: function(obj) {
        return JSON.parse(JSON.stringify(obj));
    },
    
    // URL 파라미터 파싱
    getUrlParams: function() {
        const params = new URLSearchParams(window.location.search);
        const result = {};
        for (const [key, value] of params) {
            result[key] = value;
        }
        return result;
    }
};

// 페이지 로드 완료 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    // 페이지 애니메이션 추가
    document.body.classList.add('fade-in');
    
    // 툴팁 초기화 (Bootstrap)
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // 전역 에러 핸들러
    window.addEventListener('error', function(e) {
        console.error('전역 오류:', e.error);
    });
    
    console.log('재무제표 시각화 앱이 초기화되었습니다.');
});

// 페이지 언로드 시 정리
window.addEventListener('beforeunload', function() {
    // 모든 차트 인스턴스 정리
    window.AppConfig.destroyAllCharts();
});
