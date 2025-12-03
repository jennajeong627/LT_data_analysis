import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Set Korean font
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# Output directory
output_dir = r'C:\Users\user\.gemini\antigravity\brain\8fd772ef-33d9-4495-9894-ecaf33833f42'
os.makedirs(output_dir, exist_ok=True)

print("=" * 80)
print("GT1 C안 구간별 Reading Skill 오답 분석")
print("=" * 80)

# Load student-item level data
print("\n[1] Loading student-item data...")
df_items = pd.read_csv('data/2024_5월_학생문항별결과.csv', encoding='utf-8-sig')
print(f"   Total records: {len(df_items):,}")

# Filter GT1
df_gt1_items = df_items[df_items['레벨'] == 'GT1'].copy()
print(f"   GT1 records: {len(df_gt1_items):,}")

# Load aggregated data for C안 classification
df_agg = pd.read_csv('data/2024_5월_문항난이도별결과.csv', encoding='utf-8-sig')
df_students = df_agg.groupby(['레벨', '학생명'])['정답 수'].sum().reset_index()
df_students.columns = ['레벨', '학생명', '전체 정답 수']
df_gt1_students = df_students[df_students['레벨'] == 'GT1'].copy()

# Calculate percentile
df_gt1_students['백분위'] = df_gt1_students['전체 정답 수'].rank(pct=True) * 100

# C안 classification
criteria_c = {
    'below2': {'score': (0, 6), 'percentile': (0, 30)},
    'below1': {'score': (7, 11), 'percentile': (30, 55)},
    'on': {'score': (12, 15), 'percentile': (55, 75)},
    'above1': {'score': (16, 17), 'percentile': (75, 85)},
    'above2': {'score': (18, 20), 'percentile': (85, 100)}
}

def classify_c(row):
    score = row['전체 정답 수']
    percentile = row['백분위']
    
    for segment, criteria in criteria_c.items():
        score_min, score_max = criteria['score']
        perc_min, perc_max = criteria['percentile']
        
        score_match = score_min <= score <= score_max
        if segment == 'above2':
            perc_match = perc_min <= percentile <= perc_max
        else:
            perc_match = perc_min <= percentile < perc_max
        
        if score_match and perc_match:
            return segment
    
    return 'unclassified'

df_gt1_students['C안_구간'] = df_gt1_students.apply(classify_c, axis=1)

# Merge classification back to item-level data
df_gt1_items = df_gt1_items.merge(
    df_gt1_students[['학생명', 'C안_구간', '전체 정답 수']], 
    on='학생명', 
    how='left'
)

print(f"\n[2] C안 구간별 학생 수:")
segment_counts = df_gt1_students['C안_구간'].value_counts()
for segment in ['below2', 'below1', 'on', 'above1', 'above2', 'unclassified']:
    count = segment_counts.get(segment, 0)
    print(f"   {segment}: {count:,}명")

# ============================================================================
# Reading Skill Mapping (문항 번호 기반)
# ============================================================================
print("\n[3] Reading Skill 매핑...")

# 난이도별 문항 번호 매핑 (실제 데이터 기반)
# 각 난이도는 특정 문항 번호들에 해당
difficulty_to_items = {
    '★': [1, 2, 3, 4],           # 4개
    '★★': [5, 6, 7, 8, 9, 10],   # 6개
    '★★★': [11, 12, 13, 14, 15, 16],  # 6개
    '★★★★': [17, 18, 19, 20]     # 4개
}

# Reading Skill 정의 (난이도 기반)
reading_skills = {
    '★': 'Basic Comprehension (기본 이해)',
    '★★': 'Literal Understanding (문자적 이해)',
    '★★★': 'Inferential Reading (추론적 읽기)',
    '★★★★': 'Critical Analysis (비판적 분석)'
}

# 문항 번호 → Reading Skill 매핑
item_to_skill = {}
for difficulty, items in difficulty_to_items.items():
    skill = reading_skills[difficulty]
    for item_num in items:
        item_to_skill[item_num] = skill

# Add skill column
df_gt1_items['Reading_Skill'] = df_gt1_items['문항 순번'].map(item_to_skill)

# ============================================================================
# PART 1: 구간별 오답 분석
# ============================================================================
print("\n" + "=" * 80)
print("PART 1: C안 구간별 Reading Skill 오답 분석")
print("=" * 80)

# Filter only wrong answers
df_wrong = df_gt1_items[df_gt1_items['정답 여부'] == 'N'].copy()

segment_order = ['below2', 'below1', 'on', 'above1', 'above2']

# Analyze wrong answers by segment and skill
results = []

for segment in segment_order:
    segment_data = df_wrong[df_wrong['C안_구간'] == segment]
    total_wrong = len(segment_data)
    
    print(f"\n{segment} 구간:")
    print(f"  총 오답 수: {total_wrong:,}")
    
    if total_wrong > 0:
        skill_wrong = segment_data['Reading_Skill'].value_counts()
        
        for skill in reading_skills.values():
            wrong_count = skill_wrong.get(skill, 0)
            wrong_pct = (wrong_count / total_wrong * 100) if total_wrong > 0 else 0
            
            # Calculate total attempts for this skill in this segment
            segment_students = df_gt1_items[df_gt1_items['C안_구간'] == segment]
            skill_attempts = len(segment_students[segment_students['Reading_Skill'] == skill])
            
            error_rate = (wrong_count / skill_attempts * 100) if skill_attempts > 0 else 0
            
            print(f"  {skill}:")
            print(f"    오답 수: {wrong_count:,} ({wrong_pct:.1f}% of total wrong)")
            print(f"    오답률: {error_rate:.1f}%")
            
            results.append({
                '구간': segment,
                'Reading_Skill': skill,
                '오답_수': wrong_count,
                '오답_비율': wrong_pct,
                '오답률': error_rate,
                '시도_수': skill_attempts
            })

# Convert to DataFrame
df_results = pd.DataFrame(results)

# ============================================================================
# VISUALIZATIONS
# ============================================================================
print("\n" + "=" * 80)
print("Creating Visualizations")
print("=" * 80)

# Visualization 1: Heatmap of error rates by segment and skill
fig, ax = plt.subplots(figsize=(14, 8))

# Pivot for heatmap
heatmap_data = df_results.pivot(index='구간', columns='Reading_Skill', values='오답률')
heatmap_data = heatmap_data.reindex(segment_order)

# Reorder columns by skill order
skill_order = list(reading_skills.values())
heatmap_data = heatmap_data[skill_order]

# Create heatmap
im = ax.imshow(heatmap_data.values, cmap='RdYlGn_r', aspect='auto', vmin=0, vmax=100)

# Set ticks
ax.set_xticks(np.arange(len(skill_order)))
ax.set_yticks(np.arange(len(segment_order)))
ax.set_xticklabels(skill_order, fontsize=10, rotation=15, ha='right')
ax.set_yticklabels(segment_order, fontsize=11)

# Add colorbar
cbar = plt.colorbar(im, ax=ax)
cbar.set_label('오답률 (%)', rotation=270, labelpad=20, fontsize=11)

# Add text annotations
for i in range(len(segment_order)):
    for j in range(len(skill_order)):
        value = heatmap_data.values[i, j]
        if not np.isnan(value):
            text = ax.text(j, i, f'{value:.1f}%',
                          ha="center", va="center", color="black", 
                          fontsize=10, fontweight='bold')

ax.set_title('C안 구간별 Reading Skill 오답률 히트맵', fontsize=14, fontweight='bold', pad=20)
ax.set_xlabel('Reading Skill', fontsize=12, fontweight='bold')
ax.set_ylabel('C안 구간', fontsize=12, fontweight='bold')

plt.tight_layout()
viz1_path = os.path.join(output_dir, 'gt1_c_segment_skill_errors_heatmap.png')
plt.savefig(viz1_path, dpi=150, bbox_inches='tight')
print(f"\n[OK] Saved: {viz1_path}")
plt.close()

# Visualization 2: Stacked bar chart - wrong answer count by segment
fig, ax = plt.subplots(figsize=(12, 7))

# Prepare data
segment_skill_wrong = df_results.pivot(index='구간', columns='Reading_Skill', values='오답_수')
segment_skill_wrong = segment_skill_wrong.reindex(segment_order)[skill_order]

# Plot stacked bar
segment_skill_wrong.plot(kind='bar', stacked=True, ax=ax, 
                         color=['#e53e3e', '#ed8936', '#48bb78', '#38a169'],
                         alpha=0.8, edgecolor='black', linewidth=1.2)

ax.set_xlabel('C안 구간', fontsize=12, fontweight='bold')
ax.set_ylabel('오답 수', fontsize=12, fontweight='bold')
ax.set_title('C안 구간별 Reading Skill 오답 수', fontsize=14, fontweight='bold', pad=15)
ax.legend(title='Reading Skill', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
ax.grid(axis='y', alpha=0.3)
plt.xticks(rotation=0)

plt.tight_layout()
viz2_path = os.path.join(output_dir, 'gt1_c_segment_skill_errors_stacked.png')
plt.savefig(viz2_path, dpi=150, bbox_inches='tight')
print(f"[OK] Saved: {viz2_path}")
plt.close()

# Visualization 3: Grouped bar chart - error rate comparison
fig, ax = plt.subplots(figsize=(14, 8))

x = np.arange(len(segment_order))
width = 0.2

for i, skill in enumerate(skill_order):
    skill_data = df_results[df_results['Reading_Skill'] == skill]
    skill_data = skill_data.set_index('구간').reindex(segment_order)
    
    offset = (i - len(skill_order)/2 + 0.5) * width
    bars = ax.bar(x + offset, skill_data['오답률'].values, width, 
                  label=skill, alpha=0.8)

ax.set_xlabel('C안 구간', fontsize=12, fontweight='bold')
ax.set_ylabel('오답률 (%)', fontsize=12, fontweight='bold')
ax.set_title('C안 구간별 Reading Skill 오답률 비교', fontsize=14, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(segment_order)
ax.legend(title='Reading Skill', fontsize=9)
ax.grid(axis='y', alpha=0.3)
ax.set_ylim(0, 100)

plt.tight_layout()
viz3_path = os.path.join(output_dir, 'gt1_c_segment_skill_errors_grouped.png')
plt.savefig(viz3_path, dpi=150, bbox_inches='tight')
print(f"[OK] Saved: {viz3_path}")
plt.close()

# ============================================================================
# SAVE REPORT
# ============================================================================
print("\n" + "=" * 80)
print("Saving Report")
print("=" * 80)

report_path = os.path.join(output_dir, 'gt1_c_segment_skill_errors_report.txt')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("GT1 C안 구간별 Reading Skill 오답 분석\n")
    f.write("=" * 80 + "\n\n")
    
    f.write("구간별 학생 수:\n")
    f.write("-" * 80 + "\n")
    for segment in segment_order + ['unclassified']:
        count = segment_counts.get(segment, 0)
        f.write(f"{segment}: {count:,}명\n")
    
    f.write("\n\n구간별 Reading Skill 오답 분석:\n")
    f.write("=" * 80 + "\n\n")
    
    for segment in segment_order:
        segment_results = df_results[df_results['구간'] == segment]
        f.write(f"\n{segment} 구간:\n")
        f.write("-" * 80 + "\n")
        
        total_wrong = segment_results['오답_수'].sum()
        f.write(f"총 오답 수: {int(total_wrong):,}\n\n")
        
        for _, row in segment_results.iterrows():
            f.write(f"{row['Reading_Skill']}:\n")
            f.write(f"  오답 수: {int(row['오답_수']):,} ({row['오답_비율']:.1f}% of total wrong)\n")
            f.write(f"  오답률: {row['오답률']:.1f}%\n")
            f.write(f"  시도 수: {int(row['시도_수']):,}\n\n")

print(f"[OK] Saved: {report_path}")

print("\n" + "=" * 80)
print("Analysis Complete!")
print("=" * 80)
print(f"\nGenerated files:")
print(f"  1. {viz1_path}")
print(f"  2. {viz2_path}")
print(f"  3. {viz3_path}")
print(f"  4. {report_path}")
print("\n" + "=" * 80)
