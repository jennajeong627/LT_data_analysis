import pandas as pd
import json
import random

def main():
    csv_path = r"c:\Users\user\projects\LT_data_analysis\integrated_grades_detail.csv"
    df = pd.read_csv(csv_path)
    
    # Levels Order: GT2(Bottom) to MAG2(Top) visually
    # Let's map them to Y-axis indices.
    # We want GT2 at bottom (y=0) or top?
    # Usually in strip plot:
    # MAG2 (Top)
    # S2
    # MGT2
    # GT2 (Bottom)
    # So let's align with that. GT2=0, MGT2=1, S2=2, MAG2=3.
    
    level_map = {'GT2': 0, 'MGT2': 1, 'S2': 2, 'MAG2': 3}
    
    abs_data = []
    rel_data = []
    
    for _, row in df.iterrows():
        lvl = row['Level']
        if lvl not in level_map: continue
        
        x_base = level_map[lvl]
        # Add jitter to X (range +/- 0.3)
        jitter = (random.random() - 0.5) * 0.6 
        x_val = x_base + jitter
        
        # Absolute Data: y = Score
        abs_data.append({
            'x': x_val,
            'y': row['Score'],
            'level': lvl,
            'name': row['이름']
        })
        
        # Relative Data: y = Percentile (Top %)
        rel_data.append({
            'x': x_val,
            'y': row['Percentile'],
            'level': lvl,
            'name': row['이름']
        })
        
    output = {
        'abs': abs_data,
        'rel': rel_data
    }
    
    # Write to a specific JS file that simply sets a global variable
    js_content = f"const scatterData = {json.dumps(output)};"
    
    with open(r"c:\Users\user\projects\LT_data_analysis\scatter_data.js", "w", encoding="utf-8") as f:
        f.write(js_content)
        
    print("Scatter data exported to scatter_data.js")

if __name__ == "__main__":
    main()
