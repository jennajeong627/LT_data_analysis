import pandas as pd
import sys

# Set encoding for output
sys.stdout.reconfigure(encoding='utf-8')

file_path = r'c:\Users\user\projects\LT_data_analysis\2025_LT_11월_data\2025_11월_MAG2.csv'
df = pd.read_csv(file_path)
jiwoo = df[df['이름'] == '김지우']

subjects = ['English', 'Speech Building', 'Eng. Foundations', 'Listening']
results = {}

for sub in subjects:
    sub_df = jiwoo[jiwoo['시험과목'] == sub]
    if sub_df.empty:
        results[sub] = {'best': 'N/A', 'worst': 'N/A'}
        continue
    
    # Calculate accuracy per skill
    skill_stats = sub_df.groupby('스킬')['정답여부'].apply(lambda x: (x == 'Y').sum() / len(x)).reset_index()
    skill_stats.columns = ['스킬', '정답률']
    
    # Sort: highest accuracy first, then name
    skill_stats_best = skill_stats.sort_values(by=['정답률', '스킬'], ascending=[False, True])
    best_skill = skill_stats_best.iloc[0]['스킬']
    
    # Sort: lowest accuracy first, then name
    skill_stats_worst = skill_stats.sort_values(by=['정답률', '스킬'], ascending=[True, True])
    worst_skill = skill_stats_worst.iloc[0]['스킬']
    
    results[sub] = {'best': best_skill, 'worst': worst_skill}

for sub in subjects:
    print(f"{sub} | Best: {results[sub]['best']} | Worst: {results[sub]['worst']}")
