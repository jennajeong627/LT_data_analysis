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
print("GT1 Distribution Analysis - C안 절대+상대 결합 기준")
print("=" * 80)

# Load data
print("\n[1] Loading data...")
df = pd.read_csv('data/2024_5월_문항난이도별결과.csv', encoding='utf-8-sig')

# Get GT1 students
df_students = df.groupby(['레벨', '학생명'])['정답 수'].sum().reset_index()
df_students.columns = ['레벨', '학생명', '전체 정답 수']
df_gt1 = df_students[df_students['레벨'] == 'GT1'].copy()

total_students = len(df_gt1)
print(f"   Total GT1 students: {total_students:,}")

# Calculate percentile
df_gt1['백분위'] = df_gt1['전체 정답 수'].rank(pct=True) * 100

# C안 절대+상대 결합 기준점
# 점수 기준 (A안) AND 백분위 기준 (실제 분포)
criteria_c = {
    'below2': {
        'score': (0, 6),
        'percentile': (0, 30),
        'desc': '점수 ≤ 6 AND 백분위 ≤ 30%'
    },
    'below1': {
        'score': (7, 11),
        'percentile': (30, 55),
        'desc': '7 ≤ 점수 ≤ 11 AND 30% ≤ 백분위 < 55%'
    },
    'on': {
        'score': (12, 15),
        'percentile': (55, 75),
        'desc': '12 ≤ 점수 ≤ 15 AND 55% ≤ 백분위 < 75%'
    },
    'above1': {
        'score': (16, 17),
        'percentile': (75, 85),
        'desc': '16 ≤ 점수 ≤ 17 AND 75% ≤ 백분위 < 85%'
    },
    'above2': {
        'score': (18, 20),
        'percentile': (85, 100),
        'desc': '점수 ≥ 18 AND 백분위 ≥ 85%'
    }
}

# Classify by C안 (both conditions must be met)
def classify_by_criteria_c(row):
    score = row['전체 정답 수']
    percentile = row['백분위']
    
    for segment, criteria in criteria_c.items():
        score_min, score_max = criteria['score']
        perc_min, perc_max = criteria['percentile']
        
        # Check both conditions
        score_match = score_min <= score <= score_max
        
        if segment == 'above2':
            perc_match = perc_min <= percentile <= perc_max
        else:
            perc_match = perc_min <= percentile < perc_max
        
        if score_match and perc_match:
            return segment
    
    return 'unclassified'  # Doesn't meet both conditions

df_gt1['구간'] = df_gt1.apply(classify_by_criteria_c, axis=1)

# ============================================================================
# PART 1: Distribution Analysis
# ============================================================================
print("\n" + "=" * 80)
print("PART 1: C안 절대+상대 결합 기준 - GT1 학생 분포")
print("=" * 80)

segment_order = ['below2', 'below1', 'on', 'above1', 'above2', 'unclassified']
distribution = df_gt1['구간'].value_counts().reindex(segment_order, fill_value=0)
distribution_pct = (distribution / total_students * 100).round(2)

print("\nC안 절대+상대 결합 기준점:")
print("-" * 80)
for segment in segment_order:
    if segment == 'unclassified':
        count = distribution[segment]
        pct = distribution_pct[segment]
        print(f"\n{segment:15s}")
        print(f"  해석: 두 조건을 모두 충족하지 못함")
        print(f"  학생 수: {count:,}명 ({pct:.2f}%)")
    else:
        criteria = criteria_c[segment]
        score_min, score_max = criteria['score']
        perc_min, perc_max = criteria['percentile']
        desc = criteria['desc']
        count = distribution[segment]
        pct = distribution_pct[segment]
        
        print(f"\n{segment:15s}")
        print(f"  조건: {desc}")
        print(f"  점수 범위: {score_min}~{score_max}개")
        print(f"  백분위 범위: {perc_min}~{perc_max}%")
        print(f"  학생 수: {count:,}명 ({pct:.2f}%)")

# Summary statistics
print("\n" + "=" * 80)
print("요약 통계")
print("=" * 80)

classified = total_students - distribution['unclassified']
below_on = distribution['below2'] + distribution['below1']
on_above = distribution['on'] + distribution['above1'] + distribution['above2']

print(f"\n분류 성공: {classified:,}명 ({classified/total_students*100:.2f}%)")
print(f"분류 실패 (unclassified): {distribution['unclassified']:,}명 ({distribution_pct['unclassified']:.2f}%)")
print(f"\n기준 미달 (below2 + below1): {below_on:,}명 ({below_on/total_students*100:.2f}%)")
print(f"기준 충족 이상 (on + above): {on_above:,}명 ({on_above/total_students*100:.2f}%)")

# Analyze unclassified students
if distribution['unclassified'] > 0:
    print("\n" + "=" * 80)
    print("미분류 학생 분석")
    print("=" * 80)
    
    unclassified_students = df_gt1[df_gt1['구간'] == 'unclassified']
    print(f"\n미분류 학생 점수 범위: {unclassified_students['전체 정답 수'].min():.0f}~{unclassified_students['전체 정답 수'].max():.0f}개")
    print(f"미분류 학생 백분위 범위: {unclassified_students['백분위'].min():.1f}~{unclassified_students['백분위'].max():.1f}%")

# ============================================================================
# VISUALIZATIONS
# ============================================================================
print("\n" + "=" * 80)
print("Creating Visualizations")
print("=" * 80)

# Visualization 1: Bar chart
fig, ax = plt.subplots(figsize=(12, 7))

colors = ['#e53e3e', '#ed8936', '#48bb78', '#38a169', '#2f855a', '#718096']
display_segments = segment_order
bars = ax.bar(display_segments, distribution.values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

ax.set_xlabel('구간', fontsize=13, fontweight='bold')
ax.set_ylabel('학생 수', fontsize=13, fontweight='bold')
ax.set_title('GT1 학생 분포 - C안 절대+상대 결합 기준', fontsize=15, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3, linestyle='--')

# Add value labels
for i, (bar, segment) in enumerate(zip(bars, display_segments)):
    height = bar.get_height()
    pct = distribution_pct[segment]
    
    # Count and percentage on top
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height):,}명\n({pct:.1f}%)',
            ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Criteria below
    if segment != 'unclassified':
        criteria = criteria_c[segment]
        score_min, score_max = criteria['score']
        perc_min, perc_max = criteria['percentile']
        ax.text(i, -max(distribution.values)*0.08, 
                f'{score_min}-{score_max}개\n{perc_min}-{perc_max}%ile',
                ha='center', va='top', fontsize=9, color='gray', fontweight='bold')

plt.tight_layout()
viz1_path = os.path.join(output_dir, 'gt1_criteria_c_distribution.png')
plt.savefig(viz1_path, dpi=150, bbox_inches='tight')
print(f"\n[OK] Saved: {viz1_path}")
plt.close()

# Visualization 2: Pie chart (excluding unclassified)
fig, ax = plt.subplots(figsize=(10, 8))

# Only show classified students
classified_segments = [s for s in segment_order if s != 'unclassified']
classified_values = [distribution[s] for s in classified_segments]
classified_colors = colors[:5]

wedges, texts, autotexts = ax.pie(classified_values, labels=classified_segments,
                                    autopct='%1.1f%%', colors=classified_colors, startangle=90,
                                    textprops={'fontsize': 11, 'fontweight': 'bold'})

# Enhance labels
for i, (wedge, segment) in enumerate(zip(wedges, classified_segments)):
    criteria = criteria_c[segment]
    score_min, score_max = criteria['score']
    count = distribution[segment]
    texts[i].set_text(f'{segment}\n({score_min}-{score_max}개)\n{count:,}명')
    texts[i].set_fontsize(10)
    texts[i].set_fontweight('bold')

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(11)

ax.set_title(f'GT1 학생 구간별 비율 - C안 절대+상대 결합\n(분류 성공: {classified:,}명, {classified/total_students*100:.1f}%)', 
             fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
viz2_path = os.path.join(output_dir, 'gt1_criteria_c_pie.png')
plt.savefig(viz2_path, dpi=150, bbox_inches='tight')
print(f"[OK] Saved: {viz2_path}")
plt.close()

# Visualization 3: Comparison with A안 and B안
# Load previous results for comparison
print("\n" + "=" * 80)
print("Creating Comparison Chart")
print("=" * 80)

# A안 results (from previous analysis)
a_dist = {'below2': 139, 'below1': 748, 'on': 396, 'above1': 48, 'above2': 53}
# B안 results (from previous analysis)
b_dist = {'below2': 232, 'below1': 166, 'on': 472, 'above1': 326, 'above2': 142}
# C안 results (current)
c_dist = {s: distribution[s] for s in classified_segments}

fig, ax = plt.subplots(figsize=(14, 8))

x = np.arange(len(classified_segments))
width = 0.25

bars1 = ax.bar(x - width, [a_dist[s] for s in classified_segments], width, 
               label='A안 (절대평가)', alpha=0.8, color='steelblue')
bars2 = ax.bar(x, [b_dist[s] for s in classified_segments], width, 
               label='B안 (상대평가)', alpha=0.8, color='orange')
bars3 = ax.bar(x + width, [c_dist[s] for s in classified_segments], width, 
               label='C안 (절대+상대)', alpha=0.8, color='green')

ax.set_xlabel('구간', fontsize=13, fontweight='bold')
ax.set_ylabel('학생 수', fontsize=13, fontweight='bold')
ax.set_title('GT1 학생 분포 비교 - A안 vs B안 vs C안', fontsize=15, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(classified_segments)
ax.legend(fontsize=11)
ax.grid(axis='y', alpha=0.3)

# Add value labels
for bars in [bars1, bars2, bars3]:
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=8)

plt.tight_layout()
viz3_path = os.path.join(output_dir, 'gt1_criteria_abc_comparison.png')
plt.savefig(viz3_path, dpi=150, bbox_inches='tight')
print(f"[OK] Saved: {viz3_path}")
plt.close()

# ============================================================================
# SAVE REPORT
# ============================================================================
print("\n" + "=" * 80)
print("Saving Report")
print("=" * 80)

report_path = os.path.join(output_dir, 'gt1_criteria_c_report.txt')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("GT1 학생 분포 분석 - C안 절대+상대 결합 기준\n")
    f.write("=" * 80 + "\n\n")
    
    f.write(f"총 학생 수: {total_students:,}명\n\n")
    
    f.write("C안 절대+상대 결합 기준점:\n")
    f.write("-" * 80 + "\n\n")
    
    for segment in segment_order:
        if segment == 'unclassified':
            count = distribution[segment]
            pct = distribution_pct[segment]
            f.write(f"{segment}\n")
            f.write(f"  해석: 두 조건을 모두 충족하지 못함\n")
            f.write(f"  학생 수: {count:,}명 ({pct:.2f}%)\n\n")
        else:
            criteria = criteria_c[segment]
            score_min, score_max = criteria['score']
            perc_min, perc_max = criteria['percentile']
            desc = criteria['desc']
            count = distribution[segment]
            pct = distribution_pct[segment]
            
            f.write(f"{segment}\n")
            f.write(f"  조건: {desc}\n")
            f.write(f"  점수 범위: {score_min}~{score_max}개\n")
            f.write(f"  백분위 범위: {perc_min}~{perc_max}%\n")
            f.write(f"  학생 수: {count:,}명 ({pct:.2f}%)\n\n")
    
    f.write("\n" + "=" * 80 + "\n")
    f.write("요약 통계\n")
    f.write("=" * 80 + "\n\n")
    
    f.write(f"분류 성공: {classified:,}명 ({classified/total_students*100:.2f}%)\n")
    f.write(f"분류 실패: {distribution['unclassified']:,}명 ({distribution_pct['unclassified']:.2f}%)\n\n")
    
    f.write(f"기준 미달 (below2 + below1): {below_on:,}명 ({below_on/total_students*100:.2f}%)\n")
    f.write(f"기준 충족 이상 (on + above): {on_above:,}명 ({on_above/total_students*100:.2f}%)\n")

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
