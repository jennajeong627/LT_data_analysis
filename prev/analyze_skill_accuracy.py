import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Set Korean font
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# Output directory
output_dir = r'C:\Users\user\.gemini\antigravity\brain\8fd772ef-33d9-4495-9894-ecaf33833f42'
os.makedirs(output_dir, exist_ok=True)

print("=" * 80)
print("GT1 학생 20개 Skill별 정답률 분석")
print("=" * 80)

# Load student-item level data
print("\n[1] Loading data...")
df_items = pd.read_csv('data/2024_5월_학생문항별결과.csv', encoding='utf-8-sig')

# Filter GT1
df_gt1 = df_items[df_items['레벨'] == 'GT1'].copy()
print(f"   GT1 records: {len(df_gt1):,}")

# Get unique students
total_students = df_gt1['학생명'].nunique()
print(f"   GT1 students: {total_students:,}")

# ============================================================================
# Skill Mapping (문항 번호 = Skill 번호)
# ============================================================================
print("\n[2] Skill 매핑...")

# 난이도별 문항 번호 매핑
difficulty_mapping = {
    '★': list(range(1, 5)),      # 1-4번
    '★★': list(range(5, 11)),    # 5-10번
    '★★★': list(range(11, 17)),  # 11-16번
    '★★★★': list(range(17, 21))  # 17-20번
}

# Skill 정의 (문항 번호 = Skill 번호)
skill_definitions = {}
for difficulty, item_nums in difficulty_mapping.items():
    for item_num in item_nums:
        skill_definitions[item_num] = {
            'skill_num': item_num,
            'difficulty': difficulty,
            'name': f'Skill {item_num:02d}'
        }

# ============================================================================
# PART 1: 각 Skill별 정답률 계산
# ============================================================================
print("\n" + "=" * 80)
print("PART 1: Skill별 정답률 분석")
print("=" * 80)

skill_results = []

for item_num in range(1, 21):
    # Filter data for this item
    item_data = df_gt1[df_gt1['문항 순번'] == item_num]
    
    if len(item_data) == 0:
        continue
    
    # Calculate statistics
    total_attempts = len(item_data)
    correct_count = len(item_data[item_data['정답 여부'] == 'Y'])
    wrong_count = len(item_data[item_data['정답 여부'] == 'N'])
    
    correct_rate = (correct_count / total_attempts * 100) if total_attempts > 0 else 0
    wrong_rate = (wrong_count / total_attempts * 100) if total_attempts > 0 else 0
    
    # Get difficulty
    difficulty = skill_definitions[item_num]['difficulty']
    
    skill_results.append({
        'Skill': item_num,
        'Skill_Name': f'Skill {item_num:02d}',
        '난이도': difficulty,
        '시도_수': total_attempts,
        '정답_수': correct_count,
        '오답_수': wrong_count,
        '정답률': correct_rate,
        '오답률': wrong_rate
    })
    
    print(f"Skill {item_num:02d} ({difficulty:4s}): 정답률 {correct_rate:5.1f}% ({correct_count:4,}/{total_attempts:4,})")

# Convert to DataFrame
df_skills = pd.DataFrame(skill_results)

# ============================================================================
# PART 2: 난이도별 평균 정답률
# ============================================================================
print("\n" + "=" * 80)
print("PART 2: 난이도별 평균 정답률")
print("=" * 80)

difficulty_stats = df_skills.groupby('난이도').agg({
    '정답률': 'mean',
    'Skill': 'count'
}).round(2)

difficulty_stats.columns = ['평균_정답률', 'Skill_수']

print("\n난이도별 통계:")
for difficulty in ['★', '★★', '★★★', '★★★★']:
    if difficulty in difficulty_stats.index:
        avg_rate = difficulty_stats.loc[difficulty, '평균_정답률']
        count = int(difficulty_stats.loc[difficulty, 'Skill_수'])
        print(f"  {difficulty:4s}: 평균 {avg_rate:5.1f}% ({count}개 문항)")

# ============================================================================
# VISUALIZATIONS
# ============================================================================
print("\n" + "=" * 80)
print("Creating Visualizations")
print("=" * 80)

# Visualization 1: Bar chart of all 20 skills
fig, ax = plt.subplots(figsize=(16, 8))

colors = []
for difficulty in df_skills['난이도']:
    if difficulty == '★':
        colors.append('#48bb78')
    elif difficulty == '★★':
        colors.append('#38a169')
    elif difficulty == '★★★':
        colors.append('#ed8936')
    else:  # ★★★★
        colors.append('#e53e3e')

bars = ax.bar(df_skills['Skill'], df_skills['정답률'], color=colors, alpha=0.8, edgecolor='black', linewidth=1.2)

# Add value labels
for bar, skill_num, rate in zip(bars, df_skills['Skill'], df_skills['정답률']):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{rate:.1f}%',
            ha='center', va='bottom', fontsize=9, fontweight='bold')

ax.set_xlabel('Skill 번호 (문항 번호)', fontsize=13, fontweight='bold')
ax.set_ylabel('정답률 (%)', fontsize=13, fontweight='bold')
ax.set_title('GT1 학생 20개 Skill별 정답률', fontsize=15, fontweight='bold', pad=20)
ax.set_xticks(range(1, 21))
ax.set_ylim(0, 100)
ax.grid(axis='y', alpha=0.3, linestyle='--')

# Add difficulty labels
ax.axvline(x=4.5, color='gray', linestyle='--', alpha=0.5)
ax.axvline(x=10.5, color='gray', linestyle='--', alpha=0.5)
ax.axvline(x=16.5, color='gray', linestyle='--', alpha=0.5)

ax.text(2.5, 95, '★', ha='center', fontsize=14, fontweight='bold', color='#48bb78')
ax.text(7.5, 95, '★★', ha='center', fontsize=14, fontweight='bold', color='#38a169')
ax.text(13.5, 95, '★★★', ha='center', fontsize=14, fontweight='bold', color='#ed8936')
ax.text(18.5, 95, '★★★★', ha='center', fontsize=14, fontweight='bold', color='#e53e3e')

# Add legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#48bb78', label='★ Basic (1-4)', alpha=0.8),
    Patch(facecolor='#38a169', label='★★ Literal (5-10)', alpha=0.8),
    Patch(facecolor='#ed8936', label='★★★ Inferential (11-16)', alpha=0.8),
    Patch(facecolor='#e53e3e', label='★★★★ Critical (17-20)', alpha=0.8)
]
ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

plt.tight_layout()
viz1_path = os.path.join(output_dir, 'gt1_skill_accuracy_by_item.png')
plt.savefig(viz1_path, dpi=150, bbox_inches='tight')
print(f"\n[OK] Saved: {viz1_path}")
plt.close()

# Visualization 2: Heatmap style visualization
fig, ax = plt.subplots(figsize=(16, 6))

# Create grid
skill_nums = df_skills['Skill'].values
rates = df_skills['정답률'].values

# Plot as colored rectangles
for i, (skill, rate) in enumerate(zip(skill_nums, rates)):
    # Color based on rate
    if rate >= 80:
        color = '#2f855a'
    elif rate >= 60:
        color = '#48bb78'
    elif rate >= 40:
        color = '#ed8936'
    else:
        color = '#e53e3e'
    
    rect = plt.Rectangle((i, 0), 1, 1, facecolor=color, edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    
    # Add text
    ax.text(i + 0.5, 0.5, f'S{skill:02d}\n{rate:.1f}%',
            ha='center', va='center', fontsize=10, fontweight='bold', color='white')

ax.set_xlim(0, 20)
ax.set_ylim(0, 1)
ax.set_xticks(np.arange(0.5, 20.5, 1))
ax.set_xticklabels(range(1, 21))
ax.set_yticks([])
ax.set_xlabel('Skill 번호', fontsize=13, fontweight='bold')
ax.set_title('GT1 Skill별 정답률 히트맵', fontsize=15, fontweight='bold', pad=20)

# Add difficulty separators
for x in [4, 10, 16]:
    ax.axvline(x=x, color='white', linewidth=3)

plt.tight_layout()
viz2_path = os.path.join(output_dir, 'gt1_skill_accuracy_heatmap.png')
plt.savefig(viz2_path, dpi=150, bbox_inches='tight')
print(f"[OK] Saved: {viz2_path}")
plt.close()

# Visualization 3: Grouped by difficulty
fig, ax = plt.subplots(figsize=(12, 7))

difficulty_order = ['★', '★★', '★★★', '★★★★']
difficulty_colors = ['#48bb78', '#38a169', '#ed8936', '#e53e3e']

x_pos = 0
x_labels = []
x_ticks = []

for difficulty, color in zip(difficulty_order, difficulty_colors):
    difficulty_skills = df_skills[df_skills['난이도'] == difficulty]
    
    for _, row in difficulty_skills.iterrows():
        bars = ax.bar(x_pos, row['정답률'], color=color, alpha=0.8, edgecolor='black', linewidth=1.2)
        
        # Add label
        ax.text(x_pos, row['정답률'] + 2, f"{row['정답률']:.1f}%",
                ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        x_labels.append(f"S{row['Skill']:02d}")
        x_ticks.append(x_pos)
        x_pos += 1
    
    x_pos += 0.5  # Gap between difficulty groups

ax.set_xlabel('Skill 번호', fontsize=12, fontweight='bold')
ax.set_ylabel('정답률 (%)', fontsize=12, fontweight='bold')
ax.set_title('GT1 Skill별 정답률 (난이도별 그룹)', fontsize=14, fontweight='bold', pad=15)
ax.set_xticks(x_ticks)
ax.set_xticklabels(x_labels, rotation=45, ha='right')
ax.set_ylim(0, 100)
ax.grid(axis='y', alpha=0.3)

# Add legend
legend_elements = [
    Patch(facecolor=color, label=f'{diff} ({len(df_skills[df_skills["난이도"]==diff])}개)', alpha=0.8)
    for diff, color in zip(difficulty_order, difficulty_colors)
]
ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

plt.tight_layout()
viz3_path = os.path.join(output_dir, 'gt1_skill_accuracy_grouped.png')
plt.savefig(viz3_path, dpi=150, bbox_inches='tight')
print(f"[OK] Saved: {viz3_path}")
plt.close()

# ============================================================================
# SAVE DETAILED REPORT
# ============================================================================
print("\n" + "=" * 80)
print("Saving Report")
print("=" * 80)

report_path = os.path.join(output_dir, 'gt1_skill_accuracy_report.txt')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("GT1 학생 20개 Skill별 정답률 분석\n")
    f.write("=" * 80 + "\n\n")
    
    f.write(f"총 학생 수: {total_students:,}명\n\n")
    
    f.write("Skill별 상세 정답률:\n")
    f.write("-" * 80 + "\n")
    f.write(f"{'Skill':<8} {'난이도':<6} {'시도수':<10} {'정답수':<10} {'오답수':<10} {'정답률':<10}\n")
    f.write("-" * 80 + "\n")
    
    for _, row in df_skills.iterrows():
        f.write(f"S{row['Skill']:02d}      {row['난이도']:4s}   "
                f"{row['시도_수']:6,}     {row['정답_수']:6,}     "
                f"{row['오답_수']:6,}     {row['정답률']:6.2f}%\n")
    
    f.write("\n\n난이도별 평균 정답률:\n")
    f.write("-" * 80 + "\n")
    for difficulty in difficulty_order:
        if difficulty in difficulty_stats.index:
            avg_rate = difficulty_stats.loc[difficulty, '평균_정답률']
            count = int(difficulty_stats.loc[difficulty, 'Skill_수'])
            f.write(f"{difficulty:4s}: 평균 {avg_rate:6.2f}% ({count}개 문항)\n")
    
    f.write("\n\n정답률 상위 5개 Skill:\n")
    f.write("-" * 80 + "\n")
    top5 = df_skills.nlargest(5, '정답률')
    for _, row in top5.iterrows():
        f.write(f"Skill {row['Skill']:02d} ({row['난이도']:4s}): {row['정답률']:.2f}%\n")
    
    f.write("\n\n정답률 하위 5개 Skill:\n")
    f.write("-" * 80 + "\n")
    bottom5 = df_skills.nsmallest(5, '정답률')
    for _, row in bottom5.iterrows():
        f.write(f"Skill {row['Skill']:02d} ({row['난이도']:4s}): {row['정답률']:.2f}%\n")

print(f"[OK] Saved: {report_path}")

# Save CSV for further analysis
csv_path = os.path.join(output_dir, 'gt1_skill_accuracy_data.csv')
df_skills.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f"[OK] Saved: {csv_path}")

print("\n" + "=" * 80)
print("Analysis Complete!")
print("=" * 80)
print(f"\nGenerated files:")
print(f"  1. {viz1_path}")
print(f"  2. {viz2_path}")
print(f"  3. {viz3_path}")
print(f"  4. {report_path}")
print(f"  5. {csv_path}")
print("\n" + "=" * 80)
