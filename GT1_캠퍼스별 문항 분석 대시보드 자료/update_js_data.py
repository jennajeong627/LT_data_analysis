import json
import os

base_dir = r"c:\Users\user\projects\LT_data_analysis"
json_file = os.path.join(base_dir, "may_campus_choice_data.json")
js_output_file = os.path.join(base_dir, "gt1_choice_data.js")

def update_js():
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    js_content = f"const MAY_CHOICE_DATA = {json.dumps(data, ensure_ascii=False, indent=2)};"
    
    with open(js_output_file, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"Updated {js_output_file}")

if __name__ == "__main__":
    update_js()
