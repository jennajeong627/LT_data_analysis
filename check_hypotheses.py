import pandas as pd
import numpy as np
import os
import glob

def count_stars(star_str):
    if pd.isna(star_str):
        return 0
    return str(star_str).count('★')

def load_data():
    base_dir = r"c:\Users\user\projects\LT_data_analysis\2025_LT_11월_data"
    files = {
        'GT2': os.path.join(base_dir, "2025_11월_GT2.csv"),
        'MGT2': os.path.join(base_dir, "2025_11월_MGT2.csv"),
        'S2': os.path.join(base_dir, "2025_11월_S2.csv"),
        'MAG2': os.path.join(base_dir, "2025_11월_MAG2.csv")
    }
    
    all_data = []
    for level, fpath in files.items():
        if os.path.exists(fpath):
            df = pd.read_csv(fpath)
            df['Level'] = level
            all_data.append(df)
            
    if not all_data:
        return None
    
    full_df = pd.concat(all_data, ignore_index=True)
    
    # Preprocessing
    # Difficulty
    full_df['Difficulty'] = full_df['문항난이도'].apply(count_stars)
    # Correctness (Y/N -> 1/0)
    full_df['IsCorrect'] = full_df['정답여부'].apply(lambda x: 1 if x == 'Y' else 0)
    
    return full_df

def analyze_part1_reality(df, student_stats):
    print("\n--- [Part 1] Reality Check Metrics by Level ---")
    
    levels = ['GT2', 'MGT2', 'S2', 'MAG2']
    
    # 1. 1 Point Weight (Density)
    # Measure: % of students in the mode score(s). Or Std Dev.
    # Higher density means 1 point changes rank more.
    print(f"{'Level':<6} | {'StdDev':<8} | {'Mode %':<8} | {'Abs 1-2 Gap':<12}")
    for lvl in levels:
        s = student_stats[student_stats['Level'] == lvl]['Score']
        if len(s) == 0: continue
        
        std = s.std()
        mode_counts = s.value_counts()
        if not mode_counts.empty:
            max_mode_pct = (mode_counts.iloc[0] / len(s)) * 100
        else:
            max_mode_pct = 0
            
        print(f"{lvl:<6} | {std:<8.2f} | {max_mode_pct:<8.1f}% |")

    # 3. Level Reversal
    # Compare MGT2 Top 10% mean vs S2 Bottom 20% mean
    mgt2_scores = student_stats[student_stats['Level'] == 'MGT2']['Score']
    s2_scores = student_stats[student_stats['Level'] == 'S2']['Score']
    
    if not mgt2_scores.empty and not s2_scores.empty:
        mgt2_top10 = mgt2_scores.quantile(0.90)
        mgt2_top10_mean = mgt2_scores[mgt2_scores >= mgt2_top10].mean()
        
        s2_bot20 = s2_scores.quantile(0.20)
        s2_bot20_mean = s2_scores[s2_scores <= s2_bot20].mean()
        
        print(f"\n[Level Reversal Check]")
        print(f"MGT2 Top 10% Cut: {mgt2_top10} (Mean: {mgt2_top10_mean:.2f})")
        print(f"S2 Bottom 20% Cut: {s2_bot20} (Mean: {s2_bot20_mean:.2f})")
        print(f"Reversal Exists: {mgt2_top10_mean > s2_bot20_mean}")

def analyze_part2_diagnosis(df, student_stats):
    print("\n--- [Part 2] Diagnosis Metrics by Level ---")
    levels = ['GT2', 'MGT2', 'S2', 'MAG2']
    
    # 2. Late Slump (Endurance)
    # Compare Q1-10 acc vs Q11-20 acc
    # 4. Ignore Difficulty (Guessing)
    # Compare Easy (1-2) vs Hard (4-5) acc
    
    print(f"{'Level':<6} | {'Acc Q1-10':<10} | {'Acc Q11-20':<10} | {'Drop':<6} | {'Acc Easy':<8} | {'Acc Hard':<8} | {'Gap':<6}")
    
    for lvl in levels:
        sub_df = df[df['Level'] == lvl]
        if sub_df.empty: continue
        
        q1_10 = sub_df[sub_df['문항 순번'] <= 10]['IsCorrect'].mean() * 100
        q11_20 = sub_df[sub_df['문항 순번'] > 10]['IsCorrect'].mean() * 100
        drop = q1_10 - q11_20
        
        easy = sub_df[sub_df['Difficulty'].isin([1, 2])]['IsCorrect'].mean() * 100
        hard = sub_df[sub_df['Difficulty'].isin([4, 5])]['IsCorrect'].mean() * 100
        diff_gap = easy - hard
        
        print(f"{lvl:<6} | {q1_10:<10.1f} | {q11_20:<10.1f} | {drop:<6.1f} | {easy:<8.1f} | {hard:<8.1f} | {diff_gap:<6.1f}")

def analyze_part3_potential(df, student_stats):
    print("\n--- [Part 3] Potential Metrics by Level ---")
    levels = ['GT2', 'MGT2', 'S2', 'MAG2']
    
    # 3. Quantum Jump (Borderline Students)
    # Count students in range [51, 53] (Near 54), [45, 47] (Near 48), [39, 41] (Near 42)
    # Let's verify % of students within 3 points below next grade cut.
    # Target Cuts: 54, 48, 42, 36
    
    cuts = [54, 48, 42, 36]
    
    print(f"{'Level':<6} | {'Near 1G(51-53)':<14} | {'Near 2G(45-47)':<14} | {'Near 3G(39-41)':<14}")
    
    for lvl in levels:
        s = student_stats[student_stats['Level'] == lvl]['Score']
        total = len(s)
        if total == 0: continue
        
        n_1g = len(s[(s >= 51) & (s <= 53)])
        n_2g = len(s[(s >= 45) & (s <= 47)])
        n_3g = len(s[(s >= 39) & (s <= 41)])
        
        pct_1g = (n_1g / total) * 100
        pct_2g = (n_2g / total) * 100
        pct_3g = (n_3g / total) * 100
        
        print(f"{lvl:<6} | {pct_1g:<5.1f}% ({n_1g})   | {pct_2g:<5.1f}% ({n_2g})   | {pct_3g:<5.1f}% ({n_3g})")

def main():
    raw_df = load_data()
    if raw_df is None:
        print("No data loaded.")
        return
        
    # Calculate Scores per student
    # Group by Level, ID
    # Note: '문항 순번' is unique per test, sum IsCorrect = Score
    student_stats = raw_df.groupby(['Level', '학번', '이름'])['IsCorrect'].sum().reset_index(name='Score')
    
    analyze_part1_reality(raw_df, student_stats)
    analyze_part2_diagnosis(raw_df, student_stats)
    analyze_part3_potential(raw_df, student_stats)

if __name__ == "__main__":
    main()
