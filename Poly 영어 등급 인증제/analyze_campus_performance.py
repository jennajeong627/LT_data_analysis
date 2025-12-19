import pandas as pd
import glob
import os

def analyze_campuses():
    data_dir = r"c:\Users\user\projects\LT_data_analysis\2025_LT_11월_data"
    all_files = glob.glob(os.path.join(data_dir, "*.csv"))
    
    dfs = []
    for file in all_files:
        # We need to calculate scores per student first
        df = pd.read_csv(file)
        # Group by student to get their score and campus
        # Score is number of 'Y' in '정답여부'
        student_scores = df.groupby(['캠퍼스', '학번', '이름', '교육과정']).agg({
            '정답여부': lambda x: (x == 'Y').sum()
        }).reset_index()
        student_scores.rename(columns={'정답여부': 'Score', '교육과정': 'Level'}, inplace=True)
        dfs.append(student_scores)
    
    combined_students = pd.concat(dfs)
    
    # Campus Summary
    campus_stats = combined_students.groupby('캠퍼스').agg({
        'Score': 'mean',
        '학번': 'count'
    }).reset_index()
    campus_stats.rename(columns={'Score': 'Avg_Score', '학번': 'Student_Count'}, inplace=True)
    
    # MAG2 Ratio
    mag2_counts = combined_students[combined_students['Level'] == 'MAG2'].groupby('캠퍼스').size().reset_index(name='MAG2_Count')
    campus_stats = pd.merge(campus_stats, mag2_counts, on='캠퍼스', how='left').fillna(0)
    campus_stats['MAG2_Ratio'] = (campus_stats['MAG2_Count'] / campus_stats['Student_Count']) * 100
    
    # Sort by Avg Score for Ranking
    campus_stats = campus_stats.sort_values(by='Avg_Score', ascending=False)
    
    print("Top 10 Campuses by Average Score:")
    print(campus_stats.head(10))
    
    # Let's also look at Skill performance per campus for "Strengths/Weaknesses"
    # This requires looking at the original long-format data
    all_raw_data = pd.concat([pd.read_csv(f) for f in all_files])
    skill_stats = all_raw_data.groupby(['캠퍼스', '스킬']).agg({
        '정답여부': lambda x: (x == 'Y').mean() * 100
    }).reset_index()
    skill_stats.rename(columns={'정답여부': 'Accuracy'}, inplace=True)
    
    return campus_stats, skill_stats

if __name__ == "__main__":
    campus_stats, skill_stats = analyze_campuses()
    campus_stats.to_csv("campus_performance_summary.csv", index=False)
    # Get top 5 strengths/weaknesses for top campuses
    top_campuses = campus_stats.head(5)['캠퍼스'].tolist()
    for campus in top_campuses:
        print(f"\n--- {campus} Analysis ---")
        campus_skills = skill_stats[skill_stats['캠퍼스'] == campus].sort_values(by='Accuracy', ascending=False)
        print("Strengths (Top Skills):")
        print(campus_skills.head(3))
        print("Weaknesses (Bottom Skills):")
        print(campus_skills.tail(3))
