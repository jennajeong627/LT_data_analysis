import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# Set Korean font
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

print("=" * 80)
print("GT1 A안 vs B안 vs C안 비교 - 정규분포 시각화")
print("=" * 80)

# Load data
print("\n[1] Loading data...")
df = pd.read_csv('data/2024_5월_문항난이도별결과.csv', encoding='utf-8-sig')

# Get GT1 students
df_students = df.groupby(['레벨', '학생명'])['정답 수'].sum().reset_index()
df_students.columns = ['레벨', '학생명', '전체 정답 수']
df_gt1 = df_students[df_students['레벨'] == 'GT1'].copy()

total_students = len(df_gt1)
scores = df_gt1['전체 정답 수'].values

print(f"   Total GT1 students: {total_students:,}")
print(f"   Mean: {scores.mean():.2f}")
print(f"   Std Dev: {scores.std():.2f}")

# Calculate percentile
df_gt1['백분위'] = df_gt1['전체 정답 수'].rank(pct=True) * 100

# A안 절대평가 기준
criteria_a = {
    'below2': (0, 6),
    'below1': (7, 11),
    'on': (12, 15),
    'above1': (16, 17),
    'above2': (18, 20)
}

# B안 상대평가 기준 (백분위)
criteria_b_percentile = {
    'below2': (0, 20),
    'below1': (21, 40),
    'on': (41, 70),
    'above1': (71, 90),
    'above2': (91, 100)
}

# C안 절대+상대 결합 기준
criteria_c = {
    'below2': {'score': (0, 6), 'percentile': (0, 30)},
    'below1': {'score': (7, 11), 'percentile': (30, 55)},
    'on': {'score': (12, 15), 'percentile': (55, 75)},
    'above1': {'score': (16, 17), 'percentile': (75, 85)},
    'above2': {'score': (18, 20), 'percentile': (85, 100)}
}

# Classify by A안
def classify_a(score):
    for segment, (min_s, max_s) in criteria_a.items():
        if min_s <= score <= max_s:
            return segment
    return 'unknown'

# Classify by B안
def classify_b(percentile):
    for segment, (min_p, max_p) in criteria_b_percentile.items():
        if segment == 'above2':
            if min_p <= percentile <= max_p:
                return segment
        else:
            if min_p <= percentile < max_p:
                return segment
    return 'unknown'

# Classify by C안
def classify_c(row):
    score = row['전체 정답 수']
    percentile = row['백분위']
    
    for segment, criteria in criteria_c.items():
        score_min, score_max = criteria['score']
        perc_min, perc_max = criteria['percentile']
        
        score_match = score_min <= score <= score_max
        if segment == 'above2':
            perc_match = perc_min <= percentile <= perc_max
        else:
            perc_match = perc_min <= percentile < perc_max
        
        if score_match and perc_match:
            return segment
    
    return 'unclassified'

df_gt1['A안'] = df_gt1['전체 정답 수'].apply(classify_a)
df_gt1['B안'] = df_gt1['백분위'].apply(classify_b)
df_gt1['C안'] = df_gt1.apply(classify_c, axis=1)

# ============================================================================
# VISUALIZATION: 3-Panel Comparison
# ============================================================================
print("\n[2] Creating visualization...")

fig, axes = plt.subplots(3, 1, figsize=(16, 20))

segment_colors = {
    'below2': '#e53e3e',
    'below1': '#ed8936',
    'on': '#48bb78',
    'above1': '#38a169',
    'above2': '#2f855a',
    'unclassified': '#718096',
    'unknown': '#cccccc'
}

# Normal distribution parameters
mu, sigma = scores.mean(), scores.std()
x = np.linspace(0, 20, 1000)
normal_curve = stats.norm.pdf(x, mu, sigma)

# Panel 1: A안 (절대평가)
ax1 = axes[0]
n1, bins1, patches1 = ax1.hist(scores, bins=range(0, 22), density=True, 
                                alpha=0.6, edgecolor='black', linewidth=1.2)

# Color by A안 segments
for patch, left_edge in zip(patches1, bins1[:-1]):
    score = int(left_edge)
    segment = classify_a(score)
    patch.set_facecolor(segment_colors[segment])
    patch.set_alpha(0.7)

# Plot normal curve
ax1.plot(x, normal_curve, 'r-', linewidth=3, label=f'정규분포 (μ={mu:.2f}, σ={sigma:.2f})')

# Add segment boundaries
boundaries = [6.5, 11.5, 15.5, 17.5]
for boundary in boundaries:
    ax1.axvline(x=boundary, color='black', linestyle='--', linewidth=2, alpha=0.5)

# Add mean line
ax1.axvline(x=mu, color='darkred', linestyle='-', linewidth=2.5, alpha=0.8)

ax1.set_xlabel('점수 (정답 수)', fontsize=12, fontweight='bold')
ax1.set_ylabel('확률 밀도', fontsize=12, fontweight='bold')
ax1.set_title('A안 - 절대평가 기준 (점수 기준)', fontsize=14, fontweight='bold', pad=15)
ax1.set_xlim(-0.5, 20.5)
ax1.set_xticks(range(0, 21, 1))
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.legend(loc='upper right', fontsize=10)

# Add segment labels
y_bottom = ax1.get_ylim()[0]
segment_positions = {'below2': 3, 'below1': 9, 'on': 13.5, 'above1': 16.5, 'above2': 19}
for segment, x_pos in segment_positions.items():
    min_s, max_s = criteria_a[segment]
    ax1.text(x_pos, y_bottom - 0.005, f'{segment}\n({min_s}-{max_s}개)',
            ha='center', va='top', fontsize=9, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=segment_colors[segment], 
                     alpha=0.7, edgecolor='black'))

# Panel 2: B안 (상대평가)
ax2 = axes[1]
n2, bins2, patches2 = ax2.hist(scores, bins=range(0, 22), density=True, 
                                alpha=0.6, edgecolor='black', linewidth=1.2)

# Color by B안 segments (based on percentile)
for patch, left_edge in zip(patches2, bins2[:-1]):
    score = int(left_edge)
    # Find percentile for this score
    percentile = df_gt1[df_gt1['전체 정답 수'] == score]['백분위'].mean()
    segment = classify_b(percentile)
    patch.set_facecolor(segment_colors[segment])
    patch.set_alpha(0.7)

# Plot normal curve
ax2.plot(x, normal_curve, 'r-', linewidth=3, label=f'정규분포 (μ={mu:.2f}, σ={sigma:.2f})')

# Add percentile boundaries (as score values)
percentile_boundaries = [20, 40, 70, 90]
for p in percentile_boundaries:
    score_at_p = np.percentile(scores, p)
    ax2.axvline(x=score_at_p, color='blue', linestyle='--', linewidth=2, alpha=0.5)
    ax2.text(score_at_p, ax2.get_ylim()[1]*0.95, f'{p}%ile',
            rotation=90, va='top', ha='right', fontsize=9, color='blue', fontweight='bold')

# Add mean line
ax2.axvline(x=mu, color='darkred', linestyle='-', linewidth=2.5, alpha=0.8)

ax2.set_xlabel('점수 (정답 수)', fontsize=12, fontweight='bold')
ax2.set_ylabel('확률 밀도', fontsize=12, fontweight='bold')
ax2.set_title('B안 - 상대평가 기준 (백분위 기준)', fontsize=14, fontweight='bold', pad=15)
ax2.set_xlim(-0.5, 20.5)
ax2.set_xticks(range(0, 21, 1))
ax2.grid(True, alpha=0.3, linestyle='--')
ax2.legend(loc='upper right', fontsize=10)

# Add percentile range labels
y_bottom = ax2.get_ylim()[0]
percentile_labels = {
    'below2': (0, 20, np.percentile(scores, 10)),
    'below1': (21, 40, np.percentile(scores, 30)),
    'on': (41, 70, np.percentile(scores, 55)),
    'above1': (71, 90, np.percentile(scores, 80)),
    'above2': (91, 100, np.percentile(scores, 95))
}
for segment, (min_p, max_p, x_pos) in percentile_labels.items():
    ax2.text(x_pos, y_bottom - 0.005, f'{segment}\n({min_p}-{max_p}%ile)',
            ha='center', va='top', fontsize=9, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=segment_colors[segment], 
                     alpha=0.7, edgecolor='black'))

# Panel 3: C안 (절대+상대 결합)
ax3 = axes[2]
n3, bins3, patches3 = ax3.hist(scores, bins=range(0, 22), density=True, 
                                alpha=0.6, edgecolor='black', linewidth=1.2)

# Color by C안 segments
for patch, left_edge in zip(patches3, bins3[:-1]):
    score = int(left_edge)
    # Find students with this score
    students_at_score = df_gt1[df_gt1['전체 정답 수'] == score]
    if len(students_at_score) > 0:
        # Use the most common classification for this score
        segment = students_at_score['C안'].mode()[0]
    else:
        segment = 'unclassified'
    patch.set_facecolor(segment_colors[segment])
    patch.set_alpha(0.7)

# Plot normal curve
ax3.plot(x, normal_curve, 'r-', linewidth=3, label=f'정규분포 (μ={mu:.2f}, σ={sigma:.2f})')

# Add both score and percentile boundaries
# Score boundaries (solid lines)
for boundary in [6.5, 11.5, 15.5, 17.5]:
    ax3.axvline(x=boundary, color='black', linestyle='-', linewidth=1.5, alpha=0.5)

# Percentile boundaries (dashed lines)
for p in [30, 55, 75, 85]:
    score_at_p = np.percentile(scores, p)
    ax3.axvline(x=score_at_p, color='blue', linestyle=':', linewidth=1.5, alpha=0.5)

# Add mean line
ax3.axvline(x=mu, color='darkred', linestyle='-', linewidth=2.5, alpha=0.8)

ax3.set_xlabel('점수 (정답 수)', fontsize=12, fontweight='bold')
ax3.set_ylabel('확률 밀도', fontsize=12, fontweight='bold')
ax3.set_title('C안 - 절대+상대 결합 기준 (점수 AND 백분위)', fontsize=14, fontweight='bold', pad=15)
ax3.set_xlim(-0.5, 20.5)
ax3.set_xticks(range(0, 21, 1))
ax3.grid(True, alpha=0.3, linestyle='--')
ax3.legend(loc='upper right', fontsize=10)

# Add segment labels
y_bottom = ax3.get_ylim()[0]
for segment, x_pos in segment_positions.items():
    if segment in criteria_c:
        min_s, max_s = criteria_c[segment]['score']
        min_p, max_p = criteria_c[segment]['percentile']
        ax3.text(x_pos, y_bottom - 0.005, f'{segment}\n({min_s}-{max_s}개 AND\n{min_p}-{max_p}%ile)',
                ha='center', va='top', fontsize=8, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.4', facecolor=segment_colors[segment], 
                         alpha=0.7, edgecolor='black'))

plt.tight_layout()
output_path = r'c:\Users\user\projects\LT_data_analysis\gt1_abc_comparison_normal_distribution.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight')
print(f"\n[OK] Saved: {output_path}")
plt.close()

# ============================================================================
# Summary Statistics
# ============================================================================
print("\n" + "=" * 80)
print("Distribution Summary")
print("=" * 80)

segment_order = ['below2', 'below1', 'on', 'above1', 'above2']

print("\nA안 (절대평가):")
a_dist = df_gt1['A안'].value_counts().reindex(segment_order, fill_value=0)
for segment in segment_order:
    count = a_dist[segment]
    pct = count / total_students * 100
    print(f"  {segment}: {count:,}명 ({pct:.2f}%)")

print("\nB안 (상대평가):")
b_dist = df_gt1['B안'].value_counts().reindex(segment_order, fill_value=0)
for segment in segment_order:
    count = b_dist[segment]
    pct = count / total_students * 100
    print(f"  {segment}: {count:,}명 ({pct:.2f}%)")

print("\nC안 (절대+상대):")
c_dist = df_gt1['C안'].value_counts()
for segment in segment_order + ['unclassified']:
    count = c_dist.get(segment, 0)
    pct = count / total_students * 100
    print(f"  {segment}: {count:,}명 ({pct:.2f}%)")

print("\n" + "=" * 80)
print("Analysis Complete!")
print("=" * 80)
print(f"\nSaved to: {output_path}")
print("\n" + "=" * 80)
