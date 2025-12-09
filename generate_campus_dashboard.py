import pandas as pd
import json
import os

def process_excel_file(file_path, period_name):
    """엑셀 파일을 읽어서 캠퍼스별 데이터를 추출"""
    df = pd.read_excel(file_path)
    
    campus_data = {}
    current_campus = None
    
    for idx, row in df.iterrows():
        campus_name = row.iloc[0]
        category = row.iloc[1]
        
        # 캠퍼스명 처리: 새로운 캠퍼스인 경우에만 초기화
        if pd.notna(campus_name):
            # 캠퍼스명이 변경된 경우에만 새로운 캠퍼스로 간주
            if campus_name != current_campus:
                current_campus = campus_name
                # 해당 캠퍼스가 아직 없는 경우에만 초기화
                if current_campus not in campus_data:
                    campus_data[current_campus] = {
                        '응시인원': [],
                        '정답인원': [],
                        '정답률': []
                    }
        
        # 현재 캠퍼스가 있고 카테고리가 있으면 데이터 추가
        if current_campus and pd.notna(category):
            # 1번~20번 문항 데이터 추출
            question_data = []
            for i in range(2, 22):  # 컬럼 2~21 (1번~20번 문항)
                value = row.iloc[i]
                question_data.append(float(value) if pd.notna(value) else 0)
            
            # 카테고리에 따라 데이터 저장
            if '응시' in str(category):
                campus_data[current_campus]['응시인원'] = question_data
            elif '정답인원' in str(category):
                campus_data[current_campus]['정답인원'] = question_data
            elif '정답률' in str(category) or '%' in str(category):
                campus_data[current_campus]['정답률'] = question_data
    
    return campus_data

def generate_dashboard_html():
    """대시보드 HTML 생성"""
    
    # 파일 정보
    files = [
        ('output/GT1_2024년5월_캠퍼스별_문항분석.xlsx', '2024년 5월'),
        ('output/GT1_2024년8월_캠퍼스별_문항분석.xlsx', '2024년 8월'),
        ('output/GT1_2024년11월_캠퍼스별_문항분석.xlsx', '2024년 11월'),
        ('output/GT1_2025년2월_캠퍼스별_문항분석.xlsx', '2025년 2월')
    ]
    
    all_data = {}
    
    for file_path, period_name in files:
        if os.path.exists(file_path):
            print(f"Processing {period_name}...")
            campus_data = process_excel_file(file_path, period_name)
            all_data[period_name] = campus_data
            print(f"  - Found {len(campus_data)} campuses")
        else:
            print(f"Warning: {file_path} not found")
    
    # JSON 데이터를 문자열로 변환
    data_json = json.dumps(all_data, ensure_ascii=False, indent=2)
    
    # HTML 템플릿 읽기
    html_template = '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GT1 캠퍼스별 문항분석 대시보드</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 40px;
            color: white;
        }

        h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }

        .subtitle {
            font-size: 1.1rem;
            opacity: 0.95;
            font-weight: 300;
        }

        .dashboard-card {
            background: rgba(255, 255, 255, 0.98);
            border-radius: 24px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
        }

        /* 탭 스타일 */
        .tabs {
            display: flex;
            gap: 12px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }

        .tab {
            flex: 1;
            min-width: 150px;
            padding: 16px 24px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            color: #4a5568;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .tab:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }

        .tab.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
        }

        /* 캠퍼스 선택 */
        .campus-selector {
            margin-bottom: 30px;
        }

        .campus-selector label {
            display: block;
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 12px;
            color: #2d3748;
        }

        .campus-selector select {
            width: 100%;
            padding: 14px 20px;
            font-size: 1rem;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            background: white;
            cursor: pointer;
            transition: all 0.3s ease;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            color: #2d3748;
        }

        .campus-selector select:hover {
            border-color: #667eea;
        }

        .campus-selector select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        /* 데이터 테이블 */
        .data-section {
            margin-top: 30px;
        }

        .section-title {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 20px;
            color: #2d3748;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .section-title::before {
            content: '';
            width: 4px;
            height: 28px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 2px;
        }

        table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin-top: 20px;
            overflow: hidden;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }

        thead {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        th {
            padding: 16px;
            text-align: center;
            font-weight: 600;
            font-size: 0.95rem;
            letter-spacing: 0.5px;
        }

        tbody tr {
            background: white;
            transition: all 0.2s ease;
        }

        tbody tr:nth-child(even) {
            background: #f7fafc;
        }

        tbody tr:hover {
            background: #edf2f7;
            transform: scale(1.01);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        td {
            padding: 14px;
            text-align: center;
            border-bottom: 1px solid #e2e8f0;
            font-size: 0.95rem;
        }

        .question-num {
            font-weight: 600;
            color: #667eea;
        }

        .accuracy {
            font-weight: 600;
        }

        .accuracy.high {
            color: #48bb78;
        }

        .accuracy.medium {
            color: #ed8936;
        }

        .accuracy.low {
            color: #f56565;
        }

        /* 차트 컨테이너 */
        .chart-container {
            margin-top: 40px;
            background: #f7fafc;
            padding: 30px;
            border-radius: 16px;
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.06);
            height: 500px;
        }

        .chart-title {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 20px;
            color: #2d3748;
            text-align: center;
        }

        .chart-wrapper {
            position: relative;
            height: 400px;
            width: 100%;
        }

        #accuracyChart {
            max-width: 100%;
            max-height: 100%;
        }

        /* 통계 카드 */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 24px;
            border-radius: 16px;
            color: white;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
            transition: transform 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-4px);
        }

        .stat-label {
            font-size: 0.9rem;
            opacity: 0.9;
            margin-bottom: 8px;
            font-weight: 500;
        }

        .stat-value {
            font-size: 2rem;
            font-weight: 700;
        }

        .stat-unit {
            font-size: 1rem;
            opacity: 0.9;
            margin-left: 4px;
        }

        .hidden {
            display: none;
        }

        /* 반응형 */
        @media (max-width: 768px) {
            h1 {
                font-size: 1.8rem;
            }

            .dashboard-card {
                padding: 24px;
            }

            .tabs {
                flex-direction: column;
            }

            .tab {
                min-width: 100%;
            }

            table {
                font-size: 0.85rem;
            }

            th, td {
                padding: 10px 8px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 GT1 캠퍼스별 문항분석 대시보드</h1>
            <p class="subtitle">시기별 · 캠퍼스별 문항 정답률 분석</p>
        </header>

        <div class="dashboard-card">
            <!-- 시기 선택 탭 -->
            <div class="tabs" id="periodTabs">
                <button class="tab active" data-period="2024년 5월">2024년 5월</button>
                <button class="tab" data-period="2024년 8월">2024년 8월</button>
                <button class="tab" data-period="2024년 11월">2024년 11월</button>
                <button class="tab" data-period="2025년 2월">2025년 2월</button>
            </div>

            <!-- 캠퍼스 선택 -->
            <div class="campus-selector">
                <label for="campusSelect">🏫 캠퍼스 선택</label>
                <select id="campusSelect">
                    <option value="">캠퍼스를 선택하세요</option>
                </select>
            </div>

            <!-- 통계 카드 -->
            <div class="stats-grid" id="statsGrid" style="display: none;">
                <div class="stat-card">
                    <div class="stat-label">총 응시인원</div>
                    <div class="stat-value" id="totalStudents">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">평균 정답률</div>
                    <div class="stat-value">
                        <span id="avgAccuracy">-</span>
                        <span class="stat-unit">%</span>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">최고 정답률</div>
                    <div class="stat-value">
                        <span id="maxAccuracy">-</span>
                        <span class="stat-unit">%</span>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">최저 정답률</div>
                    <div class="stat-value">
                        <span id="minAccuracy">-</span>
                        <span class="stat-unit">%</span>
                    </div>
                </div>
            </div>

            <!-- 데이터 테이블 -->
            <div class="data-section" id="dataSection" style="display: none;">
                <div class="section-title">문항별 상세 분석</div>
                <table>
                    <thead>
                        <tr>
                            <th>문항번호</th>
                            <th>응시인원</th>
                            <th>정답인원</th>
                            <th>정답률 (%)</th>
                        </tr>
                    </thead>
                    <tbody id="dataTableBody">
                    </tbody>
                </table>
            </div>

            <!-- 차트 -->
            <div class="chart-container" id="chartContainer" style="display: none;">
                <div class="chart-title">📈 문항별 정답률 추이</div>
                <div class="chart-wrapper">
                    <canvas id="accuracyChart"></canvas>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        // 데이터를 HTML에 직접 포함
        const dashboardData = DATA_PLACEHOLDER;
        
        let currentPeriod = '2024년 5월';
        let currentChart = null;

        // 초기화
        function init() {
            console.log('Dashboard initialized with data:', dashboardData);
            updateCampusSelector();
        }

        // 캠퍼스 선택 업데이트
        function updateCampusSelector() {
            const select = document.getElementById('campusSelect');
            select.innerHTML = '<option value="">캠퍼스를 선택하세요</option>';

            if (dashboardData && dashboardData[currentPeriod]) {
                // 전체 캠퍼스 옵션 추가
                const allOption = document.createElement('option');
                allOption.value = '__ALL__';
                allOption.textContent = '📊 전체 캠퍼스';
                select.appendChild(allOption);
                
                // 구분선
                const separator = document.createElement('option');
                separator.disabled = true;
                separator.textContent = '──────────────';
                select.appendChild(separator);
                
                const campuses = Object.keys(dashboardData[currentPeriod]).sort();
                campuses.forEach(campus => {
                    const option = document.createElement('option');
                    option.value = campus;
                    option.textContent = campus;
                    select.appendChild(option);
                });
            }
        }

        // 정답률에 따른 클래스 반환
        function getAccuracyClass(accuracy) {
            if (accuracy >= 70) return 'high';
            if (accuracy >= 40) return 'medium';
            return 'low';
        }

        // 전체 캠퍼스 데이터 집계
        function aggregateAllCampuses() {
            if (!dashboardData || !dashboardData[currentPeriod]) {
                return null;
            }
            
            const campuses = Object.keys(dashboardData[currentPeriod]);
            const aggregated = {
                '응시인원': new Array(20).fill(0),
                '정답인원': new Array(20).fill(0),
                '정답률': new Array(20).fill(0)
            };
            
            // 모든 캠퍼스의 데이터를 합산
            campuses.forEach(campus => {
                const campusData = dashboardData[currentPeriod][campus];
                for (let i = 0; i < 20; i++) {
                    aggregated['응시인원'][i] += campusData['응시인원'][i] || 0;
                    aggregated['정답인원'][i] += campusData['정답인원'][i] || 0;
                }
            });
            
            // 정답률 재계산
            for (let i = 0; i < 20; i++) {
                if (aggregated['응시인원'][i] > 0) {
                    aggregated['정답률'][i] = (aggregated['정답인원'][i] / aggregated['응시인원'][i]) * 100;
                } else {
                    aggregated['정답률'][i] = 0;
                }
            }
            
            return aggregated;
        }

        // 데이터 표시
        function displayData(campus) {
            let data;
            
            // 전체 캠퍼스 선택 시
            if (campus === '__ALL__') {
                data = aggregateAllCampuses();
                if (!data) return;
            } else {
                // 개별 캠퍼스 선택 시
                if (!dashboardData || !dashboardData[currentPeriod] || !dashboardData[currentPeriod][campus]) {
                    return;
                }
                data = dashboardData[currentPeriod][campus];
            }
            const tbody = document.getElementById('dataTableBody');
            tbody.innerHTML = '';

            // 통계 계산
            let totalStudents = 0;
            let totalAccuracy = 0;
            let maxAccuracy = 0;
            let minAccuracy = 100;
            let validQuestions = 0;

            // 테이블 생성
            for (let i = 0; i < 20; i++) {
                const 응시인원 = data['응시인원'][i] || 0;
                const 정답인원 = data['정답인원'][i] || 0;
                const 정답률 = data['정답률'][i] || 0;

                if (응시인원 > 0) {
                    totalStudents = Math.max(totalStudents, 응시인원);
                    totalAccuracy += 정답률;
                    maxAccuracy = Math.max(maxAccuracy, 정답률);
                    minAccuracy = Math.min(minAccuracy, 정답률);
                    validQuestions++;
                }

                const row = document.createElement('tr');
                row.innerHTML = `
                    <td class="question-num">${i + 1}번</td>
                    <td>${Math.round(응시인원)}명</td>
                    <td>${Math.round(정답인원)}명</td>
                    <td class="accuracy ${getAccuracyClass(정답률)}">${정답률.toFixed(2)}%</td>
                `;
                tbody.appendChild(row);
            }

            // 통계 표시
            document.getElementById('totalStudents').textContent = Math.round(totalStudents) + '명';
            document.getElementById('avgAccuracy').textContent = (totalAccuracy / validQuestions).toFixed(2);
            document.getElementById('maxAccuracy').textContent = maxAccuracy.toFixed(2);
            document.getElementById('minAccuracy').textContent = minAccuracy.toFixed(2);

            // 섹션 표시
            document.getElementById('statsGrid').style.display = 'grid';
            document.getElementById('dataSection').style.display = 'block';
            document.getElementById('chartContainer').style.display = 'block';

            // 차트 업데이트
            updateChart(data);
        }

        // 차트 업데이트
        function updateChart(data) {
            const ctx = document.getElementById('accuracyChart').getContext('2d');
            
            const labels = Array.from({length: 20}, (_, i) => `${i + 1}번`);
            const accuracyData = data['정답률'] || [];

            if (currentChart) {
                currentChart.destroy();
            }

            currentChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: '정답률 (%)',
                        data: accuracyData,
                        borderColor: 'rgb(102, 126, 234)',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 5,
                        pointHoverRadius: 7,
                        pointBackgroundColor: 'rgb(102, 126, 234)',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top',
                            labels: {
                                font: {
                                    size: 14,
                                    family: 'Inter'
                                }
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            padding: 12,
                            titleFont: {
                                size: 14,
                                family: 'Inter'
                            },
                            bodyFont: {
                                size: 13,
                                family: 'Inter'
                            },
                            callbacks: {
                                label: function(context) {
                                    return '정답률: ' + context.parsed.y.toFixed(2) + '%';
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                callback: function(value) {
                                    return value + '%';
                                },
                                font: {
                                    size: 12,
                                    family: 'Inter'
                                }
                            },
                            grid: {
                                color: 'rgba(0, 0, 0, 0.05)'
                            }
                        },
                        x: {
                            ticks: {
                                font: {
                                    size: 11,
                                    family: 'Inter'
                                }
                            },
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            });
        }

        // 이벤트 리스너
        document.getElementById('periodTabs').addEventListener('click', (e) => {
            if (e.target.classList.contains('tab')) {
                // 탭 활성화
                document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
                e.target.classList.add('active');

                // 현재 시기 업데이트
                currentPeriod = e.target.dataset.period;
                
                // 캠퍼스 선택 초기화
                document.getElementById('campusSelect').value = '';
                document.getElementById('statsGrid').style.display = 'none';
                document.getElementById('dataSection').style.display = 'none';
                document.getElementById('chartContainer').style.display = 'none';
                
                // 캠퍼스 목록 업데이트
                updateCampusSelector();
            }
        });

        document.getElementById('campusSelect').addEventListener('change', (e) => {
            const campus = e.target.value;
            if (campus) {
                displayData(campus);
            } else {
                document.getElementById('statsGrid').style.display = 'none';
                document.getElementById('dataSection').style.display = 'none';
                document.getElementById('chartContainer').style.display = 'none';
            }
        });

        // 데이터 로드 후 즉시 초기화 (DOMContentLoaded 대신)
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
        } else {
            init();
        }
    </script>
</body>
</html>'''
    
    # DATA_PLACEHOLDER를 실제 데이터로 교체
    html_content = html_template.replace('DATA_PLACEHOLDER', data_json)
    
    # HTML 파일 저장
    output_file = 'output/GT1_캠퍼스별_문항분석_대시보드.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n[SUCCESS] Dashboard generated: {output_file}")
    print(f"Total periods: {len(all_data)}")
    
    # 통계 출력
    for period, campuses in all_data.items():
        print(f"\n{period}: {len(campuses)} campuses")

if __name__ == '__main__':
    generate_dashboard_html()
