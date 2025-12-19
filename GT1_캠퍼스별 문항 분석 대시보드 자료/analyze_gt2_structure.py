import pandas as pd

try:
    df = pd.read_csv('2025_10월_data/2025_10월_MT.csv')
    print("Columns:", df.columns)
    print("Levels:", df['레벨'].unique())
    print("Subjects:", df['시험과목'].unique())
    
    for subject in df['시험과목'].unique():
        subset = df[df['시험과목'] == subject]
        max_q = subset['문항 순번'].max()
        print(f"Subject: {subject}, Max Question: {max_q}")
        
except Exception as e:
    print(e)
