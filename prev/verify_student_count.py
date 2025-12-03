import pandas as pd

print("=" * 80)
print("GT1 학생 수 정확한 확인")
print("=" * 80)

# 학생문항별결과 파일
df_items = pd.read_csv('data/2024_5월_학생문항별결과.csv', encoding='utf-8-sig')
df_gt1_items = df_items[df_items['레벨'] == 'GT1']

print("\n[학생문항별결과 파일]")
print(f"GT1 총 레코드 수: {len(df_gt1_items):,}")
print(f"GT1 고유 학생 수: {df_gt1_items['학생명'].nunique():,}")
print(f"학생당 평균 레코드: {len(df_gt1_items) / df_gt1_items['학생명'].nunique():.1f}")

# 문항난이도별결과 파일
df_agg = pd.read_csv('data/2024_5월_문항난이도별결과.csv', encoding='utf-8-sig')
df_gt1_agg = df_agg[df_agg['레벨'] == 'GT1']

print("\n[문항난이도별결과 파일]")
print(f"GT1 총 레코드 수: {len(df_gt1_agg):,}")

# 문항난이도별결과에서 고유 학생 수
unique_students_agg = df_gt1_agg['학생명'].nunique()
print(f"GT1 고유 학생 수: {unique_students_agg:,}")

# 학생별 레코드 수 분포
student_counts = df_gt1_agg.groupby('학생명').size()
print(f"\n학생당 레코드 수 분포:")
print(f"  최소: {student_counts.min()}")
print(f"  최대: {student_counts.max()}")
print(f"  평균: {student_counts.mean():.1f}")
print(f"  중앙값: {student_counts.median():.0f}")

# 학생문항별결과에서 문항 1번만 필터링해서 학생 수 확인
df_item1 = df_gt1_items[df_gt1_items['문항 순번'] == 1]
print(f"\n[검증] 문항 1번 응시 학생 수: {len(df_item1):,}")

print("\n" + "=" * 80)
print("결론:")
print("=" * 80)
print(f"학생문항별결과 기준 GT1 학생 수: {df_gt1_items['학생명'].nunique():,}명")
print(f"문항 1번 응시 학생 수: {len(df_item1):,}명")
print("=" * 80)
