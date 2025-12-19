
import pandas as pd
import os

file_path = r"c:\Users\user\projects\LT_data_analysis\raw_data\LT_문항데이터_2025년_11월_Gr2.xlsx"
sheet_name = "GT2"

try:
    # Read the first few rows to inspect structure
    df_preview = pd.read_excel(file_path, sheet_name=sheet_name, nrows=30, header=None)
    print(df_preview)
except Exception as e:
    print(f"Error reading Excel file: {e}")
