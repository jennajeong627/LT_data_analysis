import pandas as pd
import openpyxl

# Excel 파일 경로
excel_file = 'LT_데이터집계_2024년_11월_GR1_251028.xlsx'

# 변환할 시트 목록
sheet_names = ['학생별구간분류', '학생문항별결과', '문항난이도별결과']

# 각 시트를 CSV로 변환
for sheet_name in sheet_names:
    print(f"\n처리 중: {sheet_name}")
    
    # 먼저 시트의 구조를 확인 (처음 30행 읽기)
    df_preview = pd.read_excel(excel_file, sheet_name=sheet_name, header=None, nrows=30)
    print(f"\n{sheet_name} - 처음 30행 미리보기:")
    print(df_preview)
    
    # 28행부터 데이터 읽기 (header=27로 설정하면 28행이 헤더가 됨)
    df = pd.read_excel(excel_file, sheet_name=sheet_name, header=27)
    
    # CSV 파일명 생성
    csv_filename = f'2024_11월_{sheet_name}.csv'
    
    # CSV로 저장
    df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
    
    print(f"\n저장됨: {csv_filename}")
    print(f"행 수: {len(df)}")
    print(f"열 수: {len(df.columns)}")
    print(f"\n컬럼 목록:")
    print(df.columns.tolist())
    print(f"\n처음 5행:")
    print(df.head())

print("\n\n모든 시트 변환 완료!")
