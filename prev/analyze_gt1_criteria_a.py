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
print("GT1 Distribution Analysis - A안 절대평가 기준")
print("=" * 80)

# Load data
print("\n[1] Loading data...")
df = pd.read_csv('data/2024_5월_문항난이도별결과.csv', encoding='utf-8-sig')

# Filter GT1 level and select required columns
df_gt1 = df[df['레벨'] == 'GT1'][['레벨', '정답 수']].copy()
print(f"   Total GT1 records: {len(df_gt1):,}")

# Get unique students by summing their correct answers
# Group by student to get total score
df_students = df.groupby(['레벨', '학생명'])['정답 수'].sum().reset_index()
df_students.columns = ['레벨', '학생명', '전체 정답 수']
df_gt1_students = df_students[df_students['레벨'] == 'GT1'].copy()

total_students = len(df_gt1_students)
print(f"   Total GT1 students: {total_students:,}")

# A안 절대평가 기준점
criteria_a = {
    'below2': (0, 6, '기초 부족'),
    'below1': (7, 11, '기초는 있으나 불안정'),
    'on': (12, 15, '교육과정 기준 충족'),
    'above1': (16, 17, '상위 수준 진입 가능'),
    'above2': (18, 20, '매우 우수, 상위권에서도 안정적')
}

# Classify students
def classify_by_criteria_a(score):
    for segment, (min_s, max_s, desc) in criteria_a.items():
        if min_s <= score <= max_s:
            return segment
    return 'unknown'

df_gt1_students['구간'] = df_gt1_students['전체 정답 수'].apply(classify_by_criteria_a)

# ============================================================================
# PART 1: Distribution Analysis
# ============================================================================
print("\n" + "=" * 80)
print("PART 1: A안 절대평가 기준 - GT1 학생 분포")
print("=" * 80)

segment_order = ['below2', 'below1', 'on', 'above1', 'above2']
distribution = df_gt1_students['구간'].value_counts().reindex(segment_order, fill_value=0)
distribution_pct = (distribution / total_students * 100).round(2)

print("\nA안 절대평가 기준점 (20문항):")
print("-" * 80)
for segment in segment_order:
    min_s, max_s, desc = criteria_a[segment]
    count = distribution[segment]
    pct = distribution_pct[segment]
    print(f"\n{segment:10s} ({min_s:2d}~{max_s:2d}개)")
    print(f"  해석: {desc}")
    print(f"  학생 수: {count:,}명 ({pct:.2f}%)")

# Summary statistics
print("\n" + "=" * 80)
print("요약 통계")
print("=" * 80)

below_on = distribution['below2'] + distribution['below1']
on_above = distribution['on'] + distribution['above1'] + distribution['above2']

print(f"\n기준 미달 (below2 + below1): {below_on:,}명 ({below_on/total_students*100:.2f}%)")
print(f"기준 충족 이상 (on + above): {on_above:,}명 ({on_above/total_students*100:.2f}%)")

print(f"\n평균 정답 수: {df_gt1_students['전체 정답 수'].mean():.2f}개")
print(f"중앙값: {df_gt1_students['전체 정답 수'].median():.1f}개")

# ============================================================================
# VISUALIZATIONS
# ============================================================================
print("\n" + "=" * 80)
print("Creating Visualizations")
print("=" * 80)

# Visualization 1: Bar chart with details
fig, ax = plt.subplots(figsize=(12, 7))

colors = ['#e53e3e', '#ed8936', '#48bb78', '#38a169', '#2f855a']
bars = ax.bar(segment_order, distribution.values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

ax.set_xlabel('구간', fontsize=13, fontweight='bold')
ax.set_ylabel('학생 수', fontsize=13, fontweight='bold')
ax.set_title('GT1 학생 분포 - A안 절대평가 기준', fontsize=15, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3, linestyle='--')

# Add value labels
for i, (bar, segment) in enumerate(zip(bars, segment_order)):
    height = bar.get_height()
    pct = distribution_pct[segment]
    min_s, max_s, desc = criteria_a[segment]
    
    # Count and percentage on top
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height):,}명\n({pct:.1f}%)',
            ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Score range below
    ax.text(i, -max(distribution.values)*0.08, f'{min_s}-{max_s}개',
            ha='center', va='top', fontsize=10, color='gray', fontweight='bold')

plt.tight_layout()
viz1_path = os.path.join(output_dir, 'gt1_criteria_a_distribution.png')
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
    min_s, max_s, desc = criteria_a[segment]
    count = distribution[segment]
    texts[i].set_text(f'{segment}\n({min_s}-{max_s}개)\n{count:,}명')
    texts[i].set_fontsize(10)
    texts[i].set_fontweight('bold')

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(11)

ax.set_title('GT1 학생 구간별 비율 - A안 절대평가', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
viz2_path = os.path.join(output_dir, 'gt1_criteria_a_pie.png')
plt.savefig(viz2_path, dpi=150, bbox_inches='tight')
print(f"[OK] Saved: {viz2_path}")
plt.close()

# Visualization 3: Stacked bar with interpretation
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
        min_s, max_s, desc = criteria_a[segment]
        ax.text(bottom + pct/2, 0, f'{segment}\n{int(count):,}명\n({pct:.1f}%)',
                ha='center', va='center', fontsize=10, fontweight='bold', color='white')
    
    bottom += pct

ax.set_xlim(0, 100)
ax.set_ylim(-0.5, 0.5)
ax.set_xlabel('비율 (%)', fontsize=13, fontweight='bold')
ax.set_title('GT1 학생 구간 분포 (100% 스택)', fontsize=14, fontweight='bold', pad=20)
ax.set_yticks([])
ax.grid(axis='x', alpha=0.3)
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=5, fontsize=10)

plt.tight_layout()
viz3_path = os.path.join(output_dir, 'gt1_criteria_a_stacked.png')
plt.savefig(viz3_path, dpi=150, bbox_inches='tight')
print(f"[OK] Saved: {viz3_path}")
plt.close()

# ============================================================================
# SAVE REPORT
# ============================================================================
print("\n" + "=" * 80)
print("Saving Report")
print("=" * 80)

report_path = os.path.join(output_dir, 'gt1_criteria_a_report.txt')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("GT1 학생 분포 분석 - A안 절대평가 기준\n")
    f.write("=" * 80 + "\n\n")
    
    f.write(f"총 학생 수: {total_students:,}명\n\n")
    
    f.write("A안 절대평가 기준점 (20문항):\n")
    f.write("-" * 80 + "\n\n")
    
    for segment in segment_order:
        min_s, max_s, desc = criteria_a[segment]
        count = distribution[segment]
        pct = distribution_pct[segment]
        
        f.write(f"{segment} ({min_s}~{max_s}개)\n")
        f.write(f"  해석: {desc}\n")
        f.write(f"  학생 수: {count:,}명 ({pct:.2f}%)\n\n")
    
    f.write("\n" + "=" * 80 + "\n")
    f.write("요약 통계\n")
    f.write("=" * 80 + "\n\n")
    
    f.write(f"기준 미달 (below2 + below1): {below_on:,}명 ({below_on/total_students*100:.2f}%)\n")
    f.write(f"기준 충족 이상 (on + above): {on_above:,}명 ({on_above/total_students*100:.2f}%)\n\n")
    
    f.write(f"평균 정답 수: {df_gt1_students['전체 정답 수'].mean():.2f}개\n")
    f.write(f"중앙값: {df_gt1_students['전체 정답 수'].median():.1f}개\n")

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
