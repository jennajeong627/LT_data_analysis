import pandas as pd
import json
import os

# 파일 경로 설정
csv_file_path = r'c:\Users\user\projects\LT_data_analysis\2025_10월_data\2025_10월_MT.csv'
group_file_path = r'c:\Users\user\projects\LT_data_analysis\캠퍼스별_그룹화.md'
output_json_path = r'c:\Users\user\projects\LT_data_analysis\2025_10월_data\dashboard_data.json'

# 1. 캠퍼스 그룹 정보 읽기
campus_groups = {"직영": [], "FC": []}
current_group = None

if os.path.exists(group_file_path):
    with open(group_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith("# 직영 캠퍼스"):
                current_group = "직영"
            elif line.startswith("# FC 캠퍼스"):
                current_group = "FC"
            elif line.startswith("- ") and current_group:
                campus_name = line.replace("- ", "").strip()
                campus_groups[current_group].append(campus_name)

# 2. CSV 파일 읽기
try:
    df = pd.read_csv(csv_file_path)
except Exception as e:
    print(f"Error reading CSV: {e}")
    exit(1)

# 컬럼명 확인 및 처리 (공백 제거 등)
df.columns = [c.strip() for c in df.columns]

# 필요한 컬럼 확인
required_columns = ['캠퍼스', '문항 순번', '정답여부']
for col in required_columns:
    if col not in df.columns:
        print(f"Missing column: {col}")
        # '문항순번'이나 '문항 순번' 등 유연하게 처리 시도 가능하지만 일단 에러 처리
        exit(1)

# 3. 데이터 집계
# 캠퍼스별, 문항별 집계
result_data = {}

# 전체 캠퍼스 목록 (CSV에 있는 모든 캠퍼스)
all_campuses = df['캠퍼스'].unique()

for campus in all_campuses:
    campus_df = df[df['캠퍼스'] == campus]
    campus_data = {}
    
    # 1번부터 15번 문항까지 (데이터에 있는 문항만)
    questions = sorted(campus_df['문항 순번'].unique())
    
    for q_num in questions:
        # 15번까지만 관심 있다고 가정 (사용자 요청: "문항은 15문항이야")
        if q_num > 15:
            continue
            
        q_df = campus_df[campus_df['문항 순번'] == q_num]
        
        total_students = len(q_df)
        correct_count = len(q_df[q_df['정답여부'] == 'Y'])
        accuracy = (correct_count / total_students * 100) if total_students > 0 else 0
        
        campus_data[int(q_num)] = {
            "total": total_students,
            "correct_count": correct_count,
            "accuracy": round(accuracy, 2)
        }
    
    result_data[campus] = campus_data

# 그룹별 데이터 집계 (직영, FC)
group_stats = {}
for group_name, campuses in campus_groups.items():
    # 해당 그룹에 속한 학생들 필터링
    # 캠퍼스 이름 매칭 시 주의: CSV에는 풀 네임으로 되어 있을 수 있음 (예: '대치폴리' vs '대치폴리매그넷')
    # 단순 포함 여부나 매핑 로직이 필요할 수 있으나, 현재는 CSV의 캠퍼스 컬럼 값이 그룹 파일의 이름 포함 여부로 체크하거나
    # 정확한 매핑이 없으면 일단 set(campuses)에 있는 이름 그대로 사용 시도.
    # 하지만 CSV 데이터(df['캠퍼스'])와 그룹 파일(.md)의 이름이 정확히 일치하지 않을 수 있음.
    # 예: md파일 '대치폴리' -> csv '대치폴리매그넷'
    # 따라서, df['캠퍼스'] 값이 groups 리스트의 어떤 항목을 *포함*하거나 *시작*하는지 확인해야 함.
    
    group_df_list = []
    
    # 1. 효율적인 매칭을 위해 CSV의 유니크 캠퍼스 목록을 순회하며 그룹에 속하는지 판별
    matched_campuses = []
    for csv_campus in all_campuses:
        is_in_group = False
        for group_campus in campuses:
            # 단순 포함 관계 확인 (예: '대치폴리' in '대치폴리매그넷')
            if group_campus in csv_campus: 
                is_in_group = True
                break
        if is_in_group:
            matched_campuses.append(csv_campus)
            
    if not matched_campuses:
        continue
        
    group_df = df[df['캠퍼스'].isin(matched_campuses)]
    
    if group_df.empty:
        continue

    group_data = {}
    questions = sorted(group_df['문항 순번'].unique())
    
    for q_num in questions:
        if q_num > 15: continue
        q_df = group_df[group_df['문항 순번'] == q_num]
        
        total_students = len(q_df)
        correct_count = len(q_df[q_df['정답여부'] == 'Y'])
        accuracy = (correct_count / total_students * 100) if total_students > 0 else 0
        
        group_data[int(q_num)] = {
            "total": total_students,
            "correct_count": correct_count,
            "accuracy": round(accuracy, 2)
        }
    group_stats[group_name] = group_data

# 전체(All) 데이터 집계 (선택 사항, 필요시 사용)
total_data = {}
all_questions = sorted(df['문항 순번'].unique())
for q_num in all_questions:
    if q_num > 15: continue
    q_df = df[df['문항 순번'] == q_num]
    total_students = len(q_df)
    correct_count = len(q_df[q_df['정답여부'] == 'Y'])
    accuracy = (correct_count / total_students * 100) if total_students > 0 else 0
    total_data[int(q_num)] = {
        "total": total_students,
        "correct_count": correct_count,
        "accuracy": round(accuracy, 2)
    }

# 4. JSON 구조 생성
final_output = {
    "metadata": {
        "campus_groups": campus_groups,
        "all_campuses_list": list(all_campuses)
    },
    "stats": result_data,
    "group_stats": group_stats,
    "total_stats": total_data
}

# 5. JSON 파일 저장
with open(output_json_path, 'w', encoding='utf-8') as f:
    json.dump(final_output, f, ensure_ascii=False, indent=4)

print(f"Dashboard data generated at: {output_json_path}")
