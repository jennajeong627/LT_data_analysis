import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import os

# Set Korean font
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# Output directory
output_dir = r'C:\Users\user\.gemini\antigravity\brain\8fd772ef-33d9-4495-9894-ecaf33833f42'
os.makedirs(output_dir, exist_ok=True)

print("=" * 80)
print("GT1 Normal Distribution Analysis - A안 절대평가 기준")
print("=" * 80)

# Load data
print("\n[1] Loading data...")
df = pd.read_csv('data/2024_5월_문항난이도별결과.csv', encoding='utf-8-sig')

# Get GT1 students
df_students = df.groupby(['레벨', '학생명'])['정답 수'].sum().reset_index()
df_students.columns = ['레벨', '학생명', '전체 정답 수']
df_gt1 = df_students[df_students['레벨'] == 'GT1'].copy()

total_students = len(df_gt1)
scores = df_gt1['전체 정답 수'].values

print(f"   Total GT1 students: {total_students:,}")
print(f"   Mean: {scores.mean():.2f}")
print(f"   Std Dev: {scores.std():.2f}")

# A안 절대평가 기준점
criteria_a = {
    'below2': (0, 6, '기초 부족'),
    'below1': (7, 11, '기초는 있으나 불안정'),
    'on': (12, 15, '교육과정 기준 충족'),
    'above1': (16, 17, '상위 수준 진입 가능'),
    'above2': (18, 20, '매우 우수')
}

# ============================================================================
# VISUALIZATION: Normal Distribution with Segments
# ============================================================================
print("\n" + "=" * 80)
print("Creating Normal Distribution Visualization")
print("=" * 80)

fig, ax = plt.subplots(figsize=(16, 9))

# Create histogram
n, bins, patches = ax.hist(scores, bins=range(0, 22), density=True, 
                           alpha=0.6, color='steelblue', edgecolor='black', 
                           linewidth=1.2, label='실제 분포')

# Fit normal distribution
mu, sigma = scores.mean(), scores.std()
x = np.linspace(0, 20, 1000)
normal_curve = stats.norm.pdf(x, mu, sigma)

# Plot normal curve
ax.plot(x, normal_curve, 'r-', linewidth=3, label=f'정규분포 곡선\n(μ={mu:.2f}, σ={sigma:.2f})')

# Color histogram bars by segment
segment_colors = {
    'below2': '#e53e3e',
    'below1': '#ed8936',
    'on': '#48bb78',
    'above1': '#38a169',
    'above2': '#2f855a'
}

for patch, left_edge in zip(patches, bins[:-1]):
    score = int(left_edge)
    for segment, (min_s, max_s, desc) in criteria_a.items():
        if min_s <= score <= max_s:
            patch.set_facecolor(segment_colors[segment])
            patch.set_alpha(0.7)
            break

# Add vertical lines for segment boundaries
boundaries = [6.5, 11.5, 15.5, 17.5]
boundary_labels = ['below2/below1', 'below1/on', 'on/above1', 'above1/above2']
boundary_colors = ['red', 'orange', 'green', 'blue']

for boundary, label, color in zip(boundaries, boundary_labels, boundary_colors):
    ax.axvline(x=boundary, color=color, linestyle='--', linewidth=2, alpha=0.7)
    # Add label at top
    y_pos = ax.get_ylim()[1] * 0.95
    ax.text(boundary, y_pos, label, rotation=90, va='top', ha='right',
            fontsize=9, color=color, fontweight='bold')

# Add mean and std dev lines
ax.axvline(x=mu, color='darkred', linestyle='-', linewidth=2.5, 
           label=f'평균 (μ={mu:.2f})', alpha=0.8)
ax.axvline(x=mu-sigma, color='purple', linestyle=':', linewidth=2, 
           label=f'μ-σ ({mu-sigma:.2f})', alpha=0.6)
ax.axvline(x=mu+sigma, color='purple', linestyle=':', linewidth=2, 
           label=f'μ+σ ({mu+sigma:.2f})', alpha=0.6)

# Labels and title
ax.set_xlabel('점수 (정답 수)', fontsize=13, fontweight='bold')
ax.set_ylabel('확률 밀도', fontsize=13, fontweight='bold')
ax.set_title('GT1 학생 점수 분포 - 정규분포 곡선 및 A안 절대평가 구간', 
             fontsize=15, fontweight='bold', pad=20)
ax.set_xlim(-0.5, 20.5)
ax.set_xticks(range(0, 21, 1))
ax.grid(True, alpha=0.3, linestyle='--')
ax.legend(loc='upper right', fontsize=10, framealpha=0.9)

# Add segment labels at bottom
y_bottom = ax.get_ylim()[0]
segment_positions = {
    'below2': 3,
    'below1': 9,
    'on': 13.5,
    'above1': 16.5,
    'above2': 19
}

for segment, x_pos in segment_positions.items():
    min_s, max_s, desc = criteria_a[segment]
    ax.text(x_pos, y_bottom - 0.005, f'{segment}\n({min_s}-{max_s}개)',
            ha='center', va='top', fontsize=9, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor=segment_colors[segment], 
                     alpha=0.7, edgecolor='black'))

plt.tight_layout()
viz1_path = os.path.join(output_dir, 'gt1_normal_distribution.png')
plt.savefig(viz1_path, dpi=150, bbox_inches='tight')
print(f"\n[OK] Saved: {viz1_path}")
plt.close()

# ============================================================================
# VISUALIZATION 2: Normal Distribution with Shaded Areas
# ============================================================================
fig, ax = plt.subplots(figsize=(16, 9))

# Plot normal curve
ax.plot(x, normal_curve, 'k-', linewidth=3, label='정규분포 곡선')

# Shade areas by segment
for segment, (min_s, max_s, desc) in criteria_a.items():
    x_segment = x[(x >= min_s) & (x <= max_s)]
    y_segment = stats.norm.pdf(x_segment, mu, sigma)
    ax.fill_between(x_segment, y_segment, alpha=0.5, 
                    color=segment_colors[segment], label=f'{segment} ({min_s}-{max_s}개)')

# Add actual data points as scatter
score_counts = df_gt1['전체 정답 수'].value_counts().sort_index()
for score, count in score_counts.items():
    density = count / total_students
    ax.scatter(score, density/2, s=count*2, alpha=0.6, color='darkblue', 
              edgecolors='black', linewidth=0.5, zorder=5)

# Add mean line
ax.axvline(x=mu, color='red', linestyle='-', linewidth=2.5, 
           label=f'평균 (μ={mu:.2f})', alpha=0.8)

# Add ±1σ, ±2σ lines
for i in range(1, 3):
    ax.axvline(x=mu-i*sigma, color='gray', linestyle=':', linewidth=1.5, alpha=0.5)
    ax.axvline(x=mu+i*sigma, color='gray', linestyle=':', linewidth=1.5, alpha=0.5)
    
    # Add labels
    if mu-i*sigma >= 0:
        ax.text(mu-i*sigma, ax.get_ylim()[1]*0.9, f'-{i}σ', 
               ha='center', fontsize=9, color='gray')
    if mu+i*sigma <= 20:
        ax.text(mu+i*sigma, ax.get_ylim()[1]*0.9, f'+{i}σ', 
               ha='center', fontsize=9, color='gray')

ax.set_xlabel('점수 (정답 수)', fontsize=13, fontweight='bold')
ax.set_ylabel('확률 밀도', fontsize=13, fontweight='bold')
ax.set_title('GT1 정규분포 곡선 - 구간별 음영 및 실제 데이터 포인트', 
             fontsize=15, fontweight='bold', pad=20)
ax.set_xlim(-0.5, 20.5)
ax.set_xticks(range(0, 21, 1))
ax.grid(True, alpha=0.3, linestyle='--')
ax.legend(loc='upper left', fontsize=9, framealpha=0.9, ncol=2)

plt.tight_layout()
viz2_path = os.path.join(output_dir, 'gt1_normal_shaded.png')
plt.savefig(viz2_path, dpi=150, bbox_inches='tight')
print(f"[OK] Saved: {viz2_path}")
plt.close()

# ============================================================================
# VISUALIZATION 3: Q-Q Plot (Normality Test)
# ============================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# Q-Q Plot
stats.probplot(scores, dist="norm", plot=ax1)
ax1.set_title('Q-Q Plot (정규성 검정)', fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.3)

# Box Plot with normal distribution overlay
bp = ax2.boxplot([scores], vert=False, widths=0.5, patch_artist=True,
                  boxprops=dict(facecolor='lightblue', alpha=0.7),
                  medianprops=dict(color='red', linewidth=2),
                  meanprops=dict(marker='D', markerfacecolor='green', markersize=10),
                  showmeans=True)

# Add normal distribution curve on secondary y-axis
ax2_twin = ax2.twinx()
ax2_twin.plot(x, normal_curve, 'r-', linewidth=2, alpha=0.7, label='정규분포')
ax2_twin.set_ylabel('확률 밀도', fontsize=11)
ax2_twin.legend(loc='upper right')

ax2.set_xlabel('점수 (정답 수)', fontsize=12, fontweight='bold')
ax2.set_title('Box Plot 및 정규분포 곡선', fontsize=13, fontweight='bold')
ax2.set_xlim(-0.5, 20.5)
ax2.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
viz3_path = os.path.join(output_dir, 'gt1_normality_test.png')
plt.savefig(viz3_path, dpi=150, bbox_inches='tight')
print(f"[OK] Saved: {viz3_path}")
plt.close()

# ============================================================================
# Statistical Tests
# ============================================================================
print("\n" + "=" * 80)
print("Normality Tests")
print("=" * 80)

# Shapiro-Wilk test
shapiro_stat, shapiro_p = stats.shapiro(scores)
print(f"\nShapiro-Wilk Test:")
print(f"  Statistic: {shapiro_stat:.4f}")
print(f"  P-value: {shapiro_p:.4f}")
print(f"  Result: {'정규분포를 따름' if shapiro_p > 0.05 else '정규분포를 따르지 않음'} (α=0.05)")

# Kolmogorov-Smirnov test
ks_stat, ks_p = stats.kstest(scores, 'norm', args=(mu, sigma))
print(f"\nKolmogorov-Smirnov Test:")
print(f"  Statistic: {ks_stat:.4f}")
print(f"  P-value: {ks_p:.4f}")
print(f"  Result: {'정규분포를 따름' if ks_p > 0.05 else '정규분포를 따르지 않음'} (α=0.05)")

# Skewness and Kurtosis
skewness = stats.skew(scores)
kurtosis = stats.kurtosis(scores)
print(f"\nSkewness (왜도): {skewness:.4f}")
print(f"  해석: {'좌편향' if skewness < -0.5 else '우편향' if skewness > 0.5 else '대칭적'}")
print(f"\nKurtosis (첨도): {kurtosis:.4f}")
print(f"  해석: {'뾰족함' if kurtosis > 0 else '평평함'}")

print("\n" + "=" * 80)
print("Analysis Complete!")
print("=" * 80)
print(f"\nGenerated files:")
print(f"  1. {viz1_path}")
print(f"  2. {viz2_path}")
print(f"  3. {viz3_path}")
print("\n" + "=" * 80)
