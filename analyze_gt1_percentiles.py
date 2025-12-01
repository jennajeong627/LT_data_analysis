import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Set Korean font
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# Output directory
output_dir = r'C:\Users\user\.gemini\antigravity\brain\8fd772ef-33d9-4495-9894-ecaf33833f42'
os.makedirs(output_dir, exist_ok=True)

print("=" * 80)
print("GT1 Score Distribution and Percentile Analysis")
print("=" * 80)

# Load data
print("\n[1] Loading data...")
df = pd.read_csv('data/2024_5월_문항난이도별결과.csv', encoding='utf-8-sig')
df_gt1 = df[df['레벨'] == 'GT1'].copy()

# Get unique students with their scores
df_students = df_gt1.groupby(['학생명', '전체 정답 수']).first().reset_index()
total_students = len(df_students)

print(f"   Total GT1 students: {total_students:,}")

# ============================================================================
# PART 1: Score Distribution
# ============================================================================
print("\n" + "=" * 80)
print("PART 1: Score Distribution")
print("=" * 80)

# Count students by score
score_dist = df_students['전체 정답 수'].value_counts().sort_index()

print("\nScore Distribution (0-20):")
print("-" * 80)
print(f"{'Score':<10} {'Count':<10} {'Percentage':<15} {'Cumulative %':<15}")
print("-" * 80)

cumulative_count = 0
for score in range(21):
    count = score_dist.get(score, 0)
    percentage = (count / total_students * 100)
    cumulative_count += count
    cumulative_pct = (cumulative_count / total_students * 100)
    
    if count > 0:
        print(f"{score:<10} {count:<10} {percentage:>6.2f}%{'':<8} {cumulative_pct:>6.2f}%")

# ============================================================================
# PART 2: Percentile Calculation
# ============================================================================
print("\n" + "=" * 80)
print("PART 2: Percentile Analysis")
print("=" * 80)

# Calculate percentiles
percentiles = [0, 10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90, 100]
percentile_scores = np.percentile(df_students['전체 정답 수'], percentiles)

print("\nPercentile to Score Mapping:")
print("-" * 80)
print(f"{'Percentile':<15} {'Score':<10} {'Interpretation'}")
print("-" * 80)

for pct, score in zip(percentiles, percentile_scores):
    if pct == 0:
        interp = "Minimum score"
    elif pct == 25:
        interp = "1st Quartile (Q1)"
    elif pct == 50:
        interp = "Median (Q2)"
    elif pct == 75:
        interp = "3rd Quartile (Q3)"
    elif pct == 100:
        interp = "Maximum score"
    else:
        interp = ""
    
    print(f"{pct}th{'':<12} {score:<10.1f} {interp}")

# ============================================================================
# PART 3: Score to Percentile Mapping
# ============================================================================
print("\n" + "=" * 80)
print("PART 3: Score to Percentile Mapping")
print("=" * 80)

print("\nEach Score's Percentile Range:")
print("-" * 80)
print(f"{'Score':<10} {'Students':<12} {'Percentile Range':<25} {'Category'}")
print("-" * 80)

cumulative = 0
for score in range(21):
    count = score_dist.get(score, 0)
    if count > 0:
        start_pct = (cumulative / total_students * 100)
        cumulative += count
        end_pct = (cumulative / total_students * 100)
        
        # Categorize
        if end_pct <= 30:
            category = "below2 range"
        elif end_pct <= 55:
            category = "below1 range"
        elif end_pct <= 75:
            category = "on range"
        elif end_pct <= 85:
            category = "above1 range"
        else:
            category = "above2 range"
        
        print(f"{score:<10} {count:<12} {start_pct:>5.1f}% - {end_pct:>5.1f}%{'':<10} {category}")

# ============================================================================
# PART 4: Statistical Summary
# ============================================================================
print("\n" + "=" * 80)
print("PART 4: Statistical Summary")
print("=" * 80)

stats = df_students['전체 정답 수'].describe()
mode_score = df_students['전체 정답 수'].mode()[0]
mode_count = score_dist[mode_score]

print(f"\nMean (평균):        {stats['mean']:.2f}")
print(f"Median (중앙값):    {stats['50%']:.1f}")
print(f"Mode (최빈값):      {mode_score} (학생 {mode_count}명)")
print(f"Std Dev (표준편차): {stats['std']:.2f}")
print(f"Min (최소):         {int(stats['min'])}")
print(f"Max (최대):         {int(stats['max'])}")
print(f"Range (범위):       {int(stats['max'] - stats['min'])}")
print(f"\nQ1 (25%):           {stats['25%']:.1f}")
print(f"Q2 (50%):           {stats['50%']:.1f}")
print(f"Q3 (75%):           {stats['75%']:.1f}")
print(f"IQR (Q3-Q1):        {stats['75%'] - stats['25%']:.1f}")

# ============================================================================
# VISUALIZATIONS
# ============================================================================
print("\n" + "=" * 80)
print("Creating Visualizations")
print("=" * 80)

# Visualization 1: Histogram with percentile lines
fig, ax = plt.subplots(figsize=(14, 7))

# Create histogram
counts = [score_dist.get(i, 0) for i in range(21)]
bars = ax.bar(range(21), counts, color='steelblue', alpha=0.7, edgecolor='black')

# Add percentile lines
key_percentiles = {
    30: ('below2/below1 경계', 'red'),
    55: ('below1/on 경계', 'orange'),
    75: ('on/above1 경계', 'green'),
    85: ('above1/above2 경계', 'blue')
}

for pct, (label, color) in key_percentiles.items():
    score = np.percentile(df_students['전체 정답 수'], pct)
    ax.axvline(x=score, color=color, linestyle='--', linewidth=2, alpha=0.7, label=f'{pct}th: {label}')

ax.set_xlabel('점수', fontsize=12)
ax.set_ylabel('학생 수', fontsize=12)
ax.set_title('GT1 점수 분포 및 백분위 경계선', fontsize=14, fontweight='bold')
ax.set_xticks(range(0, 21, 1))
ax.grid(axis='y', alpha=0.3)
ax.legend(loc='upper right', fontsize=10)

# Add value labels on bars
for i, (bar, count) in enumerate(zip(bars, counts)):
    if count > 0:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(count)}',
                ha='center', va='bottom', fontsize=8)

plt.tight_layout()
viz1_path = os.path.join(output_dir, 'gt1_score_distribution.png')
plt.savefig(viz1_path, dpi=150, bbox_inches='tight')
print(f"\n[OK] Saved: {viz1_path}")
plt.close()

# Visualization 2: Cumulative Distribution
fig, ax = plt.subplots(figsize=(14, 7))

scores = sorted(score_dist.index)
cumulative_pcts = []
cumulative = 0

for score in range(21):
    cumulative += score_dist.get(score, 0)
    cumulative_pcts.append(cumulative / total_students * 100)

ax.plot(range(21), cumulative_pcts, marker='o', linewidth=2, markersize=6, color='steelblue')
ax.fill_between(range(21), cumulative_pcts, alpha=0.3, color='steelblue')

# Add horizontal lines for key percentiles
for pct in [30, 55, 75, 85]:
    ax.axhline(y=pct, color='red', linestyle='--', alpha=0.5, linewidth=1)
    ax.text(20.5, pct, f'{pct}%', va='center', fontsize=9, color='red')

ax.set_xlabel('점수', fontsize=12)
ax.set_ylabel('누적 백분위 (%)', fontsize=12)
ax.set_title('GT1 누적 점수 분포 (백분위)', fontsize=14, fontweight='bold')
ax.set_xticks(range(0, 21, 1))
ax.set_ylim(0, 100)
ax.grid(True, alpha=0.3)

plt.tight_layout()
viz2_path = os.path.join(output_dir, 'gt1_cumulative_distribution.png')
plt.savefig(viz2_path, dpi=150, bbox_inches='tight')
print(f"[OK] Saved: {viz2_path}")
plt.close()

# Visualization 3: Box Plot with percentiles
fig, ax = plt.subplots(figsize=(12, 6))

bp = ax.boxplot([df_students['전체 정답 수']], vert=False, widths=0.5,
                 patch_artist=True, showmeans=True,
                 boxprops=dict(facecolor='lightblue', alpha=0.7),
                 medianprops=dict(color='red', linewidth=2),
                 meanprops=dict(marker='D', markerfacecolor='green', markersize=10))

# Add percentile annotations
percentile_values = {
    'Min': stats['min'],
    'Q1 (25%)': stats['25%'],
    'Median (50%)': stats['50%'],
    'Mean': stats['mean'],
    'Q3 (75%)': stats['75%'],
    'Max': stats['max']
}

y_pos = 1.15
for label, value in percentile_values.items():
    ax.text(value, y_pos, f'{label}\n{value:.1f}', 
            ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax.axvline(x=value, color='gray', linestyle=':', alpha=0.5)

ax.set_xlabel('점수', fontsize=12)
ax.set_title('GT1 점수 분포 Box Plot', fontsize=14, fontweight='bold')
ax.set_yticks([])
ax.set_xlim(-1, 21)
ax.grid(axis='x', alpha=0.3)

plt.tight_layout()
viz3_path = os.path.join(output_dir, 'gt1_boxplot.png')
plt.savefig(viz3_path, dpi=150, bbox_inches='tight')
print(f"[OK] Saved: {viz3_path}")
plt.close()

# ============================================================================
# SAVE REPORT
# ============================================================================
print("\n" + "=" * 80)
print("Saving Report")
print("=" * 80)

report_path = os.path.join(output_dir, 'gt1_percentile_report.txt')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("GT1 Score Distribution and Percentile Analysis\n")
    f.write("=" * 80 + "\n\n")
    
    f.write(f"Total Students: {total_students:,}\n\n")
    
    f.write("Statistical Summary:\n")
    f.write("-" * 80 + "\n")
    f.write(f"Mean:           {stats['mean']:.2f}\n")
    f.write(f"Median:         {stats['50%']:.1f}\n")
    f.write(f"Mode:           {mode_score} ({mode_count} students)\n")
    f.write(f"Std Dev:        {stats['std']:.2f}\n")
    f.write(f"Min:            {int(stats['min'])}\n")
    f.write(f"Max:            {int(stats['max'])}\n")
    f.write(f"Range:          {int(stats['max'] - stats['min'])}\n\n")
    
    f.write("Quartiles:\n")
    f.write("-" * 80 + "\n")
    f.write(f"Q1 (25%):       {stats['25%']:.1f}\n")
    f.write(f"Q2 (50%):       {stats['50%']:.1f}\n")
    f.write(f"Q3 (75%):       {stats['75%']:.1f}\n")
    f.write(f"IQR:            {stats['75%'] - stats['25%']:.1f}\n\n")
    
    f.write("Key Percentiles:\n")
    f.write("-" * 80 + "\n")
    for pct, score in zip(percentiles, percentile_scores):
        f.write(f"{pct:3d}th percentile: {score:5.1f}\n")
    
    f.write("\n\nScore Distribution:\n")
    f.write("-" * 80 + "\n")
    f.write(f"{'Score':<10} {'Count':<10} {'Percentage':<15} {'Cumulative %':<15}\n")
    f.write("-" * 80 + "\n")
    
    cumulative_count = 0
    for score in range(21):
        count = score_dist.get(score, 0)
        if count > 0:
            percentage = (count / total_students * 100)
            cumulative_count += count
            cumulative_pct = (cumulative_count / total_students * 100)
            f.write(f"{score:<10} {count:<10} {percentage:>6.2f}%{'':<8} {cumulative_pct:>6.2f}%\n")

print(f"[OK] Saved: {report_path}")

print("\n" + "=" * 80)
print("Analysis Complete!")
print("=" * 80)
print(f"\nKey Findings:")
print(f"  - Mean score: {stats['mean']:.2f}")
print(f"  - Median score: {stats['50%']:.1f}")
print(f"  - Most common score: {mode_score} ({mode_count} students)")
print(f"  - 30th percentile (below2/below1): {np.percentile(df_students['전체 정답 수'], 30):.1f}")
print(f"  - 55th percentile (below1/on): {np.percentile(df_students['전체 정답 수'], 55):.1f}")
print(f"  - 75th percentile (on/above1): {np.percentile(df_students['전체 정답 수'], 75):.1f}")
print("\n" + "=" * 80)
