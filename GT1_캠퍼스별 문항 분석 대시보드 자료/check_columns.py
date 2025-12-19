import pandas as pd
import os

base_dir = r"c:\Users\user\projects\LT_data_analysis"
source_file = os.path.join(base_dir, "raw_data", "LT_데이터집계_2024년_8월_GR1_251103.xlsx")
sheet_name = '학생문항별결과'

df = pd.read_excel(source_file, sheet_name=sheet_name, header=0, nrows=0)
print(list(df.columns))

# Save columns to a file to view encoding
with open("columns.txt", "w", encoding="utf-8") as f:
    f.write(",".join(df.columns))
