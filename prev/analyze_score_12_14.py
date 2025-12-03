import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the data
df = pd.read_csv('2024_5월_학생문항별결과.csv')

# Filter students with score 12-14
students_12_14 = df[df['정답 수'].between(12, 14)]

# Get unique students
unique_students = students_12_14[['결과코드', '정답 수']].drop_duplicates()
print(f"정답 수 12~14점인 학생 수: {len(unique_students)}")
print(f"  - 12점: {len(unique_students[unique_students['정답 수'] == 12])}")
print(f"  - 13점: {len(unique_students[unique_students['정답 수'] == 13])}")
print(f"  - 14점: {len(unique_students[unique_students['정답 수'] == 14])}")

# Calculate accuracy rate by difficulty level
difficulty_stats = students_12_14.groupby('난이도').agg({
    '정답 여부': lambda x: (x == 'Y').sum(),  # Correct answers
    '문항 순번': 'count'  # Total questions
}).reset_index()

difficulty_stats.columns = ['난이도', '정답 수', '전체 문제 수']
difficulty_stats['정답률(%)'] = (difficulty_stats['정답 수'] / difficulty_stats['전체 문제 수'] * 100).round(2)

print("\n난이도별 정답률:")
print(difficulty_stats)

# Difficulty mapping based on English_reading skill.md
difficulty_mapping = {
    '★': '1번~4번 (star_⭐)',
    '★★': '5번~10번 (star_⭐⭐)',
    '★★★': '11번~16번 (star_⭐⭐⭐)',
    '★★★★': '17번~20번 (star_⭐⭐⭐⭐)'
}

# Create visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# Bar chart for accuracy rate
colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
bars = ax1.bar(range(len(difficulty_stats)), difficulty_stats['정답률(%)'], color=colors)
ax1.set_xticks(range(len(difficulty_stats)))
ax1.set_xticklabels(difficulty_stats['난이도'], fontsize=12)
ax1.set_ylabel('정답률 (%)', fontsize=12)
ax1.set_xlabel('난이도', fontsize=12)
ax1.set_title('정답 수 12~14점 학생들의 난이도별 정답률', fontsize=14, fontweight='bold')
ax1.set_ylim(0, 100)
ax1.grid(axis='y', alpha=0.3)

# Add percentage labels on bars
for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.1f}%',
             ha='center', va='bottom', fontsize=10, fontweight='bold')

# Stacked bar chart showing correct vs incorrect
difficulty_stats['오답 수'] = difficulty_stats['전체 문제 수'] - difficulty_stats['정답 수']

x = range(len(difficulty_stats))
ax2.bar(x, difficulty_stats['정답 수'], label='정답', color='#2ecc71')
ax2.bar(x, difficulty_stats['오답 수'], bottom=difficulty_stats['정답 수'], 
        label='오답', color='#e74c3c', alpha=0.7)

ax2.set_xticks(x)
ax2.set_xticklabels(difficulty_stats['난이도'], fontsize=12)
ax2.set_ylabel('문제 수', fontsize=12)
ax2.set_xlabel('난이도', fontsize=12)
ax2.set_title('난이도별 정답/오답 분포', fontsize=14, fontweight='bold')
ax2.legend(fontsize=10)
ax2.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('score_12_14_difficulty_analysis.png', dpi=300, bbox_inches='tight')
print("\n시각화 이미지 저장 완료: score_12_14_difficulty_analysis.png")

# Detailed analysis by question number
question_stats = students_12_14.groupby(['문항 순번', '난이도']).agg({
    '정답 여부': lambda x: (x == 'Y').sum(),
    '결과코드': 'count'
}).reset_index()

question_stats.columns = ['문항 순번', '난이도', '정답 수', '응답 수']
question_stats['정답률(%)'] = (question_stats['정답 수'] / question_stats['응답 수'] * 100).round(2)
question_stats = question_stats.sort_values('문항 순번')

print("\n문항별 상세 정답률:")
print(question_stats.to_string(index=False))

# Save results to CSV
difficulty_stats.to_csv('난이도별_정답률_12_14점.csv', index=False, encoding='utf-8-sig')
question_stats.to_csv('문항별_정답률_12_14점.csv', index=False, encoding='utf-8-sig')

print("\n결과 파일 저장 완료:")
print("  - 난이도별_정답률_12_14점.csv")
print("  - 문항별_정답률_12_14점.csv")
