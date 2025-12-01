import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
import matplotlib.font_manager as fm
import os

# Set font for Korean characters
def set_korean_font():
    font_path = 'C:/Windows/Fonts/malgun.ttf'
    if os.path.exists(font_path):
        font_name = fm.FontProperties(fname=font_path).get_name()
        plt.rc('font', family=font_name)
    else:
        plt.rc('font', family='Malgun Gothic')
    plt.rcParams['axes.unicode_minus'] = False

set_korean_font()

# Load data
file_path = 'data/2024_5월_문항난이도별결과.csv'
df = pd.read_csv(file_path, encoding='utf-8-sig')

# Filter for relevant levels
target_levels = ['GT1', 'MGT1', 'S1', 'MAG1']
df_filtered = df[df['레벨'].isin(target_levels)].copy()

# Define classification functions for each standard
def classify_standard_a(score):
    if 0 <= score <= 6: return 'below2'
    elif 7 <= score <= 11: return 'below1'
    elif 12 <= score <= 15: return 'on'
    elif 16 <= score <= 17: return 'above1'
    elif 18 <= score <= 20: return 'above2'
    else: return 'unknown'

def classify_standard_b(score):
    if 0 <= score <= 9: return 'below2'
    elif 10 <= score <= 11: return 'below1'
    elif 12 <= score <= 15: return 'on'
    elif 16 <= score <= 17: return 'above1'
    elif 18 <= score <= 20: return 'above2'
    else: return 'unknown'

def classify_standard_c(score):
    if 0 <= score <= 6: return 'below2'
    elif 7 <= score <= 11: return 'below1'
    elif 12 <= score <= 15: return 'on'
    elif 16 <= score <= 17: return 'above1'
    elif 18 <= score <= 20: return 'above2'
    else: return 'unknown'

# Calculate stats for all standards
standards = {
    'Standard A': {'func': classify_standard_a, 'boundaries': [6.5, 11.5, 15.5, 17.5]},
    'Standard B': {'func': classify_standard_b, 'boundaries': [9.5, 11.5, 15.5, 17.5]},
    'Standard C': {'func': classify_standard_c, 'boundaries': [6.5, 11.5, 15.5, 17.5]}
}

segment_order = ['below2', 'below1', 'on', 'above1', 'above2']
colors = {'GT1': 'red', 'MGT1': 'dodgerblue', 'S1': 'lime', 'MAG1': 'orange'}

# Create figure with 3 columns (one for each standard)
fig = plt.figure(figsize=(20, 14))
gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)

for col, (std_name, std_info) in enumerate(standards.items()):
    # Classify students
    df_filtered['segment'] = df_filtered['전체 정답 수'].apply(std_info['func'])
    
    # Calculate stats
    level_stats = {}
    for level in target_levels:
        scores = df_filtered[df_filtered['레벨'] == level]['전체 정답 수']
        level_stats[level] = {
            'mean': scores.mean(),
            'std': scores.std(),
            'count': len(scores)
        }
    
    # Prepare segment counts
    segment_counts = df_filtered.groupby(['레벨', 'segment']).size().unstack(fill_value=0)
    segment_counts = segment_counts.reindex(columns=segment_order, fill_value=0)
    
    # Plot 1: Normal Distribution
    ax1 = fig.add_subplot(gs[0, col])
    x = np.linspace(0, 20, 1000)
    
    for level in target_levels:
        stats = level_stats[level]
        y = norm.pdf(x, stats['mean'], stats['std'])
        ax1.plot(x, y, label=fr"{level} ($\mu={stats['mean']:.2f}$)", 
                color=colors[level], alpha=0.6, linewidth=2)
        ax1.fill_between(x, y, color=colors[level], alpha=0.2)
    
    # Add boundaries
    for b in std_info['boundaries']:
        ax1.axvline(b, color='gray', linestyle='--', alpha=0.5)
    
    ax1.set_title(f'{std_name}\n레벨별 점수 정규분포', fontsize=12, fontweight='bold')
    ax1.set_xlabel('전체 정답 수 (점수)', fontsize=10)
    ax1.set_ylabel('확률 밀도', fontsize=10)
    ax1.set_xlim(0, 20)
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Bar Chart
    ax2 = fig.add_subplot(gs[1, col])
    width = 0.2
    x_indices = np.arange(len(segment_order))
    
    for i, level in enumerate(target_levels):
        counts = segment_counts.loc[level] if level in segment_counts.index else [0]*5
        bars = ax2.bar(x_indices + (i - 1.5) * width, counts, width, 
                      label=level, color=colors[level], alpha=0.6)
        
        # Add count labels
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}',
                        ha='center', va='bottom', fontsize=8)
    
    ax2.set_title(f'{std_name}\n레벨별 구간 분류 학생 수', fontsize=12, fontweight='bold')
    ax2.set_xlabel('구간 분류', fontsize=10)
    ax2.set_ylabel('학생 수', fontsize=10)
    ax2.set_xticks(x_indices)
    ax2.set_xticklabels(segment_order, fontsize=9)
    ax2.legend(title='레벨', fontsize=9)
    ax2.grid(True, axis='y', alpha=0.3)

plt.suptitle('2024년 5월 레벨별 학생 성적 분석 비교 (Standard A, B, C)', 
             fontsize=16, fontweight='bold', y=0.98)
plt.savefig('standard_ABC_comparison.png', dpi=300, bbox_inches='tight')
print("Comparison image saved as 'standard_ABC_comparison.png'")
