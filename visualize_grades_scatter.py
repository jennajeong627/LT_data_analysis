import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Set font for Korean support
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def main():
    file_path = "integrated_grades_detail.csv"
    if not os.path.exists(file_path):
        print("Data file not found.")
        return

    df = pd.read_csv(file_path)
    levels_order = ['GT2', 'MGT2', 'S2', 'MAG2']
    
    # Define Grade Cutoffs for Plotting
    abs_cuts = [
        (54, '1등급'), (48, '2등급'), (42, '3등급'), (36, '4등급'), 
        (30, '5등급'), (24, '6등급'), (18, '7등급'), (12, '8등급'), (0, '9등급')
    ]
    # For filling colors, we need boundaries.
    # 60-54, 54-48, ...
    abs_bounds = [60, 54, 48, 42, 36, 30, 24, 18, 12, 0]
    
    rel_cuts = [4, 11, 23, 40, 60, 77, 89, 96, 100]
    rel_labels = ['1등급', '2등급', '3등급', '4등급', '5등급', '6등급', '7등급', '8등급', '9등급']
    
    # --- 1. Absolute Evaluation Scatter (Score vs Level) ---
    plt.figure(figsize=(12, 10))
    
    # Draw Background Bands for Grades
    colors = sns.color_palette("Greys", n_colors=9)[::-1] # Lighter for higher grades? Or alternating.
    # Let's use alternating subtle colors or just lines. 
    # To show "closeness", lines are better than heavy fills, but fills help identify grade easily.
    # Let's use very light fills.
    
    for i in range(len(abs_bounds)-1):
        upper = abs_bounds[i]
        lower = abs_bounds[i+1]
        grade_num = i + 1
        plt.axhspan(lower, upper, color=f'C{i%9}', alpha=0.1)
        plt.text(3.6, (lower+upper)/2, f'{grade_num}등급', va='center', ha='left', fontsize=12, fontweight='bold', color='gray')
        
    sns.stripplot(data=df, x='Level', y='Score', order=levels_order, 
                  jitter=0.3, alpha=0.6, s=4, palette='viridis')

    # Draw Cutoff Lines
    for score, label in abs_cuts:
        if score > 0:
            plt.axhline(y=score, color='red', linestyle='--', linewidth=1, alpha=0.5)
            plt.text(-0.45, score, f'{score}점', color='red', va='center', fontsize=10, fontweight='bold')

    plt.title('절대평가: 레벨별 점수 분포 및 등급 컷 (Absolute Evaluation)', fontsize=16)
    plt.ylabel('점수 (Score)', fontsize=14)
    plt.xlabel('레벨 (Level)', fontsize=14)
    plt.ylim(0, 62) # Give some space
    plt.yticks(list(range(0, 61, 6)))
    
    plt.savefig("absolute_score_scatter.png", dpi=120)
    plt.close()
    
    # --- 2. Relative Evaluation Scatter (Percentile vs Level) ---
    plt.figure(figsize=(12, 10))
    
    # Use 'Rank Percentile' for plotting. 
    # Note: low percentile is high rank. So we usually invert Y or plot "Top N%".
    # Let's plot Percentile (0 to 100) and invert Y axis.
    
    # Draw Background Bands for Grades (Relative)
    prev_cut = 0
    for i, cut in enumerate(rel_cuts):
        grade_num = i + 1
        plt.axhspan(prev_cut, cut, color=f'C{i%9}', alpha=0.1)
        
        # Position label
        mid_point = (prev_cut + cut) / 2
        # Special adjustment for wide bands (grade 9 is tiny? no, 96-100)
        plt.text(3.6, mid_point, f'{grade_num}등급', va='center', ha='left', fontsize=12, fontweight='bold', color='gray')
        
        # Line
        plt.axhline(y=cut, color='red', linestyle='--', linewidth=1, alpha=0.5)
        if cut < 100:
             plt.text(-0.45, cut, f'{cut}%', color='red', va='center', fontsize=10, fontweight='bold')
        
        prev_cut = cut
        
    sns.stripplot(data=df, x='Level', y='Percentile', order=levels_order, 
                  jitter=0.3, alpha=0.6, s=4, palette='viridis')

    plt.ylim(100, 0) # Invert axis: Top 1% at top
    plt.title('상대평가: 레벨별 석차 백분율 분포 (Relative Evaluation)', fontsize=16)
    plt.ylabel('상위 백분율 (Top %)', fontsize=14)
    plt.xlabel('레벨 (Level)', fontsize=14)
    
    plt.savefig("relative_percentile_scatter.png", dpi=120)
    plt.close()
    
    print("Graphs saved: absolute_score_scatter.png, relative_percentile_scatter.png")

if __name__ == "__main__":
    main()
