import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Set font for Korean support (malgun gothic for windows)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def create_stacked_bar_chart(df, grade_col, title, output_file):
    """
    Create stacked bar chart for grade distribution
    
    Args:
        df: DataFrame with 'Level' and grade_col columns
        grade_col: Column name for grades (e.g., 'Abs_Grade', 'Rel_Grade')
        title: Chart title
        output_file: Output PNG file path
    """
    levels_order = ['GT2', 'MGT2', 'S2', 'MAG2']
    grades_order = [9, 8, 7, 6, 5, 4, 3, 2, 1]  # 1등급이 맨 위 (역순)
    
    # Create pivot table: Rows=Grades, Cols=Levels
    pivot = df.pivot_table(index=grade_col, columns='Level', values='학번', aggfunc='count', fill_value=0)
    
    # Reindex to ensure all grades and levels are present
    pivot = pivot.reindex(index=grades_order, columns=levels_order, fill_value=0)
    
    # Prepare data for stacked bar chart
    # Each level will be a bar, and each grade will be a segment
    # We need to transpose so that levels are on x-axis
    data = pivot.T  # Transpose: rows=levels, cols=grades
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Color map for grades (1등급이 가장 진한 파란색)
    colors = plt.cm.Blues(np.linspace(0.3, 0.9, 9))  # 9등급부터 1등급까지
    colors_dict = {grade: colors[8-i] for i, grade in enumerate(grades_order)}  # i: 0-8, so 8-i: 8-0
    
    # Create stacked bars
    bottom = np.zeros(len(levels_order))
    bars_list = []
    
    for grade in grades_order:
        values = data[grade].values
        bars = ax.bar(levels_order, values, bottom=bottom, 
                     label=f'{grade}등급', color=colors_dict[grade],
                     edgecolor='white', linewidth=1.5)
        bars_list.append(bars)
        bottom += values
    
    # Customize chart
    ax.set_xlabel('레벨 (Level)', fontsize=14, fontweight='bold')
    ax.set_ylabel('학생 수 (Number of Students)', fontsize=14, fontweight='bold')
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    
    # Set y-axis limits
    ax.set_ylim(0, bottom.max() * 1.05)
    
    # Add grid
    ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # Create legend (reverse order so 1등급 is first)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(reversed(handles), reversed(labels), 
             title='등급', bbox_to_anchor=(1.05, 1), loc='upper left',
             fontsize=10, title_fontsize=11)
    
    # Add value labels on bars (optional, can be commented out if too cluttered)
    # for bars in bars_list:
    #     for bar in bars:
    #         height = bar.get_height()
    #         if height > 0:
    #             ax.text(bar.get_x() + bar.get_width()/2., bar.get_y() + height/2,
    #                    f'{int(height)}', ha='center', va='center', 
    #                    fontsize=8, fontweight='bold', color='white')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Saved {output_file}")
    plt.close()

def main():
    file_path = "integrated_grades_detail.csv"
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found. Please run analyze_integrated_grades.py first.")
        return
    
    df = pd.read_csv(file_path)
    
    # Create stacked bar chart for absolute evaluation
    create_stacked_bar_chart(
        df, 
        'Abs_Grade',
        '절대평가 등급 분포 (Absolute Evaluation Grade Distribution)',
        'grade_distribution_stacked_bar_absolute.png'
    )
    
    # Create stacked bar chart for relative evaluation
    create_stacked_bar_chart(
        df,
        'Rel_Grade',
        '상대평가 등급 분포 (Relative Evaluation Grade Distribution)',
        'grade_distribution_stacked_bar_relative.png'
    )
    
    # Also create the combined file name requested
    create_stacked_bar_chart(
        df,
        'Abs_Grade',
        '절대평가 등급 분포 (Absolute Evaluation Grade Distribution)',
        'grade_distribution_stacked_bar.png'
    )

if __name__ == "__main__":
    main()

