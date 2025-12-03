import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Set Korean font
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# Output directory
output_dir = "analyze_gt1_c_or"
os.makedirs(output_dir, exist_ok=True)

print("=" * 80)
print("GT1 C안 (하향 OR 조건) 분석 (1,796명 기준)")
print("=" * 80)

# Load data
print("\n[1] 데이터 로딩...")
df_items = pd.read_csv('2024_5월_data/2024_5월_학생문항별결과.csv', encoding='utf-8-sig')
df_gt1 = df_items[df_items['레벨'] == 'GT1'].copy()

# 고유 식별자 생성 (학생명 + 코드)
# 코드는 첫 번째 컬럼
df_gt1['학생_ID'] = df_gt1['학생명'].astype(str) + '_' + df_gt1.iloc[:, 0].astype(str)

# 학생별 총점 계산
student_scores = df_gt1.groupby('학생_ID').agg({
    '학생명': 'first',
    '정답 여부': lambda x: (x == 'Y').sum()
}).reset_index()
student_scores.columns = ['학생_ID', '학생명', '전체_정답_수']

total_students = len(student_scores)
print(f"   GT1 학생 수: {total_students:,}명")

# Calculate percentile (Rank pct)
student_scores['백분위'] = student_scores['전체_정답_수'].rank(pct=True) * 100

# ============================================================================
# 분류 로직 정의
# ============================================================================

# 레벨 순서 (낮은 순)
level_order = ['below2', 'below1', 'on', 'above1', 'above2']
level_rank = {lvl: i for i, lvl in enumerate(level_order)}

# A안 (절대평가)
def classify_a(score):
    if score <= 6: return 'below2'
    elif score <= 11: return 'below1'
    elif score <= 15: return 'on'
    elif score <= 17: return 'above1'
    else: return 'above2'

# B안 (새로운 백분위 기준 for C안)
# 0~30 / 30~55 / 55~75 / 75~85 / 85~100
def classify_b_new(percentile):
    if percentile <= 30: return 'below2'
    elif percentile <= 55: return 'below1'
    elif percentile <= 75: return 'on'
    elif percentile <= 85: return 'above1'
    else: return 'above2'

# C안 (하향 OR)
def classify_c_or(row):
    level_a = classify_a(row['전체_정답_수'])
    level_b = classify_b_new(row['백분위'])
    
    # 둘 중 더 낮은 레벨 선택 (Min)
    rank_a = level_rank[level_a]
    rank_b = level_rank[level_b]
    
    final_rank = min(rank_a, rank_b)
    return level_order[final_rank]

# 분류 적용
student_scores['A안'] = student_scores['전체_정답_수'].apply(classify_a)
student_scores['B안_New'] = student_scores['백분위'].apply(classify_b_new)
student_scores['C안_OR'] = student_scores.apply(classify_c_or, axis=1)

# ============================================================================
# 분포 분석
# ============================================================================
print("\n[2] C안 (하향 OR) 분포 분석:")

c_or_dist = student_scores['C안_OR'].value_counts().reindex(level_order, fill_value=0)
for seg in level_order:
    count = c_or_dist[seg]
    pct = count / total_students * 100
    print(f"  {seg}: {count:,}명 ({pct:.2f}%)")

# 상세 비교 (A안 vs C안_OR)
print("\n[3] A안 vs C안_OR 비교:")
changes = pd.crosstab(student_scores['A안'], student_scores['C안_OR'])
print(changes)

# ============================================================================
# 시각화
# ============================================================================
print("\n[4] 시각화 생성...")

fig, ax = plt.subplots(figsize=(12, 8))

# Bar chart
colors = ['#e53e3e', '#ed8936', '#48bb78', '#38a169', '#2f855a']
bars = ax.bar(level_order, c_or_dist.values, color=colors, alpha=0.8, edgecolor='black')

# Labels
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 10,
            f'{int(height)}명\n({height/total_students*100:.1f}%)',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.set_title(f'GT1 C안 (하향 OR) 학생 분포 (N={total_students:,})', fontsize=16, fontweight='bold', pad=20)
ax.set_ylabel('학생 수', fontsize=12)
ax.set_ylim(0, c_or_dist.max() * 1.15)
ax.grid(axis='y', alpha=0.3, linestyle='--')

# Add explanation box
text_str = (
    "C안 (하향 OR) 기준:\n"
    "A안(점수)과 B안(백분위) 중\n"
    "더 낮은 등급을 최종 등급으로 부여\n"
    "(보수적 진단)"
)
props = dict(boxstyle='round', facecolor='wheat', alpha=0.3)
ax.text(0.95, 0.95, text_str, transform=ax.transAxes, fontsize=11,
        verticalalignment='top', horizontalalignment='right', bbox=props)

plt.tight_layout()
viz_path = os.path.join(output_dir, 'gt1_c_or_distribution_1796.png')
plt.savefig(viz_path, dpi=150, bbox_inches='tight')
print(f"   저장: {viz_path}")
plt.close()

# CSV 저장
csv_path = os.path.join(output_dir, 'gt1_c_or_analysis_1796.csv')
student_scores.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f"   저장: {csv_path}")

print("\n" + "=" * 80)
print("분석 완료")
print("=" * 80)
