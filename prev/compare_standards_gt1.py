import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Set Korean font for matplotlib
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# Create output directory
output_dir = r'C:\Users\user\.gemini\antigravity\brain\8fd772ef-33d9-4495-9894-ecaf33833f42'
os.makedirs(output_dir, exist_ok=True)

print("=" * 80)
print("GT1 Student Distribution Comparison - Standard A vs Standard B")
print("=" * 80)

# Load data
print("\n[1] Loading data...")
df = pd.read_csv('data/2024_5월_문항난이도별결과.csv', encoding='utf-8-sig')
df_gt1 = df[df['레벨'] == 'GT1'].copy()

# Get unique students
df_students = df_gt1.groupby(['학생명', '전체 정답 수']).first().reset_index()
total_students = len(df_students)

print(f"   GT1 students: {total_students:,}")

# Define two standards
standard_a = {
    'below2': (0, 6),
    'below1': (7, 11),
    'on': (12, 15),
    'above1': (16, 17),
    'above2': (18, 20)
}

standard_b = {
    'below2': (0, 9),
    'below1': (10, 11),
    'on': (12, 15),
    'above1': (16, 17),
    'above2': (18, 20)
}

# Classify students by both standards
def classify_segment(score, criteria):
    for segment, (min_score, max_score) in criteria.items():
        if min_score <= score <= max_score:
            return segment
    return 'unknown'

df_students['Standard_A'] = df_students['전체 정답 수'].apply(lambda x: classify_segment(x, standard_a))
df_students['Standard_B'] = df_students['전체 정답 수'].apply(lambda x: classify_segment(x, standard_b))

# ============================================================================
# PART 1: Standard A Distribution
# ============================================================================
print("\n" + "=" * 80)
print("PART 1: Standard A Distribution")
print("=" * 80)

segment_order = ['below2', 'below1', 'on', 'above1', 'above2']

dist_a = df_students['Standard_A'].value_counts().reindex(segment_order, fill_value=0)
dist_a_pct = (dist_a / total_students * 100).round(2)

print("\nStandard A Criteria (20 questions):")
for segment, (min_s, max_s) in standard_a.items():
    count = dist_a[segment]
    pct = dist_a_pct[segment]
    print(f"  {segment:10s} ({min_s:2d}~{max_s:2d}점): {count:5,}명 ({pct:6.2f}%)")

# ============================================================================
# PART 2: Standard B Distribution
# ============================================================================
print("\n" + "=" * 80)
print("PART 2: Standard B Distribution")
print("=" * 80)

dist_b = df_students['Standard_B'].value_counts().reindex(segment_order, fill_value=0)
dist_b_pct = (dist_b / total_students * 100).round(2)

print("\nStandard B Criteria (20 questions):")
for segment, (min_s, max_s) in standard_b.items():
    count = dist_b[segment]
    pct = dist_b_pct[segment]
    print(f"  {segment:10s} ({min_s:2d}~{max_s:2d}점): {count:5,}명 ({pct:6.2f}%)")

# ============================================================================
# PART 3: Comparison Analysis
# ============================================================================
print("\n" + "=" * 80)
print("PART 3: Comparison Analysis")
print("=" * 80)

# Create comparison table
comparison_df = pd.DataFrame({
    'Standard_A_Count': dist_a,
    'Standard_A_Pct': dist_a_pct,
    'Standard_B_Count': dist_b,
    'Standard_B_Pct': dist_b_pct,
    'Difference': dist_b - dist_a,
    'Diff_Pct': dist_b_pct - dist_a_pct
})

print("\nComparison Table:")
print("-" * 80)
print(comparison_df.to_string())

# Key differences
print("\n\nKey Differences:")
print("-" * 80)
for segment in segment_order:
    diff = comparison_df.loc[segment, 'Difference']
    diff_pct = comparison_df.loc[segment, 'Diff_Pct']
    if diff != 0:
        direction = "increased" if diff > 0 else "decreased"
        print(f"  {segment}: {direction} by {abs(int(diff))} students ({diff_pct:+.2f}%)")

# ============================================================================
# VISUALIZATIONS
# ============================================================================
print("\n" + "=" * 80)
print("Creating Visualizations")
print("=" * 80)

# Visualization 1: Side-by-side comparison
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

colors = ['#e53e3e', '#ed8936', '#48bb78', '#38a169', '#2f855a']

# Standard A
ax1 = axes[0]
bars1 = ax1.bar(segment_order, dist_a.values, color=colors, alpha=0.8)
ax1.set_xlabel('구간', fontsize=12)
ax1.set_ylabel('학생 수', fontsize=12)
ax1.set_title('Standard A - GT1 학생 분포', fontsize=14, fontweight='bold')
ax1.grid(axis='y', alpha=0.3)

for i, (bar, segment) in enumerate(zip(bars1, segment_order)):
    height = bar.get_height()
    pct = dist_a_pct[segment]
    score_range = f"{standard_a[segment][0]}-{standard_a[segment][1]}"
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height):,}\n({pct:.1f}%)',
            ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax1.text(i, -max(dist_a.values)*0.08, score_range,
            ha='center', va='top', fontsize=9, color='gray')

# Standard B
ax2 = axes[1]
bars2 = ax2.bar(segment_order, dist_b.values, color=colors, alpha=0.8)
ax2.set_xlabel('구간', fontsize=12)
ax2.set_ylabel('학생 수', fontsize=12)
ax2.set_title('Standard B - GT1 학생 분포', fontsize=14, fontweight='bold')
ax2.grid(axis='y', alpha=0.3)

for i, (bar, segment) in enumerate(zip(bars2, segment_order)):
    height = bar.get_height()
    pct = dist_b_pct[segment]
    score_range = f"{standard_b[segment][0]}-{standard_b[segment][1]}"
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height):,}\n({pct:.1f}%)',
            ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax2.text(i, -max(dist_b.values)*0.08, score_range,
            ha='center', va='top', fontsize=9, color='gray')

plt.tight_layout()
viz1_path = os.path.join(output_dir, 'gt1_standard_comparison.png')
plt.savefig(viz1_path, dpi=150, bbox_inches='tight')
print(f"\n[OK] Saved: {viz1_path}")
plt.close()

# Visualization 2: Stacked percentage comparison
fig, ax = plt.subplots(figsize=(12, 7))

x = np.arange(2)
width = 0.5

# Create stacked bars
bottom_a = np.zeros(1)
bottom_b = np.zeros(1)

for idx, segment in enumerate(segment_order):
    # Standard A
    ax.bar(0, dist_a_pct[segment], width, bottom=bottom_a, 
           label=segment if idx == 0 else "", color=colors[idx], alpha=0.9)
    # Add label
    if dist_a_pct[segment] > 3:
        ax.text(0, bottom_a + dist_a_pct[segment]/2, 
               f'{segment}\n{dist_a_pct[segment]:.1f}%',
               ha='center', va='center', fontsize=10, fontweight='bold', color='white')
    bottom_a += dist_a_pct[segment]
    
    # Standard B
    ax.bar(1, dist_b_pct[segment], width, bottom=bottom_b,
           color=colors[idx], alpha=0.9)
    # Add label
    if dist_b_pct[segment] > 3:
        ax.text(1, bottom_b + dist_b_pct[segment]/2,
               f'{segment}\n{dist_b_pct[segment]:.1f}%',
               ha='center', va='center', fontsize=10, fontweight='bold', color='white')
    bottom_b += dist_b_pct[segment]

ax.set_ylabel('비율 (%)', fontsize=12)
ax.set_title('GT1 학생 구간 분포 비교 - Standard A vs Standard B', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(['Standard A', 'Standard B'], fontsize=12, fontweight='bold')
ax.set_ylim(0, 100)
ax.grid(axis='y', alpha=0.3)

# Add legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=colors[i], label=segment, alpha=0.9) 
                   for i, segment in enumerate(segment_order)]
ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))

plt.tight_layout()
viz2_path = os.path.join(output_dir, 'gt1_standard_stacked_comparison.png')
plt.savefig(viz2_path, dpi=150, bbox_inches='tight')
print(f"[OK] Saved: {viz2_path}")
plt.close()

# Visualization 3: Difference chart
fig, ax = plt.subplots(figsize=(10, 6))

differences = comparison_df['Difference'].values
colors_diff = ['#2ca02c' if d > 0 else '#d62728' if d < 0 else '#718096' for d in differences]

bars = ax.bar(segment_order, differences, color=colors_diff, alpha=0.8)
ax.set_xlabel('구간', fontsize=12)
ax.set_ylabel('학생 수 차이 (Standard B - Standard A)', fontsize=12)
ax.set_title('Standard B와 Standard A의 학생 수 차이', fontsize=14, fontweight='bold')
ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
ax.grid(axis='y', alpha=0.3)

for bar, diff, diff_pct in zip(bars, differences, comparison_df['Diff_Pct'].values):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(diff):+,}\n({diff_pct:+.1f}%)',
            ha='center', va='bottom' if height > 0 else 'top', 
            fontsize=10, fontweight='bold')

plt.tight_layout()
viz3_path = os.path.join(output_dir, 'gt1_standard_difference.png')
plt.savefig(viz3_path, dpi=150, bbox_inches='tight')
print(f"[OK] Saved: {viz3_path}")
plt.close()

# ============================================================================
# SAVE REPORT
# ============================================================================
print("\n" + "=" * 80)
print("Saving Report")
print("=" * 80)

report_path = os.path.join(output_dir, 'gt1_standard_comparison_report.txt')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("GT1 Student Distribution Comparison\n")
    f.write("Standard A vs Standard B\n")
    f.write("=" * 80 + "\n\n")
    
    f.write(f"Total GT1 Students: {total_students:,}\n\n")
    
    f.write("Standard A Criteria:\n")
    f.write("-" * 80 + "\n")
    for segment, (min_s, max_s) in standard_a.items():
        count = dist_a[segment]
        pct = dist_a_pct[segment]
        f.write(f"  {segment:10s} ({min_s:2d}~{max_s:2d}점): {count:5,}명 ({pct:6.2f}%)\n")
    
    f.write("\n\nStandard B Criteria:\n")
    f.write("-" * 80 + "\n")
    for segment, (min_s, max_s) in standard_b.items():
        count = dist_b[segment]
        pct = dist_b_pct[segment]
        f.write(f"  {segment:10s} ({min_s:2d}~{max_s:2d}점): {count:5,}명 ({pct:6.2f}%)\n")
    
    f.write("\n\nComparison Table:\n")
    f.write("-" * 80 + "\n")
    f.write(comparison_df.to_string())
    
    f.write("\n\n\nKey Insights:\n")
    f.write("-" * 80 + "\n")
    
    # Calculate key metrics
    std_a_below = dist_a['below2'] + dist_a['below1']
    std_b_below = dist_b['below2'] + dist_b['below1']
    std_a_on_above = dist_a['on'] + dist_a['above1'] + dist_a['above2']
    std_b_on_above = dist_b['on'] + dist_b['above1'] + dist_b['above2']
    
    f.write(f"\nStandard A:\n")
    f.write(f"  - Below 'on': {std_a_below:,} ({std_a_below/total_students*100:.2f}%)\n")
    f.write(f"  - 'on' or above: {std_a_on_above:,} ({std_a_on_above/total_students*100:.2f}%)\n")
    
    f.write(f"\nStandard B:\n")
    f.write(f"  - Below 'on': {std_b_below:,} ({std_b_below/total_students*100:.2f}%)\n")
    f.write(f"  - 'on' or above: {std_b_on_above:,} ({std_b_on_above/total_students*100:.2f}%)\n")
    
    f.write(f"\nDifference:\n")
    f.write(f"  - Standard B has {abs(std_b_on_above - std_a_on_above):,} ")
    f.write(f"{'more' if std_b_on_above > std_a_on_above else 'fewer'} students meeting 'on' standard\n")

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
