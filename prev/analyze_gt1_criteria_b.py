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
print("GT1 Distribution Analysis - B안 상대평가 기준")
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

# B안 상대평가 기준점 (백분위 기준)
criteria_b_percentile = {
    'below2': (0, 20, '하위권, 기초 부족'),
    'below1': (21, 40, '하위권이지만 성장 가능'),
    'on': (41, 70, '중위권, 기준 성취'),
    'above1': (71, 90, '상위권, 우수'),
    'above2': (91, 100, '최상위권')
}

# Calculate percentile for each student
df_gt1['백분위'] = df_gt1['전체 정답 수'].rank(pct=True) * 100

# Classify by percentile
def classify_by_percentile(percentile):
    for segment, (min_p, max_p, desc) in criteria_b_percentile.items():
        if segment == 'above2':  # 최상위는 상한 포함
            if min_p <= percentile <= max_p:
                return segment
        else:
            if min_p <= percentile < max_p:
                return segment
    return 'unknown'

df_gt1['구간'] = df_gt1['백분위'].apply(classify_by_percentile)

# ============================================================================
# PART 1: Distribution Analysis
# ============================================================================
print("\n" + "=" * 80)
print("PART 1: B안 상대평가 기준 - GT1 학생 분포")
print("=" * 80)

segment_order = ['below2', 'below1', 'on', 'above1', 'above2']
distribution = df_gt1['구간'].value_counts().reindex(segment_order, fill_value=0)
distribution_pct = (distribution / total_students * 100).round(2)

print("\nB안 상대평가 기준점 (백분위 기준):")
print("-" * 80)
for segment in segment_order:
    min_p, max_p, desc = criteria_b_percentile[segment]
    count = distribution[segment]
    pct = distribution_pct[segment]
    
    # Calculate actual score range for this percentile segment
    segment_students = df_gt1[df_gt1['구간'] == segment]
    if len(segment_students) > 0:
        min_score = segment_students['전체 정답 수'].min()
        max_score = segment_students['전체 정답 수'].max()
        score_range = f"{int(min_score)}~{int(max_score)}개"
    else:
        score_range = "N/A"
    
    print(f"\n{segment:10s} (백분위 {min_p}~{max_p}%)")
    print(f"  해석: {desc}")
    print(f"  실제 점수 범위: {score_range}")
    print(f"  학생 수: {count:,}명 ({pct:.2f}%)")

# Summary statistics
print("\n" + "=" * 80)
print("요약 통계")
print("=" * 80)

below_on = distribution['below2'] + distribution['below1']
on_above = distribution['on'] + distribution['above1'] + distribution['above2']

print(f"\n하위권 (below2 + below1): {below_on:,}명 ({below_on/total_students*100:.2f}%)")
print(f"중위권 이상 (on + above): {on_above:,}명 ({on_above/total_students*100:.2f}%)")

print(f"\n평균 정답 수: {df_gt1['전체 정답 수'].mean():.2f}개")
print(f"중앙값: {df_gt1['전체 정답 수'].median():.1f}개")

# ============================================================================
# VISUALIZATIONS
# ============================================================================
print("\n" + "=" * 80)
print("Creating Visualizations")
print("=" * 80)

# Visualization 1: Bar chart with percentile ranges
fig, ax = plt.subplots(figsize=(12, 7))

colors = ['#e53e3e', '#ed8936', '#48bb78', '#38a169', '#2f855a']
bars = ax.bar(segment_order, distribution.values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

ax.set_xlabel('구간', fontsize=13, fontweight='bold')
ax.set_ylabel('학생 수', fontsize=13, fontweight='bold')
ax.set_title('GT1 학생 분포 - B안 상대평가 기준 (백분위)', fontsize=15, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3, linestyle='--')

# Add value labels
for i, (bar, segment) in enumerate(zip(bars, segment_order)):
    height = bar.get_height()
    pct = distribution_pct[segment]
    min_p, max_p, desc = criteria_b_percentile[segment]
    
    # Count and percentage on top
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height):,}명\n({pct:.1f}%)',
            ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Percentile range below
    ax.text(i, -max(distribution.values)*0.08, f'{min_p}-{max_p}%ile',
            ha='center', va='top', fontsize=10, color='gray', fontweight='bold')

plt.tight_layout()
viz1_path = os.path.join(output_dir, 'gt1_criteria_b_distribution.png')
plt.savefig(viz1_path, dpi=150, bbox_inches='tight')
print(f"\n[OK] Saved: {viz1_path}")
plt.close()

# Visualization 2: Pie chart
fig, ax = plt.subplots(figsize=(10, 8))

wedges, texts, autotexts = ax.pie(distribution.values, labels=segment_order,
                                    autopct='%1.1f%%', colors=colors, startangle=90,
                                    textprops={'fontsize': 11, 'fontweight': 'bold'})

# Enhance labels
for i, (wedge, segment) in enumerate(zip(wedges, segment_order)):
    min_p, max_p, desc = criteria_b_percentile[segment]
    count = distribution[segment]
    texts[i].set_text(f'{segment}\n({min_p}-{max_p}%ile)\n{count:,}명')
    texts[i].set_fontsize(10)
    texts[i].set_fontweight('bold')

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(11)

ax.set_title('GT1 학생 구간별 비율 - B안 상대평가', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
viz2_path = os.path.join(output_dir, 'gt1_criteria_b_pie.png')
plt.savefig(viz2_path, dpi=150, bbox_inches='tight')
print(f"[OK] Saved: {viz2_path}")
plt.close()

# Visualization 3: Stacked bar with percentile
fig, ax = plt.subplots(figsize=(12, 6))

# Create stacked bar
bottom = 0
for i, segment in enumerate(segment_order):
    count = distribution[segment]
    pct = distribution_pct[segment]
    
    ax.barh(0, pct, left=bottom, height=0.5, color=colors[i], 
            alpha=0.9, edgecolor='black', linewidth=2, label=segment)
    
    # Add label if segment is large enough
    if pct > 3:
        min_p, max_p, desc = criteria_b_percentile[segment]
        ax.text(bottom + pct/2, 0, f'{segment}\n{int(count):,}명\n({pct:.1f}%)',
                ha='center', va='center', fontsize=10, fontweight='bold', color='white')
    
    bottom += pct

ax.set_xlim(0, 100)
ax.set_ylim(-0.5, 0.5)
ax.set_xlabel('비율 (%)', fontsize=13, fontweight='bold')
ax.set_title('GT1 학생 구간 분포 (100% 스택) - B안 상대평가', fontsize=14, fontweight='bold', pad=20)
ax.set_yticks([])
ax.grid(axis='x', alpha=0.3)
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=5, fontsize=10)

plt.tight_layout()
viz3_path = os.path.join(output_dir, 'gt1_criteria_b_stacked.png')
plt.savefig(viz3_path, dpi=150, bbox_inches='tight')
print(f"[OK] Saved: {viz3_path}")
plt.close()

# ============================================================================
# SAVE REPORT
# ============================================================================
print("\n" + "=" * 80)
print("Saving Report")
print("=" * 80)

report_path = os.path.join(output_dir, 'gt1_criteria_b_report.txt')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("GT1 학생 분포 분석 - B안 상대평가 기준\n")
    f.write("=" * 80 + "\n\n")
    
    f.write(f"총 학생 수: {total_students:,}명\n\n")
    
    f.write("B안 상대평가 기준점 (백분위 기준):\n")
    f.write("-" * 80 + "\n\n")
    
    for segment in segment_order:
        min_p, max_p, desc = criteria_b_percentile[segment]
        count = distribution[segment]
        pct = distribution_pct[segment]
        
        segment_students = df_gt1[df_gt1['구간'] == segment]
        if len(segment_students) > 0:
            min_score = segment_students['전체 정답 수'].min()
            max_score = segment_students['전체 정답 수'].max()
            score_range = f"{int(min_score)}~{int(max_score)}개"
        else:
            score_range = "N/A"
        
        f.write(f"{segment} (백분위 {min_p}~{max_p}%)\n")
        f.write(f"  해석: {desc}\n")
        f.write(f"  실제 점수 범위: {score_range}\n")
        f.write(f"  학생 수: {count:,}명 ({pct:.2f}%)\n\n")
    
    f.write("\n" + "=" * 80 + "\n")
    f.write("요약 통계\n")
    f.write("=" * 80 + "\n\n")
    
    f.write(f"하위권 (below2 + below1): {below_on:,}명 ({below_on/total_students*100:.2f}%)\n")
    f.write(f"중위권 이상 (on + above): {on_above:,}명 ({on_above/total_students*100:.2f}%)\n\n")
    
    f.write(f"평균 정답 수: {df_gt1['전체 정답 수'].mean():.2f}개\n")
    f.write(f"중앙값: {df_gt1['전체 정답 수'].median():.1f}개\n")

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
