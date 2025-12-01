import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import norm
import os

# Set font for Korean display
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def analyze_gt1_distribution():
    # Load data
    file_path = 'data/2024_5월_문항난이도별결과.csv'
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    df = pd.read_csv(file_path, encoding='utf-8-sig')
    
    # Filter for GT1 only
    target_level = 'GT1'
    df_filtered = df[df['레벨'] == target_level].copy()
    
    # Define score criteria (Standard A GPT)
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
    
    # Define segment order
    segment_order = ['below2', 'below1', 'on', 'above1', 'above2']
    df_filtered['segment'] = pd.Categorical(df_filtered['segment'], categories=segment_order, ordered=True)

    # Calculate counts
    segment_counts = df_filtered['segment'].value_counts().sort_index()
    print("Segment Counts for GT1:")
    print(segment_counts)
    
    # Calculate percentages
    segment_percentages = (segment_counts / len(df_filtered) * 100).round(1)
    print("\nSegment Percentages for GT1:")
    print(segment_percentages)

    # Visualization
    fig = plt.figure(figsize=(12, 10))
    plt.suptitle(f'2024년 5월 {target_level} 학생 성적 분석 (Standard A GPT)', fontsize=16, y=0.95)

    # 1. Normal Distribution
    ax1 = plt.subplot(2, 1, 1)
    color = '#ff9999' # GT1 color
    
    x = np.linspace(0, 20, 1000)
    mu, std = norm.fit(df_filtered['전체 정답 수'])
    p = norm.pdf(x, mu, std)
    
    ax1.plot(x, p, label=f'{target_level} (μ={mu:.2f}, σ={std:.2f})', linewidth=2, color=color)
    ax1.fill_between(x, p, alpha=0.3, color=color)
    
    # Add vertical lines for segment boundaries
    # 0-6 | 7-11 | 12-15 | 16-17 | 18-20
    # Boundaries: 6.5, 11.5, 15.5, 17.5
    boundaries = [6.5, 11.5, 15.5, 17.5]
    for b in boundaries:
        ax1.axvline(x=b, color='gray', linestyle='--', alpha=0.5)
        
    # Annotate segments
    y_max = max(p)
    ax1.text(3, y_max*0.5, 'below2', ha='center', color='gray')
    ax1.text(9, y_max*0.5, 'below1', ha='center', color='gray')
    ax1.text(13.5, y_max*0.5, 'on', ha='center', color='gray')
    ax1.text(16.5, y_max*0.5, 'ab1', ha='center', color='gray')
    ax1.text(19, y_max*0.5, 'ab2', ha='center', color='gray')

    ax1.set_title('점수 정규분포', fontsize=14)
    ax1.set_xlabel('전체 정답 수 (점수)', fontsize=12)
    ax1.set_ylabel('확률 밀도', fontsize=12)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, 20)

    # 2. Segment Counts Bar Chart
    ax2 = plt.subplot(2, 1, 2)
    sns.barplot(x=segment_counts.index, y=segment_counts.values, palette=[color]*5, ax=ax2)
    
    # Add value labels
    for container in ax2.containers:
        ax2.bar_label(container)
        
    ax2.set_title('구간별 학생 수', fontsize=14)
    ax2.set_xlabel('구간 분류', fontsize=12)
    ax2.set_ylabel('학생 수', fontsize=12)
    ax2.grid(True, axis='y', alpha=0.3)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig('gt1_distribution_analysis_A_GPT.png', dpi=300)
    print("\nAnalysis complete. Chart saved as 'gt1_distribution_analysis_A_GPT.png'")

if __name__ == "__main__":
    analyze_gt1_distribution()
