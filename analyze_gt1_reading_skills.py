import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib import font_manager

# Set Korean font for matplotlib
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# Create output directory for artifacts
output_dir = r'C:\Users\user\.gemini\antigravity\brain\8fd772ef-33d9-4495-9894-ecaf33833f42'
os.makedirs(output_dir, exist_ok=True)

print("=" * 80)
print("GT1 Reading Skills Analysis by Difficulty Level")
print("=" * 80)

# Load data
print("\n[1] Loading data...")
df = pd.read_csv('data/2024_5월_문항난이도별결과.csv', encoding='utf-8-sig')

# Filter GT1 students only
df_gt1 = df[df['레벨'] == 'GT1'].copy()
print(f"   GT1 records: {len(df_gt1):,}")

# Map difficulty levels to reading skills
reading_skills = {
    '★': 'Basic Comprehension\n(기본 이해)',
    '★★': 'Literal Understanding\n(문자적 이해)',
    '★★★': 'Inferential Reading\n(추론적 읽기)',
    '★★★★': 'Critical Analysis\n(비판적 분석)'
}

print("\n[2] Reading Skills Mapping:")
for difficulty, skill in reading_skills.items():
    print(f"   {difficulty} → {skill}")

# ============================================================================
# PART 1: GT1 Performance by Difficulty/Reading Skill
# ============================================================================
print("\n" + "=" * 80)
print("PART 1: GT1 Performance by Reading Skill")
print("=" * 80)

# Calculate performance metrics by difficulty
gt1_performance = df_gt1.groupby('난이도').agg({
    '퀴즈 수': 'first',
    '정답 수': 'sum'
}).reset_index()

# Count total attempts (students × questions)
student_counts = df_gt1.groupby('난이도').size().reset_index(name='총 시도 수')
gt1_performance = gt1_performance.merge(student_counts, on='난이도')

# Calculate metrics
gt1_performance['평균 정답 수'] = gt1_performance['정답 수'] / gt1_performance['총 시도 수']
gt1_performance['정답률 (%)'] = (gt1_performance['평균 정답 수'] / gt1_performance['퀴즈 수'] * 100).round(2)
gt1_performance['Reading Skill'] = gt1_performance['난이도'].map(reading_skills)

# Calculate expected vs actual
gt1_performance['기대 정답률 (%)'] = 60.0  # "on" standard minimum
gt1_performance['차이 (%)'] = gt1_performance['정답률 (%)'] - gt1_performance['기대 정답률 (%)']

print("\nGT1 학생들의 Reading Skill별 성취도:")
print("-" * 80)
for _, row in gt1_performance.iterrows():
    status = "[O] 성취" if row['차이 (%)'] >= 0 else "[X] 부족"
    print(f"\n{row['난이도']} - {row['Reading Skill']}")
    print(f"  퀴즈 수: {row['퀴즈 수']}개")
    print(f"  평균 정답 수: {row['평균 정답 수']:.2f}개 / {row['퀴즈 수']}개")
    print(f"  정답률: {row['정답률 (%)']}%")
    print(f"  기대 정답률: {row['기대 정답률 (%)']}%")
    print(f"  차이: {row['차이 (%)']:+.2f}% -> {status}")

# Identify strengths and weaknesses
strengths = gt1_performance[gt1_performance['차이 (%)'] >= 0].sort_values('차이 (%)', ascending=False)
weaknesses = gt1_performance[gt1_performance['차이 (%)'] < 0].sort_values('차이 (%)')

print("\n" + "=" * 80)
print("강점 (Strengths):")
print("-" * 80)
if len(strengths) > 0:
    for _, row in strengths.iterrows():
        print(f"  [O] {row['난이도']} {row['Reading Skill']}: {row['정답률 (%)']}% (기대치 대비 +{row['차이 (%)']:.2f}%)")
else:
    print("  없음 - 모든 영역에서 기대치 미달")

print("\n약점 (Weaknesses):")
print("-" * 80)
if len(weaknesses) > 0:
    for _, row in weaknesses.iterrows():
        print(f"  [X] {row['난이도']} {row['Reading Skill']}: {row['정답률 (%)']}% (기대치 대비 {row['차이 (%)']:.2f}%)")
else:
    print("  없음 - 모든 영역에서 기대치 충족")

# ============================================================================
# PART 2: Individual Student Analysis
# ============================================================================
print("\n" + "=" * 80)
print("PART 2: GT1 학생별 Reading Skill 성취 분석")
print("=" * 80)

# Get unique students with their scores by difficulty
df_gt1_pivot = df_gt1.pivot_table(
    index=['학생명', '전체 정답 수'],
    columns='난이도',
    values='정답 수',
    aggfunc='first'
).reset_index()

# Calculate achievement for each skill
for difficulty in ['★', '★★', '★★★', '★★★★']:
    if difficulty in df_gt1_pivot.columns:
        quiz_count = gt1_performance[gt1_performance['난이도'] == difficulty]['퀴즈 수'].values[0]
        threshold = quiz_count * 0.6  # 60% threshold
        df_gt1_pivot[f'{difficulty}_성취'] = df_gt1_pivot[difficulty] >= threshold

# Count students achieving each skill
achievement_counts = {}
for difficulty in ['★', '★★', '★★★', '★★★★']:
    if f'{difficulty}_성취' in df_gt1_pivot.columns:
        achieved = df_gt1_pivot[f'{difficulty}_성취'].sum()
        total = len(df_gt1_pivot)
        achievement_counts[difficulty] = {
            'achieved': achieved,
            'total': total,
            'percentage': (achieved / total * 100) if total > 0 else 0
        }

print("\nReading Skill별 성취 학생 수:")
print("-" * 80)
for difficulty, skill in reading_skills.items():
    if difficulty in achievement_counts:
        data = achievement_counts[difficulty]
        print(f"{difficulty} {skill}")
        print(f"  성취: {data['achieved']:,}명 / {data['total']:,}명 ({data['percentage']:.2f}%)")

# ============================================================================
# VISUALIZATIONS
# ============================================================================
print("\n" + "=" * 80)
print("Creating Visualizations")
print("=" * 80)

# Visualization 1: Performance vs Expected
fig, ax = plt.subplots(figsize=(12, 6))

x = np.arange(len(gt1_performance))
width = 0.35

bars1 = ax.bar(x - width/2, gt1_performance['정답률 (%)'], width, 
               label='실제 정답률', color='steelblue', alpha=0.8)
bars2 = ax.bar(x + width/2, gt1_performance['기대 정답률 (%)'], width,
               label='기대 정답률 (60%)', color='orange', alpha=0.8)

ax.set_xlabel('Reading Skill (난이도)', fontsize=12)
ax.set_ylabel('정답률 (%)', fontsize=12)
ax.set_title('GT1 학생 Reading Skill별 성취도 비교', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels([f"{row['난이도']}\n{row['Reading Skill']}" 
                     for _, row in gt1_performance.iterrows()], fontsize=9)
ax.legend(fontsize=10)
ax.grid(axis='y', alpha=0.3)
ax.axhline(y=60, color='red', linestyle='--', alpha=0.5, label='최소 기대치')

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom', fontsize=9)

plt.tight_layout()
viz1_path = os.path.join(output_dir, 'gt1_reading_skills_performance.png')
plt.savefig(viz1_path, dpi=150, bbox_inches='tight')
print(f"\n[OK] Saved: {viz1_path}")
plt.close()

# Visualization 2: Achievement Rate by Skill
fig, ax = plt.subplots(figsize=(10, 6))

skills_list = []
achieved_pct = []
not_achieved_pct = []

for difficulty in ['★', '★★', '★★★', '★★★★']:
    if difficulty in achievement_counts:
        skills_list.append(f"{difficulty}\n{reading_skills[difficulty]}")
        achieved_pct.append(achievement_counts[difficulty]['percentage'])
        not_achieved_pct.append(100 - achievement_counts[difficulty]['percentage'])

x = np.arange(len(skills_list))
width = 0.6

bars1 = ax.bar(x, achieved_pct, width, label='성취', color='#2ca02c', alpha=0.8)
bars2 = ax.bar(x, not_achieved_pct, width, bottom=achieved_pct, 
               label='미성취', color='#d62728', alpha=0.8)

ax.set_xlabel('Reading Skill', fontsize=12)
ax.set_ylabel('학생 비율 (%)', fontsize=12)
ax.set_title('GT1 학생 Reading Skill별 성취 비율', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(skills_list, fontsize=9)
ax.legend(fontsize=10)
ax.set_ylim(0, 100)
ax.grid(axis='y', alpha=0.3)

# Add percentage labels
for i, (a_pct, na_pct) in enumerate(zip(achieved_pct, not_achieved_pct)):
    if a_pct > 5:
        ax.text(i, a_pct/2, f'{a_pct:.1f}%', ha='center', va='center', 
                fontsize=10, fontweight='bold', color='white')
    if na_pct > 5:
        ax.text(i, a_pct + na_pct/2, f'{na_pct:.1f}%', ha='center', va='center',
                fontsize=10, fontweight='bold', color='white')

plt.tight_layout()
viz2_path = os.path.join(output_dir, 'gt1_reading_skills_achievement.png')
plt.savefig(viz2_path, dpi=150, bbox_inches='tight')
print(f"[OK] Saved: {viz2_path}")
plt.close()

# Visualization 3: Heatmap-style comparison
fig, ax = plt.subplots(figsize=(10, 6))

# Create data for heatmap
metrics = ['정답률 (%)', '성취 학생 비율 (%)']
data_matrix = []

for difficulty in ['★', '★★', '★★★', '★★★★']:
    row_data = []
    # Accuracy rate
    acc = gt1_performance[gt1_performance['난이도'] == difficulty]['정답률 (%)'].values[0]
    row_data.append(acc)
    # Achievement rate
    if difficulty in achievement_counts:
        ach = achievement_counts[difficulty]['percentage']
        row_data.append(ach)
    else:
        row_data.append(0)
    data_matrix.append(row_data)

data_matrix = np.array(data_matrix)

im = ax.imshow(data_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)

# Set ticks and labels
ax.set_xticks(np.arange(len(metrics)))
ax.set_yticks(np.arange(len(['★', '★★', '★★★', '★★★★'])))
ax.set_xticklabels(metrics, fontsize=11)
ax.set_yticklabels([f"{d}\n{reading_skills[d]}" for d in ['★', '★★', '★★★', '★★★★']], 
                    fontsize=9)

# Add colorbar
cbar = plt.colorbar(im, ax=ax)
cbar.set_label('비율 (%)', rotation=270, labelpad=20, fontsize=11)

# Add text annotations
for i in range(len(['★', '★★', '★★★', '★★★★'])):
    for j in range(len(metrics)):
        text = ax.text(j, i, f'{data_matrix[i, j]:.1f}%',
                      ha="center", va="center", color="black", fontsize=11, fontweight='bold')

ax.set_title('GT1 Reading Skill 성취도 히트맵', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
viz3_path = os.path.join(output_dir, 'gt1_reading_skills_heatmap.png')
plt.savefig(viz3_path, dpi=150, bbox_inches='tight')
print(f"[OK] Saved: {viz3_path}")
plt.close()

# ============================================================================
# SAVE SUMMARY REPORT
# ============================================================================
print("\n" + "=" * 80)
print("Saving Summary Report")
print("=" * 80)

report_path = os.path.join(output_dir, 'gt1_reading_skills_report.txt')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("GT1 Reading Skills Analysis - May 2024\n")
    f.write("=" * 80 + "\n\n")
    
    f.write("Reading Skills Mapping:\n")
    f.write("-" * 80 + "\n")
    for difficulty, skill in reading_skills.items():
        f.write(f"{difficulty} → {skill}\n")
    
    f.write("\n\nPerformance by Reading Skill:\n")
    f.write("-" * 80 + "\n")
    f.write(gt1_performance[['난이도', 'Reading Skill', '퀴즈 수', '평균 정답 수', '정답률 (%)', '차이 (%)']].to_string(index=False))
    
    f.write("\n\n강점 (Strengths):\n")
    f.write("-" * 80 + "\n")
    if len(strengths) > 0:
        for _, row in strengths.iterrows():
            f.write(f"[O] {row['난이도']} {row['Reading Skill']}: {row['정답률 (%)']}% (+{row['차이 (%)']:.2f}%)\n")
    else:
        f.write("없음\n")
    
    f.write("\n약점 (Weaknesses):\n")
    f.write("-" * 80 + "\n")
    if len(weaknesses) > 0:
        for _, row in weaknesses.iterrows():
            f.write(f"[X] {row['난이도']} {row['Reading Skill']}: {row['정답률 (%)']}% ({row['차이 (%)']:.2f}%)\n")
    else:
        f.write("없음\n")
    
    f.write("\n\nAchievement Rates:\n")
    f.write("-" * 80 + "\n")
    for difficulty, skill in reading_skills.items():
        if difficulty in achievement_counts:
            data = achievement_counts[difficulty]
            f.write(f"{difficulty} {skill}: {data['achieved']:,}/{data['total']:,} ({data['percentage']:.2f}%)\n")

print(f"[OK] Saved: {report_path}")

print("\n" + "=" * 80)
print("Analysis Complete!")
print("=" * 80)
print(f"\nGenerated files:")
print(f"  1. {viz1_path}")
print(f"  2. {viz2_path}")
print(f"  3. {viz3_path}")
print(f"  4. {report_path}")
print("\n" + "=" * 80)
