import json

# Load the generated dashboard data
with open(r'c:\Users\user\projects\LT_data_analysis\2025_10월_data\dashboard_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Stats for individual campuses
stats = data.get('stats', {})
# Group stats (Direct, FC)
group_stats = data.get('group_stats', {})

transformed_data = {}

# Process individual campuses
for campus, q_data in stats.items():
    counts = [0] * 20
    corrects = [0] * 20
    accuracies = [0.0] * 20
    
    valid_data_found = False
    for q_num_str, vals in q_data.items():
        q_idx = int(q_num_str) - 1
        if 0 <= q_idx < 20:
            counts[q_idx] = vals['total']
            corrects[q_idx] = vals['correct_count']
            accuracies[q_idx] = vals['accuracy']
            valid_data_found = True
            
    if valid_data_found:
        transformed_data[campus] = {
            "응시인원": counts,
            "정답인원": corrects,
            "정답률": accuracies
        }

# Process group stats (add as pseudo-campuses for dropdown)
# Naming convention: Use existing names if possible or new unique keys
# In HTML logic, we might need to handle these keys specially or just treat them as campuses.
# '직영 캠퍼스 평균' and 'FC 캠퍼스 평균' as keys.

for group_name, q_data in group_stats.items():
    counts = [0] * 20
    corrects = [0] * 20
    accuracies = [0.0] * 20
    
    valid_data_found = False
    for q_num_str, vals in q_data.items():
        q_idx = int(q_num_str) - 1
        if 0 <= q_idx < 20:
            counts[q_idx] = vals['total']
            corrects[q_idx] = vals['correct_count']
            accuracies[q_idx] = vals['accuracy']
            valid_data_found = True
    
    if valid_data_found:
        key_name = f"{group_name} 캠퍼스 (평균)"
        transformed_data[key_name] = {
            "응시인원": counts,
            "정답인원": corrects,
            "정답률": accuracies
        }

# Create JS file content
final_data = {
    "2025년 10월 MT": transformed_data
}

js_content = f"window.dashboardDataOct = {json.dumps(final_data, ensure_ascii=False, indent=2)};"

with open(r'c:\Users\user\projects\LT_data_analysis\dashboard_data_oct.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print("JS data file generated: dashboard_data_oct.js")
