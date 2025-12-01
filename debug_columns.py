import pandas as pd

file_path = 'data/2024_5월_문항난이도별결과.csv'
with open(file_path, 'rb') as f:
    header = f.read(100)
    print(f"Header bytes: {header}")
    try:
        print(f"Decoded cp949: {header.decode('cp949')}")
    except:
        print("cp949 decode failed")
    try:
        print(f"Decoded utf-8: {header.decode('utf-8')}")
    except:
        print("utf-8 decode failed")
    try:
        print(f"Decoded euc-kr: {header.decode('euc-kr')}")
    except:
        print("euc-kr decode failed")
    
    import chardet
    result = chardet.detect(header)
    print(f"Chardet result: {result}")

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())

# Check if '전체정답' is in columns
target_col = '전체정답'
if target_col in df.columns:
    print(f"\n'{target_col}' found in columns.")
else:
    print(f"\n'{target_col}' NOT found in columns.")
    # Print hex representation of columns to see hidden characters
    for col in df.columns:
        print(f"Column: {col}, Hex: {col.encode('utf-8').hex()}")
