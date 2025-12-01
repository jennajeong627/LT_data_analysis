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
print("All Levels Reading Performance Analysis - May 2024")
print("=" * 80)

# Load data
print("\n[1] Loading data...")
df = pd.read_csv('data/2024_5월_문항난이도별결과.csv', encoding='utf-8-sig')
print(f"   Total records: {len(df):,}")

# Filter for target levels
target_levels = ['GT1', 'MGT1', 'S1', 'MAG1']
df_filtered = df[df['레벨'].isin(target_levels)].copy()
print(f"   Filtered records: {len(df_filtered):,}")

# Reading skills mapping
reading_skills = {
    '★': 'Basic Comprehension',
    '★★': 'Literal Understanding',
    '★★★': 'Inferential Reading',
    '★★★★': 'Critical Analysis'
}

# Standard test A criteria
criteria = {
    'below2': (0, 6),
    'below1': (7, 11),
    'on': (12, 15),
    'above1': (16, 17),
    'above2': (18, 20)
}

# ============================================================================
# PART 1: Overall Statistics by Level
# ============================================================================
print("\n" + "=" * 80)
print("PART 1: Overall Statistics by Level")
print("=" * 80)

# Get unique students
df_students = df_filtered.groupby(['레벨', '학생명', '전체 정답 수']).first().reset_index()

# Classify students by segment
def classify_segment(score):
    for segment, (min_score, max_score) in criteria.items():
        if min_score <= score <= max_score:
            return segment
    return 'unknown'

df_students['구간'] = df_students['전체 정답 수'].apply(classify_segment)

# Overall statistics by level
level_stats = df_students.groupby('레벨').agg({
    '전체 정답 수': ['count', 'mean', 'std', 'min', 'max']
}).round(2)

print("\nLevel Statistics:")
print("-" * 80)
print(level_stats.to_string())

# ============================================================================
# PART 2: Difficulty Performance by Level
# ============================================================================
print("\n" + "=" * 80)
print("PART 2: Difficulty Performance by Level")
print("=" * 80)

# Calculate performance by level and difficulty
difficulty_by_level = df_filtered.groupby(['레벨', '난이도']).agg({
    '퀴즈 수': 'first',
    '정답 수': 'sum'
}).reset_index()

# Count attempts
attempts = df_filtered.groupby(['레벨', '난이도']).size().reset_index(name='시도 수')
difficulty_by_level = difficulty_by_level.merge(attempts, on=['레벨', '난이도'])

# Calculate metrics
difficulty_by_level['평균 정답 수'] = difficulty_by_level['정답 수'] / difficulty_by_level['시도 수']
difficulty_by_level['정답률 (%)'] = (difficulty_by_level['평균 정답 수'] / difficulty_by_level['퀴즈 수'] * 100).round(2)

print("\nDifficulty Performance by Level:")
print("-" * 80)
for level in target_levels:
    level_data = difficulty_by_level[difficulty_by_level['레벨'] == level]
    print(f"\n{level}:")
    for _, row in level_data.iterrows():
        print(f"  {row['난이도']}: {row['정답률 (%)']}%")

# ============================================================================
# PART 3: Reading Skills Analysis by Level
# ============================================================================
print("\n" + "=" * 80)
print("PART 3: Reading Skills Analysis by Level")
print("=" * 80)

# Pivot for reading skills analysis
skills_pivot = df_filtered.pivot_table(
    index=['레벨', '학생명'],
    columns='난이도',
    values='정답 수',
    aggfunc='first'
).reset_index()

# Calculate achievement for each skill by level
skills_achievement = {}
for level in target_levels:
    level_students = skills_pivot[skills_pivot['레벨'] == level]
    level_achievement = {}
    
    for difficulty in ['★', '★★', '★★★', '★★★★']:
        if difficulty in skills_pivot.columns:
            quiz_count = difficulty_by_level[
                (difficulty_by_level['레벨'] == level) & 
                (difficulty_by_level['난이도'] == difficulty)
            ]['퀴즈 수'].values[0]
            
            threshold = quiz_count * 0.6
            achieved = (level_students[difficulty] >= threshold).sum()
            total = len(level_students)
            
            level_achievement[difficulty] = {
                'achieved': achieved,
                'total': total,
                'percentage': (achieved / total * 100) if total > 0 else 0
            }
    
    skills_achievement[level] = level_achievement

print("\nReading Skills Achievement by Level:")
print("-" * 80)
for level in target_levels:
    print(f"\n{level}:")
    for difficulty, skill in reading_skills.items():
        if difficulty in skills_achievement[level]:
            data = skills_achievement[level][difficulty]
            print(f"  {difficulty} {skill}: {data['percentage']:.2f}% ({data['achieved']}/{data['total']})")

# ============================================================================
# PART 4: Student Distribution by Level
# ============================================================================
print("\n" + "=" * 80)
print("PART 4: Student Distribution by Level")
print("=" * 80)

# Count students by level and segment
distribution = df_students.groupby(['레벨', '구간']).size().unstack(fill_value=0)
segment_order = ['below2', 'below1', 'on', 'above1', 'above2']
distribution = distribution.reindex(columns=segment_order, fill_value=0)
distribution['Total'] = distribution.sum(axis=1)

print("\nStudent Distribution by Level and Segment:")
print("-" * 80)
print(distribution.to_string())

# Calculate percentages
distribution_pct = distribution.div(distribution['Total'], axis=0) * 100
distribution_pct = distribution_pct.drop('Total', axis=1).round(2)

print("\nPercentage Distribution:")
print("-" * 80)
print(distribution_pct.to_string())

# ============================================================================
# VISUALIZATIONS
# ============================================================================
print("\n" + "=" * 80)
print("Creating Visualizations")
print("=" * 80)

# Visualization 1: Difficulty Performance Comparison
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
axes = axes.flatten()

difficulties = ['★', '★★', '★★★', '★★★★']
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

for idx, level in enumerate(target_levels):
    ax = axes[idx]
    level_data = difficulty_by_level[difficulty_by_level['레벨'] == level]
    
    bars = ax.bar(difficulties, level_data['정답률 (%)'].values, color=colors[idx], alpha=0.8)
    ax.set_xlabel('난이도', fontsize=11)
    ax.set_ylabel('정답률 (%)', fontsize=11)
    ax.set_title(f'{level} - 난이도별 정답률', fontsize=13, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.grid(axis='y', alpha=0.3)
    ax.axhline(y=60, color='red', linestyle='--', alpha=0.5, label='기대치 (60%)')
    ax.legend()
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
viz1_path = os.path.join(output_dir, 'all_levels_difficulty_performance.png')
plt.savefig(viz1_path, dpi=150, bbox_inches='tight')
print(f"\n[OK] Saved: {viz1_path}")
plt.close()

# Visualization 2: Reading Skills Heatmap
fig, ax = plt.subplots(figsize=(12, 8))

# Create matrix for heatmap
skills_matrix = []
for level in target_levels:
    row = []
    for difficulty in difficulties:
        if difficulty in skills_achievement[level]:
            row.append(skills_achievement[level][difficulty]['percentage'])
        else:
            row.append(0)
    skills_matrix.append(row)

skills_matrix = np.array(skills_matrix)

im = ax.imshow(skills_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)

# Set ticks and labels
ax.set_xticks(np.arange(len(difficulties)))
ax.set_yticks(np.arange(len(target_levels)))
ax.set_xticklabels([f"{d}\n{reading_skills[d]}" for d in difficulties], fontsize=10)
ax.set_yticklabels(target_levels, fontsize=11)

# Add colorbar
cbar = plt.colorbar(im, ax=ax)
cbar.set_label('성취율 (%)', rotation=270, labelpad=20, fontsize=11)

# Add text annotations
for i in range(len(target_levels)):
    for j in range(len(difficulties)):
        text = ax.text(j, i, f'{skills_matrix[i, j]:.1f}%',
                      ha="center", va="center", color="black", fontsize=10, fontweight='bold')

ax.set_title('전체 레벨 Reading Skills 성취율 히트맵', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
viz2_path = os.path.join(output_dir, 'all_levels_skills_heatmap.png')
plt.savefig(viz2_path, dpi=150, bbox_inches='tight')
print(f"[OK] Saved: {viz2_path}")
plt.close()

# Visualization 3: Student Distribution Stacked Bar
fig, ax = plt.subplots(figsize=(12, 7))

x = np.arange(len(target_levels))
width = 0.6
colors_segments = ['#e53e3e', '#ed8936', '#48bb78', '#38a169', '#2f855a']

bottom = np.zeros(len(target_levels))
for idx, segment in enumerate(segment_order):
    values = distribution_pct[segment].values
    bars = ax.bar(x, values, width, label=segment, bottom=bottom, 
                  color=colors_segments[idx], alpha=0.9)
    
    # Add percentage labels
    for i, (bar, val) in enumerate(zip(bars, values)):
        if val > 3:  # Only show label if segment is large enough
            ax.text(bar.get_x() + bar.get_width()/2., bottom[i] + val/2,
                   f'{val:.1f}%', ha='center', va='center', 
                   fontsize=9, fontweight='bold', color='white')
    
    bottom += values

ax.set_xlabel('레벨', fontsize=12)
ax.set_ylabel('학생 비율 (%)', fontsize=12)
ax.set_title('레벨별 학생 구간 분포', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(target_levels, fontsize=11)
ax.legend(title='구간', loc='upper left', bbox_to_anchor=(1, 1))
ax.set_ylim(0, 100)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
viz3_path = os.path.join(output_dir, 'all_levels_distribution.png')
plt.savefig(viz3_path, dpi=150, bbox_inches='tight')
print(f"[OK] Saved: {viz3_path}")
plt.close()

# Visualization 4: Comparative Line Chart - Difficulty Performance
fig, ax = plt.subplots(figsize=(12, 7))

for idx, level in enumerate(target_levels):
    level_data = difficulty_by_level[difficulty_by_level['레벨'] == level]
    ax.plot(difficulties, level_data['정답률 (%)'].values, 
            marker='o', linewidth=2, markersize=8, label=level, color=colors[idx])

ax.set_xlabel('난이도', fontsize=12)
ax.set_ylabel('정답률 (%)', fontsize=12)
ax.set_title('레벨별 난이도 정답률 비교', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)
ax.axhline(y=60, color='red', linestyle='--', alpha=0.5, label='기대치 (60%)')
ax.set_ylim(0, 100)

plt.tight_layout()
viz4_path = os.path.join(output_dir, 'all_levels_difficulty_comparison.png')
plt.savefig(viz4_path, dpi=150, bbox_inches='tight')
print(f"[OK] Saved: {viz4_path}")
plt.close()

# Visualization 5: Average Score Comparison
fig, ax = plt.subplots(figsize=(10, 6))

avg_scores = df_students.groupby('레벨')['전체 정답 수'].mean().reindex(target_levels)
bars = ax.bar(target_levels, avg_scores.values, color=colors, alpha=0.8)

ax.set_xlabel('레벨', fontsize=12)
ax.set_ylabel('평균 정답 수', fontsize=12)
ax.set_title('레벨별 평균 정답 수 비교', fontsize=14, fontweight='bold')
ax.axhline(y=12, color='green', linestyle='--', alpha=0.5, label='"on" 기준 (12점)')
ax.legend()
ax.grid(axis='y', alpha=0.3)
ax.set_ylim(0, 20)

# Add value labels
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.2f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
viz5_path = os.path.join(output_dir, 'all_levels_average_scores.png')
plt.savefig(viz5_path, dpi=150, bbox_inches='tight')
print(f"[OK] Saved: {viz5_path}")
plt.close()

# ============================================================================
# SAVE SUMMARY REPORT
# ============================================================================
print("\n" + "=" * 80)
print("Saving Summary Report")
print("=" * 80)

report_path = os.path.join(output_dir, 'all_levels_analysis_report.txt')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("All Levels Reading Performance Analysis - May 2024\n")
    f.write("=" * 80 + "\n\n")
    
    f.write("Overall Statistics by Level:\n")
    f.write("-" * 80 + "\n")
    f.write(level_stats.to_string())
    f.write("\n\n")
    
    f.write("Student Distribution by Level:\n")
    f.write("-" * 80 + "\n")
    f.write(distribution.to_string())
    f.write("\n\n")
    
    f.write("Percentage Distribution:\n")
    f.write("-" * 80 + "\n")
    f.write(distribution_pct.to_string())
    f.write("\n\n")
    
    f.write("Difficulty Performance by Level:\n")
    f.write("-" * 80 + "\n")
    for level in target_levels:
        f.write(f"\n{level}:\n")
        level_data = difficulty_by_level[difficulty_by_level['레벨'] == level]
        for _, row in level_data.iterrows():
            f.write(f"  {row['난이도']}: {row['정답률 (%)']}%\n")
    
    f.write("\n\nReading Skills Achievement by Level:\n")
    f.write("-" * 80 + "\n")
    for level in target_levels:
        f.write(f"\n{level}:\n")
        for difficulty, skill in reading_skills.items():
            if difficulty in skills_achievement[level]:
                data = skills_achievement[level][difficulty]
                f.write(f"  {difficulty} {skill}: {data['percentage']:.2f}% ({data['achieved']}/{data['total']})\n")

print(f"[OK] Saved: {report_path}")

# Save data for dashboard
import json
data_path = os.path.join(output_dir, 'all_levels_data.json')

# Convert to JSON-serializable format
json_data = {
    'distribution': {str(k): v for k, v in distribution.to_dict('index').items()},
    'distribution_pct': {str(k): v for k, v in distribution_pct.to_dict('index').items()},
    'difficulty_by_level': difficulty_by_level.to_dict('records'),
    'skills_achievement': {
        level: {
            diff: {
                'achieved': int(data['achieved']),
                'total': int(data['total']),
                'percentage': float(data['percentage'])
            }
            for diff, data in skills.items()
        }
        for level, skills in skills_achievement.items()
    },
    'target_levels': target_levels,
    'segment_order': segment_order
}

with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(json_data, f, ensure_ascii=False, indent=2)

print(f"[OK] Saved: {data_path}")

print("\n" + "=" * 80)
print("Analysis Complete!")
print("=" * 80)
print(f"\nGenerated files:")
print(f"  1. {viz1_path}")
print(f"  2. {viz2_path}")
print(f"  3. {viz3_path}")
print(f"  4. {viz4_path}")
print(f"  5. {viz5_path}")
print(f"  6. {report_path}")
print(f"  7. {data_path}")
print("\n" + "=" * 80)
