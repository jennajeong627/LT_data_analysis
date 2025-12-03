import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Set Korean font
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# Output directory
output_dir = r'C:\Users\user\.gemini\antigravity\brain\90cafe6d-262c-4846-b721-9583dbc8eeda'
os.makedirs(output_dir, exist_ok=True)

print("=" * 80)
print("Low Score Student (<14) Skill Analysis")
print("=" * 80)

# Load data
print("\n[1] Loading data...")
try:
    df = pd.read_csv('data/2024_5월_학생문항별결과.csv', encoding='utf-8-sig')
except FileNotFoundError:
    print("Error: File not found. Please check the path.")
    exit()

# Calculate total score per student
# We need to group by student and sum '정답 여부' (converted to int) or just count 'Y'
# The file has '정답 여부' column with 'Y'/'N'.
# It also has '문항 순번' which maps to Skill 1-20.

print("   Calculating student total scores...")
# Convert '정답 여부' to numeric (Y=1, N=0)
df['is_correct'] = df['정답 여부'].apply(lambda x: 1 if x == 'Y' else 0)

# Group by student to get total score
student_scores = df.groupby('학생명')['is_correct'].sum().reset_index()
student_scores.rename(columns={'is_correct': 'total_score'}, inplace=True)

# Filter students with score < 14
low_score_students = student_scores[student_scores['total_score'] < 14]['학생명'].unique()
print(f"   Total students: {len(student_scores):,}")
print(f"   Students with score < 14: {len(low_score_students):,}")

# Filter original dataframe for these students
df_low = df[df['학생명'].isin(low_score_students)].copy()

# ============================================================================
# Analyze Skill Accuracy for this group
# ============================================================================
print("\n[2] Analyzing Skill Accuracy for Low Score Group...")

skill_results = []

for item_num in range(1, 21):
    # Filter for this item (Skill)
    item_data = df_low[df_low['문항 순번'] == item_num]
    
    if len(item_data) == 0:
        continue
        
    total_attempts = len(item_data)
    correct_count = item_data['is_correct'].sum()
    correct_rate = (correct_count / total_attempts * 100) if total_attempts > 0 else 0
    
    skill_results.append({
        'Skill': item_num,
        'Skill_Name': f'Skill {item_num:02d}',
        'Total_Attempts': total_attempts,
        'Correct_Count': correct_count,
        'Correct_Rate': correct_rate
    })

df_skills = pd.DataFrame(skill_results)

# Save results to CSV
csv_path = os.path.join(output_dir, 'low_score_skills_analysis.csv')
df_skills.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f"   Saved analysis data to: {csv_path}")

# ============================================================================
# Visualization
# ============================================================================
print("\n[3] Creating Visualization...")

fig, ax = plt.subplots(figsize=(14, 7))

# Color mapping based on difficulty (inferred from previous context)
# 1-4: Basic (★), 5-10: Literal (★★), 11-16: Inferential (★★★), 17-20: Critical (★★★★)
colors = []
for skill in df_skills['Skill']:
    if 1 <= skill <= 4: colors.append('#48bb78')      # Green
    elif 5 <= skill <= 10: colors.append('#38a169')    # Darker Green
    elif 11 <= skill <= 16: colors.append('#ed8936')   # Orange
    else: colors.append('#e53e3e')                     # Red

bars = ax.bar(df_skills['Skill'], df_skills['Correct_Rate'], color=colors, alpha=0.8, edgecolor='black')

# Add values on top of bars
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.1f}%',
            ha='center', va='bottom', fontsize=9, fontweight='bold')

ax.set_xlabel('Skill (Question Number)', fontsize=12, fontweight='bold')
ax.set_ylabel('Correct Rate (%)', fontsize=12, fontweight='bold')
ax.set_title('Skill Accuracy for Students with Score < 14', fontsize=14, fontweight='bold', pad=15)
ax.set_xticks(range(1, 21))
ax.set_ylim(0, 100)
ax.grid(axis='y', alpha=0.3, linestyle='--')

# Add legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#48bb78', label='Basic (1-4)', alpha=0.8),
    Patch(facecolor='#38a169', label='Literal (5-10)', alpha=0.8),
    Patch(facecolor='#ed8936', label='Inferential (11-16)', alpha=0.8),
    Patch(facecolor='#e53e3e', label='Critical (17-20)', alpha=0.8)
]
ax.legend(handles=legend_elements, loc='upper right')

plt.tight_layout()
viz_path = os.path.join(output_dir, 'low_score_skills_chart.png')
plt.savefig(viz_path, dpi=150, bbox_inches='tight')
print(f"   Saved visualization to: {viz_path}")
plt.close()

print("\n" + "=" * 80)
print("Analysis Complete!")
print("=" * 80)
