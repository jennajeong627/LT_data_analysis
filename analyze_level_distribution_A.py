import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import norm
import os

# Set font for Korean display
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def analyze_level_distribution():
    # Load data
    file_path = 'data/2024_5월_문항난이도별결과.csv'
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    df = pd.read_csv(file_path, encoding='utf-8-sig')
    
    # Filter for target levels
    target_levels = ['GT1', 'MGT1', 'S1', 'MAG1']
    df_filtered = df[df['레벨'].isin(target_levels)].copy()
    
    # Define score criteria (Standard A)
    # below2: 0~6
    # below1: 7~11
    # on: 12~15
    # above1: 16~17
    # above2: 18~20
    def classify_segment(score):
        if 0 <= score <= 6:
            return 'below2'
        elif 7 <= score <= 11:
            return 'below1'
        elif 12 <= score <= 15:
            return 'on'
        elif 16 <= score <= 17:
            return 'above1'
        elif 18 <= score <= 20:
            return 'above2'
        else:
            return 'unknown'

    # Apply classification
    df_filtered['segment'] = df_filtered['전체 정답 수'].apply(classify_segment)
    
    # Define segment order for sorting
    segment_order = ['below2', 'below1', 'on', 'above1', 'above2']
    df_filtered['segment'] = pd.Categorical(df_filtered['segment'], categories=segment_order, ordered=True)

    # Calculate counts per level and segment
    segment_counts = df_filtered.groupby(['레벨', 'segment'], observed=False).size().unstack(fill_value=0)
    print("Segment Counts per Level (Standard A):")
    print(segment_counts)
    
    # Calculate percentages
    segment_percentages = segment_counts.div(segment_counts.sum(axis=1), axis=0) * 100
    print("\nSegment Percentages per Level (Standard A):")
    print(segment_percentages.round(1))

    # Visualization
    fig = plt.figure(figsize=(20, 15))
    plt.suptitle('2024년 5월 레벨별 학생 성적 분석 (Standard A)', fontsize=20, y=0.95)

    # 1. Normal Distribution Comparison
    ax1 = plt.subplot(2, 1, 1)
    colors = {'GT1': '#ff9999', 'MGT1': '#66b3ff', 'S1': '#99ff99', 'MAG1': '#ffcc99'}
    
    x = np.linspace(0, 20, 1000)
    
    for level in target_levels:
        subset = df_filtered[df_filtered['레벨'] == level]
        if len(subset) > 1:
            mu, std = norm.fit(subset['전체 정답 수'])
            p = norm.pdf(x, mu, std)
            ax1.plot(x, p, label=f'{level} (μ={mu:.2f}, σ={std:.2f})', linewidth=2, color=colors.get(level, 'gray'))
            ax1.fill_between(x, p, alpha=0.3, color=colors.get(level, 'gray'))
    
    # Add vertical lines for segment boundaries
    # 0-6 | 7-11 | 12-15 | 16-17 | 18-20
    # Boundaries at: 6.5, 11.5, 15.5, 17.5
    boundaries = [6.5, 11.5, 15.5, 17.5]
    
    for b in boundaries:
        ax1.axvline(x=b, color='gray', linestyle='--', alpha=0.5)
        
    ax1.set_title('레벨별 점수 정규분포 비교', fontsize=15)
    ax1.set_xlabel('전체 정답 수 (점수)', fontsize=12)
    ax1.set_ylabel('확률 밀도', fontsize=12)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, 20)

    # 2. Segment Counts Bar Chart
    ax2 = plt.subplot(2, 1, 2)
    
    # Prepare data for plotting
    counts_melted = segment_counts.reset_index().melt(id_vars='레벨', var_name='segment', value_name='count')
    
    # Plot
    sns.barplot(data=counts_melted, x='segment', y='count', hue='레벨', hue_order=target_levels, palette=colors, ax=ax2)
    
    # Add value labels
    for container in ax2.containers:
        ax2.bar_label(container)
        
    ax2.set_title('레벨별 구간 분류 학생 수', fontsize=15)
    ax2.set_xlabel('구간 분류', fontsize=12)
    ax2.set_ylabel('학생 수', fontsize=12)
    ax2.grid(True, axis='y', alpha=0.3)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig('level_distribution_analysis_A.png', dpi=300)
    print("\nAnalysis complete. Chart saved as 'level_distribution_analysis_A.png'")

if __name__ == "__main__":
    analyze_level_distribution()
