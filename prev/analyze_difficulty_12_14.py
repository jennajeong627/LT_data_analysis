import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

# 한글 폰트 설정
matplotlib.rc('font', family='Malgun Gothic')
matplotlib.rc('axes', unicode_minus=False)

# 1. 학생 문항별 결과 데이터 로드
df = pd.read_csv('2024_5월_학생문항별결과.csv', encoding='utf-8-sig')

print("컬럼명:", df.columns.tolist())
print("\n데이터 샘플:")
print(df.head())
print(f"\n전체 데이터 행 수: {len(df)}")

# 2. 난이도 매핑 (English_reading skill.md 기반)
difficulty_mapping = {
    1: '⭐', 2: '⭐', 3: '⭐', 4: '⭐',  # star_⭐
    5: '⭐⭐', 6: '⭐⭐', 7: '⭐⭐', 8: '⭐⭐', 9: '⭐⭐', 10: '⭐⭐',  # star_⭐⭐
    11: '⭐⭐⭐', 12: '⭐⭐⭐', 13: '⭐⭐⭐', 14: '⭐⭐⭐', 15: '⭐⭐⭐', 16: '⭐⭐⭐',  # star_⭐⭐⭐
    17: '⭐⭐⭐⭐', 18: '⭐⭐⭐⭐', 19: '⭐⭐⭐⭐', 20: '⭐⭐⭐⭐'  # star_⭐⭐⭐⭐
}

# 3. '정답 수' 컬럼을 사용하여 12~14점 학생 필터링
# 데이터에 이미 '정답 수' 컬럼이 있음
print("\n정답 수 분포:")
print(df['정답 수'].value_counts().sort_index())

# 4. 12~14점 학생 필터링
target_df = df[(df['정답 수'] >= 12) & (df['정답 수'] <= 14)].copy()

# 고유 학생 수 확인
unique_students = target_df['학번'].nunique()
print(f"\n12~14점 학생 수: {unique_students}")
print(f"대상 데이터 행 수: {len(target_df)}")

print("\n대상 데이터 샘플:")
print(target_df.head(20))

# 5. 문항 순번을 문항번호로 사용
question_col = '문항 순번'

# 6. 난이도 매핑 추가
target_df['난이도_매핑'] = target_df[question_col].map(difficulty_mapping)

# 7. 난이도별 정답률 계산
# '정답 여부'가 'Y'인 경우를 1로, 아니면 0으로 변환
target_df['정답'] = (target_df['정답 여부'] == 'Y').astype(int)

difficulty_stats = target_df.groupby('난이도_매핑').agg({
    '정답': ['sum', 'count', 'mean']
}).reset_index()

difficulty_stats.columns = ['난이도', '정답수', '전체응답수', '정답률']
difficulty_stats['정답률_퍼센트'] = difficulty_stats['정답률'] * 100

# 콘솔 출력 대신 파일에 저장
with open('분석결과_12_14점.txt', 'w', encoding='utf-8') as f:
    f.write("=== 난이도별 정답률 (12~14점 학생) ===\n")
    f.write(difficulty_stats.to_string())
    f.write("\n\n")

print("난이도별 정답률 분석 완료 (분석결과_12_14점.txt 파일 참조)")

# 9. 문항별 정답률도 계산
question_stats = target_df.groupby(question_col).agg({
    '정답': ['sum', 'count', 'mean']
}).reset_index()
question_stats.columns = ['문항번호', '정답수', '전체응답수', '정답률']
question_stats['정답률_퍼센트'] = question_stats['정답률'] * 100
question_stats['난이도'] = question_stats['문항번호'].map(difficulty_mapping)

# 파일에 추가
with open('분석결과_12_14점.txt', 'a', encoding='utf-8') as f:
    f.write("=== 문항별 정답률 (12~14점 학생) ===\n")
    f.write(question_stats.to_string())
    f.write("\n\n")

print("문항별 정답률 분석 완료")

# 10. 난이도별 학생별 점수 계산 (min, max)
# 각 학생이 각 난이도에서 맞춘 문항 수 계산
student_difficulty_scores = target_df.groupby(['학번', '난이도_매핑'])['정답'].sum().reset_index()
student_difficulty_scores.columns = ['학번', '난이도', '난이도별_정답수']

# 난이도별 min, max 점수 계산
difficulty_minmax = student_difficulty_scores.groupby('난이도')['난이도별_정답수'].agg(['min', 'max']).reset_index()
difficulty_minmax.columns = ['난이도', '최소점수', '최대점수']

# 난이도별 문항 수 계산
difficulty_question_count = pd.Series(difficulty_mapping).value_counts().to_dict()
difficulty_minmax['총문항수'] = difficulty_minmax['난이도'].map({
    '⭐': 4,
    '⭐⭐': 6,
    '⭐⭐⭐': 6,
    '⭐⭐⭐⭐': 4
})

# 파일에 추가
with open('분석결과_12_14점.txt', 'a', encoding='utf-8') as f:
    f.write("=== 난이도별 최소/최대 점수 (12~14점 학생) ===\n")
    f.write(difficulty_minmax.to_string(index=False))
    f.write("\n\n")

try:
    print("\n=== 난이도별 최소/최대 점수 ===")
    print(difficulty_minmax.to_string(index=False))
except UnicodeEncodeError:
    print("\n=== 난이도별 최소/최대 점수 ===")
    print("(콘솔 출력 생략 - 분석결과_12_14점.txt 및 난이도별_최소최대점수_12_14점.csv 파일 참조)")

# 11. 결과 저장
difficulty_stats.to_csv('난이도별_정답률_12_14점.csv', index=False, encoding='utf-8-sig')
question_stats.to_csv('문항별_정답률_12_14점.csv', index=False, encoding='utf-8-sig')
difficulty_minmax.to_csv('난이도별_최소최대점수_12_14점.csv', index=False, encoding='utf-8-sig')

# 12. 시각화
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# 난이도별 정답률 막대 그래프
difficulty_order = ['⭐', '⭐⭐', '⭐⭐⭐', '⭐⭐⭐⭐']
difficulty_stats_sorted = difficulty_stats.set_index('난이도').reindex(difficulty_order).reset_index()

colors = ['#4CAF50', '#FFC107', '#FF9800', '#F44336']  # 쉬움 -> 어려움
ax1 = axes[0]
bars1 = ax1.bar(difficulty_stats_sorted['난이도'], difficulty_stats_sorted['정답률_퍼센트'], color=colors, alpha=0.8, edgecolor='black')
ax1.set_xlabel('난이도', fontsize=14, fontweight='bold')
ax1.set_ylabel('정답률 (%)', fontsize=14, fontweight='bold')
ax1.set_title('난이도별 정답률 (12~14점 학생)', fontsize=16, fontweight='bold')
ax1.set_ylim(0, 100)
ax1.grid(axis='y', alpha=0.3, linestyle='--')

# 값 표시
for i, bar in enumerate(bars1):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.1f}%',
             ha='center', va='bottom', fontsize=12, fontweight='bold')

# 문항별 정답률 그래프
ax2 = axes[1]
question_stats_sorted = question_stats.sort_values('문항번호')
question_colors = [colors[difficulty_order.index(d)] for d in question_stats_sorted['난이도']]

bars2 = ax2.bar(question_stats_sorted['문항번호'], question_stats_sorted['정답률_퍼센트'], 
                color=question_colors, alpha=0.8, edgecolor='black')
ax2.set_xlabel('문항 번호', fontsize=14, fontweight='bold')
ax2.set_ylabel('정답률 (%)', fontsize=14, fontweight='bold')
ax2.set_title('문항별 정답률 (12~14점 학생)', fontsize=16, fontweight='bold')
ax2.set_ylim(0, 100)
ax2.set_xticks(question_stats_sorted['문항번호'])
ax2.grid(axis='y', alpha=0.3, linestyle='--')

# 범례 추가
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor=colors[0], edgecolor='black', label='⭐ (쉬움)'),
    Patch(facecolor=colors[1], edgecolor='black', label='⭐⭐'),
    Patch(facecolor=colors[2], edgecolor='black', label='⭐⭐⭐'),
    Patch(facecolor=colors[3], edgecolor='black', label='⭐⭐⭐⭐ (어려움)')
]
ax2.legend(handles=legend_elements, loc='upper right', fontsize=10)

plt.tight_layout()
plt.savefig('score_12_14_difficulty_analysis.png', dpi=300, bbox_inches='tight')
print("\n그래프가 'score_12_14_difficulty_analysis.png'로 저장되었습니다.")

plt.show()

print("\n=== 분석 완료 ===")
print(f"대상 학생 수: {unique_students}")
print(f"총 응답 수: {len(target_df)}")
print("\n결과 파일:")
print("- 난이도별_정답률_12_14점.csv")
print("- 문항별_정답률_12_14점.csv")
print("- 난이도별_최소최대점수_12_14점.csv")
print("- score_12_14_difficulty_analysis.png")
