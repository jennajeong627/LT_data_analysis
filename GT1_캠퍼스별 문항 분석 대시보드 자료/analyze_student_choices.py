import pandas as pd
import os

# 파일 경로 설정
csv_path = r"c:\Users\user\projects\LT_data_analysis\2024_5월_data\2024_5월_정오답 샘플.csv"
answer_key = {
    1: 1, 2: 3, 3: 2, 4: 3, 5: 1, 6: 4, 7: 4, 8: 2, 9: 1, 10: 3,
    11: 2, 12: 2, 13: 2, 14: 3, 15: 1, 16: 2, 17: 3, 18: 4, 19: 3, 20: 1
}

def analyze_student_choices():
    print("데이터 로딩 중...")
    try:
        # CSV 파일 읽기 (인코딩 확인 필요, 기본 utf-8 시도 후 cp949 등 시도)
        try:
            df = pd.read_csv(csv_path)
        except UnicodeDecodeError:
            df = pd.read_csv(csv_path, encoding='cp949')
            
        print(f"총 데이터 행 수: {len(df)}")
        
        # 컬럼 이름 확인 및 '정답 여부' 컬럼을 '학생선택'으로 해석
        # 데이터 샘플 확인 결과 '정답 여부' 컬럼에 1~4 값이 들어있음
        target_col = '정답 여부' 
        
        results = []
        
        for q_num in range(1, 21):
            q_data = df[df['문항 순번'] == q_num]
            total_students = len(q_data)
            
            if total_students == 0:
                print(f"{q_num}번 문항: 데이터 없음")
                continue
                
            # 보기별 카운트 (1, 2, 3, 4 등)
            counts = q_data[target_col].value_counts().sort_index()
            
            print(f"\n[ {q_num}번 문항 ] (정답: {answer_key.get(q_num, '?')})")
            print(f"총 응시 학생: {total_students}명")
            
            for choice in range(1, 5): # 1번부터 4번 보기까지 확인
                count = counts.get(choice, 0)
                ratio = (count / total_students) * 100
                is_correct = " (정답)" if choice == answer_key.get(q_num) else ""
                print(f" - {choice}번: {count}명 ({ratio:.2f}%){is_correct}")
                
            # 기타 값 확인 (결석, 마킹 오류 등)
            others = counts.index.difference([1, 2, 3, 4])
            if not others.empty:
                for val in others:
                    count = counts[val]
                    ratio = (count / total_students) * 100
                    print(f" - 기타({val}): {count}명 ({ratio:.2f}%)")

    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    analyze_student_choices()
