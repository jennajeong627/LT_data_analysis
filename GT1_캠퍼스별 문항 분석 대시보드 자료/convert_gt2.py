
import pandas as pd
import os

# Define file paths
input_file = r'c:\Users\user\projects\LT_data_analysis\raw_data\LT_문항데이터_2025년_11월_Gr2.xlsx'
output_dir = r'c:\Users\user\projects\LT_data_analysis\raw_data'
output_file = os.path.join(output_dir, 'LT_문항데이터_2025년_11월_Gr2_GT2.csv')

# Read Excel file
try:
    # Load specific sheet 'GT2'
    df = pd.read_excel(input_file, sheet_name='GT2')
    
    # Save to CSV
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"Successfully created CSV: {output_file}")
    
except Exception as e:
    print(f"Error converting file: {e}")
