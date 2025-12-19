import pandas as pd
import os

# Define paths
base_dir = r"c:\Users\user\projects\LT_data_analysis"
source_file = os.path.join(base_dir, "raw_data", "MT_문항데이터_2025년_10월_Gr2.xlsx")
dest_dir = os.path.join(base_dir, "2025_10월_data")
dest_file = os.path.join(dest_dir, "2025_10월_MT.csv")

# Sheet name
sheet_name = 'GT2'

def convert_excel_to_csv():
    print(f"Reading {source_file}...")
    
    try:
        # Use header=0 as verified
        df = pd.read_excel(source_file, sheet_name=sheet_name, header=0)
    except Exception as e:
        print(f"Error reading excel: {e}")
        return

    print("Columns found:", list(df.columns))
    
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        
    print(f"Saving to {dest_file}...")
    df.to_csv(dest_file, index=False, encoding='utf-8-sig')
    print("Done.")

if __name__ == "__main__":
    convert_excel_to_csv()
