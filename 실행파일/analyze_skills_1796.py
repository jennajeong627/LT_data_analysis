import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Set Korean font
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# Output directory
# 결과 파일 경로
output_dir = "output/11월/analyze_skills_1796"
# 각 월별 데이터 CSV 파일 경로
csv_file_path = "2024_11월_data/2024_11월__학생문항별결과.csv"
os.makedirs(output_dir, exist_ok=True)

print("=" * 80)
print("GT1 20개 Skill별 정답률 분석 (1,796명 기준)")
print("=" * 80)

# Load data
print("\n[1] 데이터 로딩...")
# 각 월별 데이터 CSV 파일 경로
df_items = pd.read_csv(csv_file_path, encoding='utf-8-sig')
df_gt1 = df_items[df_items['레벨'] == 'GT1'].copy()

# 고유 식별자 생성
df_gt1['학생_ID'] = df_gt1['학생명'].astype(str) + '_' + df_gt1.iloc[:, 0].astype(str)

total_students = df_gt1['학생_ID'].nunique()
print(f"   GT1 학생 수: {total_students:,}명")

# Skill 매핑
difficulty_mapping = {
    '★': list(range(1, 5)),
    '★★': list(range(5, 11)),
    '★★★': list(range(11, 17)),
    '★★★★': list(range(17, 21))
}

skill_definitions = {}
for difficulty, item_nums in difficulty_mapping.items():
    for item_num in item_nums:
        skill_definitions[item_num] = {
            'skill_num': item_num,
            'difficulty': difficulty,
            'name': f'Skill {item_num:02d}'
        }

# Skill별 정답률 계산
print("\n[2] Skill별 정답률 계산...")
skill_results = []

for item_num in range(1, 21):
    item_data = df_gt1[df_gt1['문항 순번'] == item_num]
    
    if len(item_data) == 0:
        continue
    
    total_attempts = len(item_data)
    correct_count = len(item_data[item_data['정답 여부'] == 'Y'])
    wrong_count = len(item_data[item_data['정답 여부'] == 'N'])
    
    correct_rate = (correct_count / total_attempts * 100) if total_attempts > 0 else 0
    wrong_rate = (wrong_count / total_attempts * 100) if total_attempts > 0 else 0
    
    difficulty = skill_definitions[item_num]['difficulty']
    
    skill_results.append({
        'Skill': item_num,
        'Skill_Name': f'Skill {item_num:02d}',
        '난이도': difficulty,
        '시도_수': total_attempts,
        '정답_수': correct_count,
        '오답_수': wrong_count,
        '정답률': correct_rate,
        '오답률': wrong_rate
    })
    
    print(f"Skill {item_num:02d} ({difficulty:4s}): 정답률 {correct_rate:5.1f}% ({correct_count:4,}/{total_attempts:4,})")

df_skills = pd.DataFrame(skill_results)

# 난이도별 평균
print("\n[3] 난이도별 평균 정답률:")
difficulty_stats = df_skills.groupby('난이도').agg({
    '정답률': 'mean',
    'Skill': 'count'
}).round(2)

for difficulty in ['★', '★★', '★★★', '★★★★']:
    if difficulty in difficulty_stats.index:
        avg_rate = difficulty_stats.loc[difficulty, '정답률']
        count = int(difficulty_stats.loc[difficulty, 'Skill'])
        print(f"  {difficulty:4s}: 평균 {avg_rate:5.1f}% ({count}개 문항)")

# 시각화 1: 전체 Skill 정답률
print("\n[4] 시각화 생성...")
fig, ax = plt.subplots(figsize=(16, 8))

colors = []
for difficulty in df_skills['난이도']:
    if difficulty == '★':
        colors.append('#48bb78')
    elif difficulty == '★★':
        colors.append('#38a169')
    elif difficulty == '★★★':
        colors.append('#ed8936')
    else:
        colors.append('#e53e3e')

bars = ax.bar(df_skills['Skill'], df_skills['정답률'], color=colors, alpha=0.8, edgecolor='black', linewidth=1.2)

for bar, skill_num, rate in zip(bars, df_skills['Skill'], df_skills['정답률']):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{rate:.1f}%',
            ha='center', va='bottom', fontsize=9, fontweight='bold')

ax.set_xlabel('Skill 번호 (문항 번호)', fontsize=13, fontweight='bold')
ax.set_ylabel('정답률 (%)', fontsize=13, fontweight='bold')
ax.set_title(f'GT1 학생 20개 Skill별 정답률 (N={total_students:,})', fontsize=15, fontweight='bold', pad=20)
ax.set_xticks(range(1, 21))
ax.set_ylim(0, 100)
ax.grid(axis='y', alpha=0.3, linestyle='--')

ax.axvline(x=4.5, color='gray', linestyle='--', alpha=0.5)
ax.axvline(x=10.5, color='gray', linestyle='--', alpha=0.5)
ax.axvline(x=16.5, color='gray', linestyle='--', alpha=0.5)

ax.text(2.5, 95, '★', ha='center', fontsize=14, fontweight='bold', color='#48bb78')
ax.text(7.5, 95, '★★', ha='center', fontsize=14, fontweight='bold', color='#38a169')
ax.text(13.5, 95, '★★★', ha='center', fontsize=14, fontweight='bold', color='#ed8936')
ax.text(18.5, 95, '★★★★', ha='center', fontsize=14, fontweight='bold', color='#e53e3e')

from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#48bb78', label='★ Basic (1-4)', alpha=0.8),
    Patch(facecolor='#38a169', label='★★ Literal (5-10)', alpha=0.8),
    Patch(facecolor='#ed8936', label='★★★ Inferential (11-16)', alpha=0.8),
    Patch(facecolor='#e53e3e', label='★★★★ Critical (17-20)', alpha=0.8)
]
ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

plt.tight_layout()
viz1_path = os.path.join(output_dir, 'gt1_skill_accuracy_1796.png')
plt.savefig(viz1_path, dpi=150, bbox_inches='tight')
print(f"   저장: {viz1_path}")
plt.close()

# 시각화 2: 히트맵
fig, ax = plt.subplots(figsize=(16, 6))

skill_nums = df_skills['Skill'].values
rates = df_skills['정답률'].values

for i, (skill, rate) in enumerate(zip(skill_nums, rates)):
    if rate >= 80:
        color = '#2f855a'
    elif rate >= 60:
        color = '#48bb78'
    elif rate >= 40:
        color = '#ed8936'
    else:
        color = '#e53e3e'
    
    rect = plt.Rectangle((i, 0), 1, 1, facecolor=color, edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    
    ax.text(i + 0.5, 0.5, f'S{skill:02d}\n{rate:.1f}%',
            ha='center', va='center', fontsize=10, fontweight='bold', color='white')

ax.set_xlim(0, 20)
ax.set_ylim(0, 1)
ax.set_xticks(np.arange(0.5, 20.5, 1))
ax.set_xticklabels(range(1, 21))
ax.set_yticks([])
ax.set_xlabel('Skill 번호', fontsize=13, fontweight='bold')
ax.set_title(f'GT1 Skill별 정답률 히트맵 (N={total_students:,})', fontsize=15, fontweight='bold', pad=20)

for x in [4, 10, 16]:
    ax.axvline(x=x, color='white', linewidth=3)

plt.tight_layout()
viz2_path = os.path.join(output_dir, 'gt1_skill_heatmap_1796.png')
plt.savefig(viz2_path, dpi=150, bbox_inches='tight')
print(f"   저장: {viz2_path}")
plt.close()

# CSV 저장
csv_path = os.path.join(output_dir, 'gt1_skill_data_1796.csv')
df_skills.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f"   저장: {csv_path}")

print("\n" + "=" * 80)
print("Skill 분석 완료!")
print("=" * 80)
print(f"총 학생 수: {total_students:,}명")
print(f"난이도별 평균:")
for difficulty in ['★', '★★', '★★★', '★★★★']:
    if difficulty in difficulty_stats.index:
        print(f"  {difficulty}: {difficulty_stats.loc[difficulty, '정답률']:.1f}%")
print("=" * 80)
