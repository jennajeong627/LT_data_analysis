import pandas as pd

print("=" * 80)
print("GT1 학생 수 차이 분석")
print("=" * 80)

# File 1: 학생문항별결과
print("\n[1] 학생문항별결과.csv 파일:")
df_items = pd.read_csv('data/2024_5월_학생문항별결과.csv', encoding='utf-8-sig')
df_gt1_items = df_items[df_items['레벨'] == 'GT1']
print(f"   GT1 총 레코드 수: {len(df_gt1_items):,}")
print(f"   GT1 고유 학생 수: {df_gt1_items['학생명'].nunique():,}")

# File 2: 문항난이도별결과
print("\n[2] 문항난이도별결과.csv 파일:")
df_agg = pd.read_csv('data/2024_5월_문항난이도별결과.csv', encoding='utf-8-sig')
df_gt1_agg = df_agg[df_agg['레벨'] == 'GT1']
print(f"   GT1 총 레코드 수: {len(df_gt1_agg):,}")

# Groupby로 학생 수 계산
df_students = df_agg.groupby(['레벨', '학생명'])['정답 수'].sum().reset_index()
df_gt1_students = df_students[df_students['레벨'] == 'GT1']
print(f"   GT1 고유 학생 수 (groupby): {len(df_gt1_students):,}")

# 학생명 비교
students_items = set(df_gt1_items['학생명'].unique())
students_agg = set(df_gt1_students['학생명'].unique())

print("\n[3] 학생명 비교:")
print(f"   학생문항별결과에만 있는 학생: {len(students_items - students_agg):,}명")
print(f"   문항난이도별결과에만 있는 학생: {len(students_agg - students_items):,}명")
print(f"   두 파일 모두에 있는 학생: {len(students_items & students_agg):,}명")

# 차이 확인
if len(students_items - students_agg) > 0:
    print("\n[4] 학생문항별결과에만 있는 학생 샘플 (최대 10명):")
    for i, student in enumerate(list(students_items - students_agg)[:10]):
        print(f"   {i+1}. {student}")

if len(students_agg - students_items) > 0:
    print("\n[5] 문항난이도별결과에만 있는 학생 샘플 (최대 10명):")
    for i, student in enumerate(list(students_agg - students_items)[:10]):
        print(f"   {i+1}. {student}")

print("\n" + "=" * 80)
print("결론:")
print("=" * 80)
print(f"학생문항별결과: {len(students_items):,}명")
print(f"문항난이도별결과: {len(students_agg):,}명")
print(f"차이: {abs(len(students_items) - len(students_agg)):,}명")
print("=" * 80)
