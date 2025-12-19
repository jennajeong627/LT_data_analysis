import pandas as pd
import os

def convert_excel_sheets_to_csv():
    # Define file paths
    # Using absolute paths as per instructions
    input_file = r'c:\Users\user\projects\LT_data_analysis\raw_data\2025년_11월_Gr2_LT_문항데이터_v3.xlsx'
    output_dir = r'c:\Users\user\projects\LT_data_analysis\2025_LT_11월_data'

    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    try:
        print(f"Reading Excel file: {input_file}")
        # Read the Excel file
        xls = pd.ExcelFile(input_file)

        # Iterate through each sheet
        for sheet_name in xls.sheet_names:
            print(f"Processing sheet: {sheet_name}")
            
            # Read the sheet into a DataFrame
            df = pd.read_excel(xls, sheet_name=sheet_name)
            
            # Construct the output CSV filename
            # Naming convention: 2025_11월_[SheetName].csv
            output_filename = f'2025_11월_{sheet_name}.csv'
            output_path = os.path.join(output_dir, output_filename)
            
            # Save to CSV
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"Saved {output_filename} to {output_dir}")
            
        print("All sheets converted successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    convert_excel_sheets_to_csv()
