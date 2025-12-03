import pandas as pd

print("=" * 80)
print("GT1 중복 응시 학생 분석")
print("=" * 80)

# 학생문항별결과 파일 로드
df_items = pd.read_csv('data/2024_5월_학생문항별결과.csv', encoding='utf-8-sig')
df_gt1 = df_items[df_items['레벨'] == 'GT1']

# 문항 1번만 필터링 (각 학생이 문항 1번을 몇 번 응시했는지 확인)
df_item1 = df_gt1[df_gt1['문항 순번'] == 1]

# 학생별 응시 횟수 계산
student_attempts = df_item1.groupby('학생명').size().reset_index()
student_attempts.columns = ['학생명', '응시_횟수']

# 중복 응시 학생 (2회 이상)
duplicate_students = student_attempts[student_attempts['응시_횟수'] > 1].sort_values('응시_횟수', ascending=False)

print(f"\n총 GT1 학생 수: {len(student_attempts):,}명")
print(f"1회 응시 학생: {len(student_attempts[student_attempts['응시_횟수'] == 1]):,}명")
print(f"중복 응시 학생: {len(duplicate_students):,}명")

if len(duplicate_students) > 0:
    print(f"\n중복 응시 횟수 분포:")
    for count in sorted(duplicate_students['응시_횟수'].unique(), reverse=True):
        num_students = len(duplicate_students[duplicate_students['응시_횟수'] == count])
        print(f"  {count}회 응시: {num_students}명")
    
    print(f"\n중복 응시 학생 목록 (총 {len(duplicate_students)}명):")
    print("-" * 80)
    print(f"{'번호':<6} {'학생명':<30} {'응시횟수':<10}")
    print("-" * 80)
    
    for idx, row in duplicate_students.iterrows():
        print(f"{idx+1:<6} {row['학생명']:<30} {row['응시_횟수']}회")
    
    # 중복 응시 학생의 상세 정보 (처음 5명)
    print(f"\n중복 응시 학생 상세 정보 (처음 5명):")
    print("=" * 80)
    
    for i, (student_name, attempts) in enumerate(duplicate_students.head(5).values):
        print(f"\n[{i+1}] {student_name} - {attempts}회 응시")
        print("-" * 80)
        
        # 해당 학생의 모든 응시 기록 (문항 1번만)
        student_records = df_item1[df_item1['학생명'] == student_name]
        
        for j, (idx, record) in enumerate(student_records.iterrows()):
            print(f"  응시 {j+1}:")
            print(f"    정답 여부: {record['정답 여부']}")
            if '응시일' in record:
                print(f"    응시일: {record['응시일']}")
            if '코드' in record:
                print(f"    코드: {record['코드']}")

# CSV로 저장
output_path = r'C:\Users\user\.gemini\antigravity\brain\8fd772ef-33d9-4495-9894-ecaf33833f42\gt1_duplicate_students.csv'
duplicate_students.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f"\n중복 학생 목록 저장: {output_path}")

print("\n" + "=" * 80)
print("분석 완료")
print("=" * 80)
