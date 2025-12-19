import pandas as pd
import os

base_dir = r"c:\Users\user\projects\LT_data_analysis"
source_file = os.path.join(base_dir, "raw_data", "LT_데이터집계_2024년_8월_GR1_251103.xlsx")
sheet_name = '문항난이도별결과'

try:
    # Read header area
    df = pd.read_excel(source_file, sheet_name=sheet_name, header=None, nrows=10)
    print(df) 
except Exception as e:
    print(e)
