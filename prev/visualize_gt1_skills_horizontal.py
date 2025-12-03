import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Set Korean font
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# Output directory
output_dir = 'images'
os.makedirs(output_dir, exist_ok=True)

print("=" * 80)
print("GT1 학생 (정답수 12점 미만) 20개 Skill별 정답률 분석 - 가로 막대 그래프")
print("=" * 80)

# Load data
print("\n[1] Loading data...")
df_items = pd.read_csv('data/2024_5월_학생문항별결과.csv', encoding='utf-8-sig')

# Filter GT1
df_gt1 = df_items[df_items['레벨'] == 'GT1'].copy()
print(f"   Total GT1 records: {len(df_gt1):,}")

# Calculate total score per student
student_scores = df_gt1.groupby('학생명')['정답 여부'].apply(lambda x: (x == 'Y').sum()).reset_index()
student_scores.columns = ['학생명', '총_정답수']

# Filter students with score < 12
low_score_students = student_scores[student_scores['총_정답수'] < 12]['학생명'].unique()
print(f"   GT1 students with score < 12: {len(low_score_students):,}")

# Filter item data for these students
df_target = df_gt1[df_gt1['학생명'].isin(low_score_students)].copy()
print(f"   Target records: {len(df_target):,}")

# Difficulty mapping
difficulty_mapping = {
    '★': list(range(1, 5)),      # 1-4
    '★★': list(range(5, 11)),    # 5-10
    '★★★': list(range(11, 17)),  # 11-16
    '★★★★': list(range(17, 21))  # 17-20
}

skill_definitions = {}
for difficulty, item_nums in difficulty_mapping.items():
    for item_num in item_nums:
        skill_definitions[item_num] = difficulty

# Calculate accuracy per skill (item)
skill_results = []

print("\n[2] Calculating skill accuracy...")
for item_num in range(1, 21):
    item_data = df_target[df_target['문항 순번'] == item_num]
    
    if len(item_data) == 0:
        continue
        
    total_attempts = len(item_data)
    correct_count = len(item_data[item_data['정답 여부'] == 'Y'])
    correct_rate = (correct_count / total_attempts * 100) if total_attempts > 0 else 0
    
    difficulty = skill_definitions.get(item_num, 'Unknown')
    
    skill_results.append({
        'Skill': f'S{item_num:02d}',
        'Skill_Num': item_num,
        '난이도': difficulty,
        '정답률': correct_rate,
        '정답수': correct_count,
        '시도수': total_attempts
    })

df_skills = pd.DataFrame(skill_results)

# Sort by accuracy (descending - highest at bottom, lowest at top)
df_skills_sorted = df_skills.sort_values('정답률', ascending=False).reset_index(drop=True)

# Visualization - Horizontal bar chart
print("\n[3] Generating horizontal bar chart...")
fig, ax = plt.subplots(figsize=(12, 10))

# Color mapping
colors = []
for difficulty in df_skills_sorted['난이도']:
    if difficulty == '★': 
        colors.append('#48bb78')
    elif difficulty == '★★': 
        colors.append('#38a169')
    elif difficulty == '★★★': 
        colors.append('#ed8936')
    else: 
        colors.append('#e53e3e')

# Create horizontal bars
y_positions = np.arange(len(df_skills_sorted))
bars = ax.barh(y_positions, df_skills_sorted['정답률'], color=colors, alpha=0.8, edgecolor='black')

# Add percentage labels at the end of bars
for i, (bar, rate) in enumerate(zip(bars, df_skills_sorted['정답률'])):
    width = bar.get_width()
    ax.text(width + 1, bar.get_y() + bar.get_height()/2.,
            f'{rate:.1f}%',
            ha='left', va='center', fontsize=9, fontweight='bold')

# Set y-axis labels (skill names)
ax.set_yticks(y_positions)
ax.set_yticklabels(df_skills_sorted['Skill'], fontsize=10)

# Labels and title
ax.set_xlabel('정답률 (%)', fontsize=12, fontweight='bold')
ax.set_ylabel('Skill 번호 (문항 번호)', fontsize=12, fontweight='bold')
ax.set_title(f'GT1 학생 (12점 미만, {len(low_score_students)}명) Skill별 정답률\n(정답률 높은 순 → 낮은 순)', 
             fontsize=14, fontweight='bold', pad=20)

ax.set_xlim(0, 105)
ax.grid(axis='x', alpha=0.3, linestyle='--')

# Add difficulty legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#48bb78', label='★ Basic (1-4)'),
    Patch(facecolor='#38a169', label='★★ Literal (5-10)'),
    Patch(facecolor='#ed8936', label='★★★ Inferential (11-16)'),
    Patch(facecolor='#e53e3e', label='★★★★ Critical (17-20)')
]
ax.legend(handles=legend_elements, loc='lower right')

plt.tight_layout()
viz_path = os.path.join(output_dir, 'gt1_low_score_skills_horizontal.png')
plt.savefig(viz_path, dpi=150, bbox_inches='tight')
print(f"[OK] Saved visualization: {viz_path}")
plt.close()

# Print sorted results
print("\n[4] Skill별 정답률 (높은 순):")
print("-" * 60)
print(f"{'Skill':<8} {'난이도':<8} {'정답률':<10}")
print("-" * 60)
for _, row in df_skills_sorted.iterrows():
    print(f"{row['Skill']:<8} {row['난이도']:<8} {row['정답률']:>6.1f}%")

print("\n" + "=" * 80)
print("분석 완료!")
print("=" * 80)
