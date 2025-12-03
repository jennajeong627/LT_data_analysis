import pandas as pd

# Load the Excel file
excel_file = 'LT_데이터집계_2024년_11월_GR1_251028.xlsx'

# List of sheets to examine
sheet_names = ['학생별구간분류', '학생문항별결과', '문항난이도별결과']

for sheet_name in sheet_names:
    print("=" * 60)
    print(f"Sheet: {sheet_name}")
    print("=" * 60)
    
    # Read raw data to examine structure
    df_raw = pd.read_excel(excel_file, sheet_name=sheet_name, header=None, engine='openpyxl')
    
    print(f"\nTotal rows: {len(df_raw)}")
    print(f"Total columns: {len(df_raw.columns)}")
    
    print(f"\n--- Examining rows 26-30 ---")
    for idx in range(25, min(31, len(df_raw))):
        row_data = df_raw.iloc[idx].dropna()
        if len(row_data) > 0:
            print(f"\nRow {idx+1}:")
            # Show first 5 columns only
            for col_idx, value in list(row_data.items())[:10]:
                print(f"  Col {col_idx}: {value}")
    
    # Try reading with row 27 as header (0-indexed row 26)
    print(f"\n--- Reading with row 28 as header ---")
    df_with_header = pd.read_excel(excel_file, sheet_name=sheet_name, header=27, engine='openpyxl')
    print(f"\nColumn names ({len(df_with_header.columns)} columns):")
    for i, col in enumerate(df_with_header.columns):
        print(f"  {i}: {col}")
    
    print(f"\nFirst 2 rows of data:")
    print(df_with_header.head(2))
    print("\n")
