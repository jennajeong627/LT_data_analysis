import json

# Load the generated dashboard data
with open(r'c:\Users\user\projects\LT_data_analysis\2025_10월_data\dashboard_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

stats = data.get('stats', {})
transformed_data = {}

for campus, q_data in stats.items():
    # Initialize arrays of size 20
    counts = [0] * 20
    corrects = [0] * 20
    accuracies = [0.0] * 20
    
    valid_data_found = False
    
    for q_num_str, vals in q_data.items():
        q_idx = int(q_num_str) - 1 # 0-indexed
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

# Convert to JSON string (indented for readability, but we'll need to trim braces for injection)
# We want to inject it as a key in the existing object.
# So we generate the content: "2025년 10월 MT": { ... },

json_str = json.dumps(transformed_data, ensure_ascii=False, indent=2)
# Add the key wrapper
final_str = f'"2025년 10월 MT": {json_str},\n'

# Save to a temporary file to read back
with open(r'c:\Users\user\projects\LT_data_analysis\gt2_injection.txt', 'w', encoding='utf-8') as f:
    f.write(final_str)

print("Injection data prepared.")
