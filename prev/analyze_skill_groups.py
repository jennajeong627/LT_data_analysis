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
print("GT1 학생 (12점 미만) 8개 Skill Group별 정답률 분석")
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

# Define 8 Skill Groups based on English reading skills
skill_groups = {
    'Recalling facts using details': [1, 5, 6, 12],
    'Drawing conclusions': [2, 7, 15, 16, 17, 20],
    'Determining cause/effect': [3, 19],
    'Analyzing characters': [4],
    'Summarizing details': [8, 13],
    'Interpreting graphic features': [9, 14],
    'Determining main ideas': [10],
    "Inferring author's purpose": [11, 18]
}

print("\n[2] Skill Group 정의:")
for group_name, items in skill_groups.items():
    items_str = ', '.join([f'S{i:02d}' for i in items])
    print(f"   {group_name}: {items_str}")

# Calculate accuracy for each skill group
print("\n[3] Calculating skill group accuracy...")
group_results = []

for group_name, item_numbers in skill_groups.items():
    # Filter data for items in this group
    group_data = df_target[df_target['문항 순번'].isin(item_numbers)]
    
    if len(group_data) == 0:
        continue
    
    total_attempts = len(group_data)
    correct_count = len(group_data[group_data['정답 여부'] == 'Y'])
    correct_rate = (correct_count / total_attempts * 100) if total_attempts > 0 else 0
    
    group_results.append({
        'Skill Group': group_name,
        '문항 수': len(item_numbers),
        '문항 번호': ', '.join([f'S{i:02d}' for i in sorted(item_numbers)]),
        '정답률': correct_rate,
        '정답수': correct_count,
        '시도수': total_attempts
    })
    
    print(f"   {group_name}: {correct_rate:.1f}%")

df_groups = pd.DataFrame(group_results)

# Sort by accuracy (highest first)
df_groups_sorted = df_groups.sort_values('정답률', ascending=False)

# Visualization: Horizontal bar chart
print("\n[4] Generating visualization...")
fig, ax = plt.subplots(figsize=(14, 10))

# Create color gradient based on accuracy
colors = []
for rate in df_groups_sorted['정답률']:
    if rate >= 70:
        colors.append('#48bb78')  # Green
    elif rate >= 50:
        colors.append('#38a169')  # Dark green
    elif rate >= 30:
        colors.append('#ed8936')  # Orange
    else:
        colors.append('#e53e3e')  # Red

y_positions = np.arange(len(df_groups_sorted))
bars = ax.barh(y_positions, df_groups_sorted['정답률'], color=colors, alpha=0.8, edgecolor='black', height=0.7)

# Add percentage labels
for i, (bar, rate) in enumerate(zip(bars, df_groups_sorted['정답률'])):
    width = bar.get_width()
    ax.text(width + 1, bar.get_y() + bar.get_height()/2.,
            f'{rate:.1f}%',
            ha='left', va='center', fontsize=11, fontweight='bold')

# Set y-axis labels (skill group names)
ax.set_yticks(y_positions)
ax.set_yticklabels(df_groups_sorted['Skill Group'], fontsize=10)

# Labels and title
ax.set_xlabel('정답률 (%)', fontsize=12, fontweight='bold')
ax.set_ylabel('Skill Group', fontsize=12, fontweight='bold')
ax.set_title(f'GT1 학생 (12점 미만, {len(low_score_students)}명) Skill Group별 정답률 - 높은 순', 
             fontsize=15, fontweight='bold', pad=20)
ax.set_xlim(0, 105)
ax.grid(axis='x', alpha=0.3, linestyle='--')

# Add legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#48bb78', label='70% 이상', alpha=0.8),
    Patch(facecolor='#38a169', label='50-70%', alpha=0.8),
    Patch(facecolor='#ed8936', label='30-50%', alpha=0.8),
    Patch(facecolor='#e53e3e', label='30% 미만', alpha=0.8)
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=10)

plt.tight_layout()
viz_path = os.path.join(output_dir, 'gt1_skill_groups_accuracy.png')
plt.savefig(viz_path, dpi=150, bbox_inches='tight')
print(f"[OK] Saved visualization: {viz_path}")
plt.close()

# Update English_reading skill.md
print("\n[5] Updating English_reading skill.md...")
md_path = 'English_reading skill.md'
with open(md_path, 'w', encoding='utf-8') as f:
    f.write("# GT1 학생 (12점 미만) Skill Group별 정답률 분석\n\n")
    f.write(f"**대상 학생 수**: {len(low_score_students)}명\n\n")
    
    f.write("## Skill Group 정의\n\n")
    f.write("| Skill Group | 문항 번호 | 문항 수 |\n")
    f.write("|-------------|-----------|--------|\n")
    for _, row in df_groups.iterrows():
        f.write(f"| {row['Skill Group']} | {row['문항 번호']} | {row['문항 수']} |\n")
    
    f.write("\n## Skill Group별 정답률 결과\n\n")
    f.write("정답률이 높은 순서로 정렬:\n\n")
    f.write("| 순위 | Skill Group | 문항 수 | 정답률 | 정답수 | 시도수 |\n")
    f.write("|------|-------------|---------|--------|--------|--------|\n")
    
    for rank, (_, row) in enumerate(df_groups_sorted.iterrows(), 1):
        f.write(f"| {rank} | {row['Skill Group']} | {row['문항 수']} | {row['정답률']:.1f}% | {row['정답수']} | {row['시도수']} |\n")
    
    f.write("\n## 시각화\n\n")
    f.write(f"![Skill Group Accuracy]({viz_path})\n")
    
    f.write("\n## 주요 발견사항\n\n")
    
    # Highest 3 groups
    f.write("### 정답률 상위 3개 Skill Group\n\n")
    for rank, (_, row) in enumerate(df_groups_sorted.head(3).iterrows(), 1):
        f.write(f"{rank}. **{row['Skill Group']}** ({row['문항 번호']}): {row['정답률']:.1f}%\n")
    
    # Lowest 3 groups
    f.write("\n### 정답률 하위 3개 Skill Group\n\n")
    for rank, (_, row) in enumerate(df_groups_sorted.tail(3).iloc[::-1].iterrows(), 1):
        f.write(f"{rank}. **{row['Skill Group']}** ({row['문항 번호']}): {row['정답률']:.1f}%\n")

print(f"[OK] Updated: {md_path}")

print("\n" + "=" * 80)
print("분석 완료!")
print("=" * 80)
print(f"\n생성된 파일:")
print(f"  1. {viz_path}")
print(f"  2. {md_path}")
print("\n" + "=" * 80)
