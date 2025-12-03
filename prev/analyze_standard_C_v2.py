import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy.stats import norm
import matplotlib.font_manager as fm
import os

# Set font for Korean characters
def set_korean_font():
    font_path = 'C:/Windows/Fonts/malgun.ttf'  # For Windows
    if os.path.exists(font_path):
        font_name = fm.FontProperties(fname=font_path).get_name()
        plt.rc('font', family=font_name)
    else:
        plt.rc('font', family='Malgun Gothic') # Fallback
    plt.rcParams['axes.unicode_minus'] = False

set_korean_font()

# Load data
file_path = 'data/2024_5월_문항난이도별결과.csv'
df = pd.read_csv(file_path, encoding='utf-8-sig')

# Filter for relevant levels
target_levels = ['GT1', 'MGT1', 'S1', 'MAG1']
df_filtered = df[df['레벨'].isin(target_levels)].copy()

# Define score ranges based on standard_test_C.md
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

# Use correct column name '전체 정답 수'
df_filtered['segment'] = df_filtered['전체 정답 수'].apply(classify_segment)

# Calculate stats for normal distribution
level_stats = {}
for level in target_levels:
    scores = df_filtered[df_filtered['레벨'] == level]['전체 정답 수']
    mean = scores.mean()
    std = scores.std()
    level_stats[level] = {'mean': mean, 'std': std, 'count': len(scores)}

# Prepare data for bar chart
segment_order = ['below2', 'below1', 'on', 'above1', 'above2']
segment_counts = df_filtered.groupby(['레벨', 'segment']).size().unstack(fill_value=0)
segment_counts = segment_counts.reindex(columns=segment_order, fill_value=0)

# Plotting
fig, axes = plt.subplots(2, 1, figsize=(14, 12))

# 1. Normal Distribution Plot
ax1 = axes[0]
x = np.linspace(0, 20, 1000)
colors = {'GT1': 'red', 'MGT1': 'dodgerblue', 'S1': 'lime', 'MAG1': 'orange'}

for level in target_levels:
    stats = level_stats[level]
    y = norm.pdf(x, stats['mean'], stats['std'])
    ax1.plot(x, y, label=fr"{level} ($\mu={stats['mean']:.2f}, \sigma={stats['std']:.2f}$)", color=colors[level], alpha=0.6)
    ax1.fill_between(x, y, color=colors[level], alpha=0.2)

# Add vertical lines for segment boundaries
boundaries = [6.5, 11.5, 15.5, 17.5] # Approximate boundaries for visual separation
for b in boundaries:
    ax1.axvline(b, color='gray', linestyle='--', alpha=0.5)

ax1.set_title('레벨별 점수 정규분포 비교 (Standard C)')
ax1.set_xlabel('전체 정답 수 (점수)')
ax1.set_ylabel('확률 밀도')
ax1.set_xlim(0, 20)
ax1.legend()
ax1.grid(True, alpha=0.3)

# 2. Bar Chart
ax2 = axes[1]
width = 0.2
x_indices = np.arange(len(segment_order))

for i, level in enumerate(target_levels):
    counts = segment_counts.loc[level] if level in segment_counts.index else [0]*5
    bars = ax2.bar(x_indices + (i - 1.5) * width, counts, width, label=level, color=colors[level], alpha=0.6)
    
    # Add count labels
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=9)

ax2.set_title('레벨별 구간 분류 학생 수 (Standard C)')
ax2.set_xlabel('구간 분류')
ax2.set_ylabel('학생 수')
ax2.set_xticks(x_indices)
ax2.set_xticklabels(segment_order)
ax2.legend(title='레벨')
ax2.grid(True, axis='y', alpha=0.3)

plt.suptitle('2024년 5월 레벨별 학생 성적 분석 (Standard C)', fontsize=16)
plt.tight_layout()
plt.savefig('standard_C_analysis.png', dpi=300)
print("Analysis complete. Image saved as 'standard_C_analysis.png'.")

# Print counts for markdown update
print("\n--- Markdown Data ---")
print("| 레벨 | below2 | below1 | on | above1 | above2 | Total |")
print("|---|---|---|---|---|---|---|")
for level in target_levels:
    counts = segment_counts.loc[level] if level in segment_counts.index else pd.Series([0]*5, index=segment_order)
    total = counts.sum()
    print(f"| {level} | {counts['below2']} | {counts['below1']} | {counts['on']} | {counts['above1']} | {counts['above2']} | {total} |")
