import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import os

# Set Korean font
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# Output directory
# 결과 파일 경로
output_dir = "output/11월/reanalyze_gt1_1796"
# 각 월별 데이터 CSV 파일 경로
csv_file_path = "2024_11월_data/2024_11월__학생문항별결과.csv"
os.makedirs(output_dir, exist_ok=True)

print("=" * 80)
print("GT1 전체 분석 재실행 (1,796명 기준)")
print("=" * 80)

# Load student-item data
print("\n[1] 데이터 로딩...")
# 각 월별 데이터 CSV 파일 경로
df_items = pd.read_csv(csv_file_path, encoding='utf-8-sig')
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
print(f"   평균 점수: {student_scores['전체_정답_수'].mean():.2f}점")
print(f"   표준편차: {student_scores['전체_정답_수'].std():.2f}")

# Calculate percentile
student_scores['백분위'] = student_scores['전체_정답_수'].rank(pct=True) * 100

# ============================================================================
# A안, B안, C안 분류
# ============================================================================
print("\n[2] A/B/C안 기준으로 분류...")

# A안 절대평가
def classify_a(score):
    if score <= 6: return 'below2'
    elif score <= 11: return 'below1'
    elif score <= 15: return 'on'
    elif score <= 17: return 'above1'
    else: return 'above2'

# B안 상대평가
def classify_b(percentile):
    if percentile < 20: return 'below2'
    elif percentile < 40: return 'below1'
    elif percentile < 70: return 'on'
    elif percentile < 90: return 'above1'
    else: return 'above2'

# C안 절대+상대
def classify_c(row):
    score = row['전체_정답_수']
    percentile = row['백분위']
    
    criteria = {
        'below2': (0, 6, 0, 30),
        'below1': (7, 11, 30, 55),
        'on': (12, 15, 55, 75),
        'above1': (16, 17, 75, 85),
        'above2': (18, 20, 85, 100)
    }
    
    for segment, (min_s, max_s, min_p, max_p) in criteria.items():
        if min_s <= score <= max_s:
            if segment == 'above2':
                if min_p <= percentile <= max_p:
                    return segment
            else:
                if min_p <= percentile < max_p:
                    return segment
    return 'unclassified'

student_scores['A안'] = student_scores['전체_정답_수'].apply(classify_a)
student_scores['B안'] = student_scores['백분위'].apply(classify_b)
student_scores['C안'] = student_scores.apply(classify_c, axis=1)

# 분포 계산
segment_order = ['below2', 'below1', 'on', 'above1', 'above2']

print("\nA안 (절대평가) 분포:")
a_dist = student_scores['A안'].value_counts().reindex(segment_order, fill_value=0)
for seg in segment_order:
    count = a_dist[seg]
    pct = count / total_students * 100
    print(f"  {seg}: {count:,}명 ({pct:.2f}%)")

print("\nB안 (상대평가) 분포:")
b_dist = student_scores['B안'].value_counts().reindex(segment_order, fill_value=0)
for seg in segment_order:
    count = b_dist[seg]
    pct = count / total_students * 100
    print(f"  {seg}: {count:,}명 ({pct:.2f}%)")

print("\nC안 (절대+상대) 분포:")
c_dist = student_scores['C안'].value_counts()
for seg in segment_order + ['unclassified']:
    count = c_dist.get(seg, 0)
    pct = count / total_students * 100
    print(f"  {seg}: {count:,}명 ({pct:.2f}%)")

# ============================================================================
# 정규분포 그래프 생성
# ============================================================================
print("\n[3] 정규분포 그래프 생성...")

scores = student_scores['전체_정답_수'].values
mu, sigma = scores.mean(), scores.std()
x = np.linspace(0, 20, 1000)
normal_curve = stats.norm.pdf(x, mu, sigma)

fig, ax = plt.subplots(figsize=(16, 9))

# Histogram
n, bins, patches = ax.hist(scores, bins=range(0, 22), density=True, 
                           alpha=0.6, color='steelblue', edgecolor='black', 
                           linewidth=1.2, label='실제 분포')

# Color by A안 segments
segment_colors = {
    'below2': '#e53e3e',
    'below1': '#ed8936',
    'on': '#48bb78',
    'above1': '#38a169',
    'above2': '#2f855a'
}

for patch, left_edge in zip(patches, bins[:-1]):
    score = int(left_edge)
    segment = classify_a(score)
    patch.set_facecolor(segment_colors[segment])
    patch.set_alpha(0.7)

# Normal curve
ax.plot(x, normal_curve, 'r-', linewidth=3, label=f'정규분포 (μ={mu:.2f}, σ={sigma:.2f})')

# Boundaries
for boundary in [6.5, 11.5, 15.5, 17.5]:
    ax.axvline(x=boundary, color='black', linestyle='--', linewidth=2, alpha=0.5)

ax.axvline(x=mu, color='darkred', linestyle='-', linewidth=2.5, alpha=0.8)

ax.set_xlabel('점수 (정답 수)', fontsize=13, fontweight='bold')
ax.set_ylabel('확률 밀도', fontsize=13, fontweight='bold')
ax.set_title(f'GT1 학생 점수 분포 - 정규분포 (N={total_students:,})', 
             fontsize=15, fontweight='bold', pad=20)
ax.set_xlim(-0.5, 20.5)
ax.set_xticks(range(0, 21, 1))
ax.grid(True, alpha=0.3, linestyle='--')
ax.legend(loc='upper right', fontsize=10)

plt.tight_layout()
viz_path = os.path.join(output_dir, 'gt1_normal_distribution_1796.png')
plt.savefig(viz_path, dpi=150, bbox_inches='tight')
print(f"   저장: {viz_path}")
plt.close()

# ============================================================================
# 통계 저장
# ============================================================================
print("\n[4] 통계 저장...")

stats_path = os.path.join(output_dir, 'gt1_statistics_1796.txt')
with open(stats_path, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("GT1 학생 통계 (1,796명 기준)\n")
    f.write("=" * 80 + "\n\n")
    
    f.write(f"총 학생 수: {total_students:,}명\n")
    f.write(f"평균 점수: {mu:.2f}점\n")
    f.write(f"표준편차: {sigma:.2f}\n")
    f.write(f"중앙값: {student_scores['전체_정답_수'].median():.1f}점\n")
    f.write(f"최소값: {student_scores['전체_정답_수'].min()}점\n")
    f.write(f"최대값: {student_scores['전체_정답_수'].max()}점\n\n")
    
    f.write("A안 (절대평가) 분포:\n")
    f.write("-" * 80 + "\n")
    for seg in segment_order:
        count = a_dist[seg]
        pct = count / total_students * 100
        f.write(f"{seg}: {count:,}명 ({pct:.2f}%)\n")
    
    f.write("\nB안 (상대평가) 분포:\n")
    f.write("-" * 80 + "\n")
    for seg in segment_order:
        count = b_dist[seg]
        pct = count / total_students * 100
        f.write(f"{seg}: {count:,}명 ({pct:.2f}%)\n")
    
    f.write("\nC안 (절대+상대) 분포:\n")
    f.write("-" * 80 + "\n")
    for seg in segment_order + ['unclassified']:
        count = c_dist.get(seg, 0)
        pct = count / total_students * 100
        f.write(f"{seg}: {count:,}명 ({pct:.2f}%)\n")

print(f"   저장: {stats_path}")

# CSV 저장
csv_path = os.path.join(output_dir, 'gt1_student_scores_1796.csv')
student_scores.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f"   저장: {csv_path}")

print("\n" + "=" * 80)
print("재분석 완료!")
print("=" * 80)
print(f"총 학생 수: {total_students:,}명")
print(f"평균: {mu:.2f}점, 표준편차: {sigma:.2f}")
print("=" * 80)
