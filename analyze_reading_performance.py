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
print("Reading Performance Analysis - May 2024")
print("=" * 80)

# Load data
print("\n[1] Loading data...")
df = pd.read_csv('data/2024_5월_문항난이도별결과.csv', encoding='utf-8-sig')
print(f"   Total records: {len(df):,}")

# Select required columns
selected_cols = ['레벨', '난이도', '퀴즈 수', '정답 수', '전체 정답 수']
df_analysis = df[selected_cols].copy()

print(f"\n[2] Analyzing {len(selected_cols)} columns: {', '.join(selected_cols)}")

# ============================================================================
# PART 1: Performance by Difficulty Level
# ============================================================================
print("\n" + "=" * 80)
print("PART 1: Quiz Performance by Difficulty Level")
print("=" * 80)

# Group by difficulty level
difficulty_summary = df_analysis.groupby('난이도').agg({
    '퀴즈 수': 'first',  # Quiz count is the same for each difficulty
    '정답 수': 'sum'      # Sum of correct answers across all students
}).reset_index()

# Count students per difficulty
student_counts = df_analysis.groupby('난이도').size().reset_index(name='학생 수')
difficulty_summary = difficulty_summary.merge(student_counts, on='난이도')

# Calculate average correct answers
difficulty_summary['평균 정답 수'] = difficulty_summary['정답 수'] / difficulty_summary['학생 수']
difficulty_summary['정답률 (%)'] = (difficulty_summary['평균 정답 수'] / difficulty_summary['퀴즈 수'] * 100).round(2)

print("\n난이도별 퀴즈 수 및 정답 현황:")
print("-" * 80)
for _, row in difficulty_summary.iterrows():
    print(f"\n난이도: {row['난이도']}")
    print(f"  - 퀴즈 수: {row['퀴즈 수']}개")
    print(f"  - 총 정답 수: {row['정답 수']:,}개 (학생 {row['학생 수']:,}명)")
    print(f"  - 평균 정답 수: {row['평균 정답 수']:.2f}개")
    print(f"  - 평균 정답률: {row['정답률 (%)']}%")

# ============================================================================
# PART 2: Achievement Standard Assessment (standard_test_A criteria)
# ============================================================================
print("\n" + "=" * 80)
print("PART 2: Achievement Standard Assessment")
print("=" * 80)

# Define standard_test_A criteria (for 20 questions)
criteria = {
    'below2': (0, 6),
    'below1': (7, 11),
    'on': (12, 15),
    'above1': (16, 17),
    'above2': (18, 20)
}

print("\nStandard Test A 기준 (20문항):")
for segment, (min_score, max_score) in criteria.items():
    print(f"  - {segment}: {min_score}~{max_score}점")

# Get unique students (one row per student)
df_students = df.groupby(['레벨', '학생명', '전체 정답 수']).first().reset_index()

# Classify students by segment
def classify_segment(score):
    for segment, (min_score, max_score) in criteria.items():
        if min_score <= score <= max_score:
            return segment
    return 'unknown'

df_students['구간'] = df_students['전체 정답 수'].apply(classify_segment)

# Count students by level and segment
achievement_summary = df_students.groupby(['레벨', '구간']).size().unstack(fill_value=0)

# Reorder columns
segment_order = ['below2', 'below1', 'on', 'above1', 'above2']
achievement_summary = achievement_summary.reindex(columns=segment_order, fill_value=0)
achievement_summary['Total'] = achievement_summary.sum(axis=1)

print("\n레벨별 성취 기준 충족 현황:")
print("-" * 80)
print(achievement_summary.to_string())

# Calculate percentages
print("\n레벨별 성취 기준 충족 비율 (%):")
print("-" * 80)
achievement_pct = achievement_summary.div(achievement_summary['Total'], axis=0) * 100
achievement_pct = achievement_pct.drop('Total', axis=1).round(2)
print(achievement_pct.to_string())

# ============================================================================
# PART 3: GT1 Student Distribution Analysis
# ============================================================================
print("\n" + "=" * 80)
print("PART 3: GT1 Student Distribution Analysis")
print("=" * 80)

# Filter GT1 students
df_gt1 = df_students[df_students['레벨'] == 'GT1'].copy()
total_gt1 = len(df_gt1)

print(f"\nGT1 학생 총 인원: {total_gt1:,}명")

# Count GT1 students by segment
gt1_distribution = df_gt1['구간'].value_counts().reindex(segment_order, fill_value=0)

print("\nGT1 학생 구간별 분포:")
print("-" * 80)
for segment in segment_order:
    count = gt1_distribution[segment]
    percentage = (count / total_gt1 * 100) if total_gt1 > 0 else 0
    score_range = f"{criteria[segment][0]}~{criteria[segment][1]}점"
    print(f"{segment:10s} ({score_range:10s}): {count:5,}명 ({percentage:5.2f}%)")

# ============================================================================
# VISUALIZATIONS
# ============================================================================
print("\n" + "=" * 80)
print("Creating Visualizations")
print("=" * 80)

# Visualization 1: Difficulty Level Performance
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Bar chart: Quiz count and average correct answers by difficulty
ax1 = axes[0]
x = np.arange(len(difficulty_summary))
width = 0.35

bars1 = ax1.bar(x - width/2, difficulty_summary['퀴즈 수'], width, label='퀴즈 수', alpha=0.8)
bars2 = ax1.bar(x + width/2, difficulty_summary['평균 정답 수'], width, label='평균 정답 수', alpha=0.8)

ax1.set_xlabel('난이도', fontsize=12)
ax1.set_ylabel('개수', fontsize=12)
ax1.set_title('난이도별 퀴즈 수 및 평균 정답 수', fontsize=14, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(difficulty_summary['난이도'])
ax1.legend()
ax1.grid(axis='y', alpha=0.3)

# Add value labels on bars
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}',
                ha='center', va='bottom', fontsize=9)

# Bar chart: Accuracy rate by difficulty
ax2 = axes[1]
bars = ax2.bar(difficulty_summary['난이도'], difficulty_summary['정답률 (%)'], 
               color='steelblue', alpha=0.8)
ax2.set_xlabel('난이도', fontsize=12)
ax2.set_ylabel('정답률 (%)', fontsize=12)
ax2.set_title('난이도별 평균 정답률', fontsize=14, fontweight='bold')
ax2.set_ylim(0, 100)
ax2.grid(axis='y', alpha=0.3)

# Add value labels
for bar in bars:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.1f}%',
            ha='center', va='bottom', fontsize=10)

plt.tight_layout()
viz1_path = os.path.join(output_dir, 'difficulty_performance.png')
plt.savefig(viz1_path, dpi=150, bbox_inches='tight')
print(f"\n[OK] Saved: {viz1_path}")
plt.close()

# Visualization 2: GT1 Student Distribution
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Bar chart: GT1 distribution
ax1 = axes[0]
colors = ['#d62728', '#ff7f0e', '#2ca02c', '#1f77b4', '#9467bd']
bars = ax1.bar(segment_order, gt1_distribution.values, color=colors, alpha=0.8)
ax1.set_xlabel('구간', fontsize=12)
ax1.set_ylabel('학생 수', fontsize=12)
ax1.set_title('GT1 학생 구간별 분포', fontsize=14, fontweight='bold')
ax1.grid(axis='y', alpha=0.3)

# Add value labels and percentages
for i, (bar, segment) in enumerate(zip(bars, segment_order)):
    height = bar.get_height()
    percentage = (height / total_gt1 * 100) if total_gt1 > 0 else 0
    score_range = f"{criteria[segment][0]}-{criteria[segment][1]}"
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height):,}\n({percentage:.1f}%)',
            ha='center', va='bottom', fontsize=9)
    # Add score range below x-axis
    ax1.text(i, -max(gt1_distribution.values)*0.05, score_range,
            ha='center', va='top', fontsize=8, color='gray')

# Pie chart: GT1 distribution percentage
ax2 = axes[1]
wedges, texts, autotexts = ax2.pie(gt1_distribution.values, labels=segment_order, 
                                     autopct='%1.1f%%', colors=colors, startangle=90)
ax2.set_title('GT1 학생 구간별 비율', fontsize=14, fontweight='bold')

# Enhance pie chart text
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(10)

plt.tight_layout()
viz2_path = os.path.join(output_dir, 'gt1_distribution.png')
plt.savefig(viz2_path, dpi=150, bbox_inches='tight')
print(f"[OK] Saved: {viz2_path}")
plt.close()

# Visualization 3: All Levels Distribution Comparison
fig, ax = plt.subplots(figsize=(12, 6))

levels = ['GT1', 'MGT1', 'S1', 'MAG1']
x = np.arange(len(segment_order))
width = 0.2

for i, level in enumerate(levels):
    level_data = achievement_summary.loc[level, segment_order].values if level in achievement_summary.index else [0] * len(segment_order)
    ax.bar(x + i*width, level_data, width, label=level, alpha=0.8)

ax.set_xlabel('구간', fontsize=12)
ax.set_ylabel('학생 수', fontsize=12)
ax.set_title('레벨별 성취 기준 분포 비교', fontsize=14, fontweight='bold')
ax.set_xticks(x + width * 1.5)
ax.set_xticklabels(segment_order)
ax.legend(title='레벨', fontsize=10)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
viz3_path = os.path.join(output_dir, 'level_comparison.png')
plt.savefig(viz3_path, dpi=150, bbox_inches='tight')
print(f"[OK] Saved: {viz3_path}")
plt.close()

# ============================================================================
# SAVE SUMMARY REPORT
# ============================================================================
print("\n" + "=" * 80)
print("Saving Summary Report")
print("=" * 80)

report_path = os.path.join(output_dir, 'reading_performance_summary.txt')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("Reading Performance Analysis - May 2024\n")
    f.write("=" * 80 + "\n\n")
    
    f.write("PART 1: Quiz Performance by Difficulty Level\n")
    f.write("-" * 80 + "\n")
    f.write(difficulty_summary.to_string(index=False))
    f.write("\n\n")
    
    f.write("PART 2: Achievement Standard Assessment\n")
    f.write("-" * 80 + "\n")
    f.write("Student Counts by Level and Segment:\n")
    f.write(achievement_summary.to_string())
    f.write("\n\n")
    f.write("Percentage Distribution:\n")
    f.write(achievement_pct.to_string())
    f.write("\n\n")
    
    f.write("PART 3: GT1 Student Distribution\n")
    f.write("-" * 80 + "\n")
    f.write(f"Total GT1 Students: {total_gt1:,}\n\n")
    for segment in segment_order:
        count = gt1_distribution[segment]
        percentage = (count / total_gt1 * 100) if total_gt1 > 0 else 0
        score_range = f"{criteria[segment][0]}~{criteria[segment][1]}"
        f.write(f"{segment:10s} ({score_range:10s}): {count:5,} ({percentage:5.2f}%)\n")

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
