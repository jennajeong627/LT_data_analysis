import pandas as pd
import json
import os

# Define file paths
base_dir = r"c:\Users\user\projects\LT_data_analysis"
data_file = os.path.join(base_dir, "2024_5월_data", "2024_5월_정오답 샘플.csv")
output_file = os.path.join(base_dir, "may_campus_choice_data.json")

# Define correct answers for May
correct_answers = {
    1: 1, 2: 3, 3: 2, 4: 3, 5: 1, 
    6: 4, 7: 4, 8: 2, 9: 1, 10: 3, 
    11: 2, 12: 2, 13: 2, 14: 3, 15: 1, 
    16: 2, 17: 3, 18: 4, 19: 3, 20: 1
}

def generate_data():
    print("Loading data...")
    # Load data
    df = pd.read_csv(data_file)
    
    # Ensure columns are stripped of whitespace
    df.columns = [col.strip() for col in df.columns]
    
    # Filter for GT1 just in case
    if '레벨' in df.columns:
        df = df[df['레벨'] == 'GT1']
    
    # The last column seems to be the student answer, labeled "정답 여부" or similar
    # Based on inspection, it's the last column. Let's use negative indexing or name if consistent.
    # Header: 레벨,캠퍼스,학급,학번,학생명,퀴즈 수,정답 수,문항 순번,정답 여부
    # The inspection showed "정답 여부" has values 1,2,3,4.
    answer_col = '정답 여부'
    campus_col = '캠퍼스'
    q_col = '문항 순번'

    # Get unique campuses
    campuses = df[campus_col].unique()
    
    result_data = {}
    
    # Initialize __ALL__ aggregate
    all_campus_stats = {}
    for q_num in range(1, 21):
        all_campus_stats[q_num] = {1: 0, 2: 0, 3: 0, 4: 0, 'total': 0}

    print(f"Processing {len(campuses)} campuses...")
    
    for campus in campuses:
        campus_df = df[df[campus_col] == campus]
        campus_stats = []
        
        for q_num in range(1, 21):
            q_df = campus_df[campus_df[q_col] == q_num]
            
            # Count choices
            counts = {1: 0, 2: 0, 3: 0, 4: 0}
            total = 0
            
            for _, row in q_df.iterrows():
                try:
                    ans = int(row[answer_col])
                    if ans in counts:
                        counts[ans] += 1
                        total += 1
                        
                        # Add to aggregate
                        all_campus_stats[q_num][ans] += 1
                        all_campus_stats[q_num]['total'] += 1
                except ValueError:
                    continue
            
            # Calculate ratios
            ratios = []
            count_list = []
            for i in range(1, 5):
                count_list.append(counts[i])
                ratio = (counts[i] / total * 100) if total > 0 else 0
                ratios.append(round(ratio, 2))
                
            campus_stats.append({
                "q": q_num,
                "ans": correct_answers[q_num],
                "counts": count_list,
                "ratios": ratios
            })
            
        result_data[campus] = campus_stats

    # Process __ALL__
    all_stats_list = []
    for q_num in range(1, 21):
        stats = all_campus_stats[q_num]
        total = stats['total']
        count_list = [stats[1], stats[2], stats[3], stats[4]]
        ratios = []
        for c in count_list:
            ratios.append(round((c / total * 100), 2) if total > 0 else 0)
            
        all_stats_list.append({
            "q": q_num,
            "ans": correct_answers[q_num],
            "counts": count_list,
            "ratios": ratios
        })
    
    result_data['__ALL__'] = all_stats_list

    # Save to JSON
    print("Saving to JSON...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    print(f"Done. Data saved to {output_file}")

if __name__ == "__main__":
    generate_data()
