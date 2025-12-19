import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set font for Korean support (malgun gothic for windows)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def main():
    file_path = "integrated_grades_detail.csv"
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found. Please run analyze_integrated_grades.py first.")
        return

    df = pd.read_csv(file_path)
    
    levels_order = ['GT2', 'MGT2', 'S2', 'MAG2']
    
    # 1. Absolute Evaluation Heatmap
    plt.figure(figsize=(10, 8))
    
    # Create pivot table: Rows=Abs_Grade, Cols=Level, Values=Count
    abs_pivot = df.pivot_table(index='Abs_Grade', columns='Level', values='학번', aggfunc='count', fill_value=0)
    
    # Reindex to ensure all grades 1-9 and all levels are present
    abs_pivot = abs_pivot.reindex(index=range(1, 10), columns=levels_order, fill_value=0)
    
    sns.heatmap(abs_pivot, annot=True, fmt='d', cmap='Blues', linewidths=.5, cbar_kws={'label': '학생 수'})
    plt.title('절대평가 등급 분포 (Absolute Evaluation)', fontsize=16)
    plt.ylabel('등급 (Grade)', fontsize=12)
    plt.xlabel('레벨 (Level)', fontsize=12)
    plt.yticks(rotation=0)
    
    output_abs = "absolute_grade_distribution.png"
    plt.savefig(output_abs, dpi=100)
    print(f"Saved {output_abs}")
    plt.close()

    # 2. Relative Evaluation Heatmap
    plt.figure(figsize=(10, 8))
    
    rel_pivot = df.pivot_table(index='Rel_Grade', columns='Level', values='학번', aggfunc='count', fill_value=0)
    rel_pivot = rel_pivot.reindex(index=range(1, 10), columns=levels_order, fill_value=0)
    
    sns.heatmap(rel_pivot, annot=True, fmt='d', cmap='Greens', linewidths=.5, cbar_kws={'label': '학생 수'})
    plt.title('상대평가 등급 분포 (Relative Evaluation)', fontsize=16)
    plt.ylabel('등급 (Grade)', fontsize=12)
    plt.xlabel('레벨 (Level)', fontsize=12)
    plt.yticks(rotation=0)
    
    output_rel = "relative_grade_distribution.png"
    plt.savefig(output_rel, dpi=100)
    print(f"Saved {output_rel}")
    plt.close()

if __name__ == "__main__":
    main()
