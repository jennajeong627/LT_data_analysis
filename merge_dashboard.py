import os

def merge():
    html_path = r'c:\Users\user\projects\LT_data_analysis\2025_Grade_Analysis_Dashboard.html'
    data_path = r'c:\Users\user\projects\LT_data_analysis\scatter_data.js'
    output_path = r'c:\Users\user\projects\LT_data_analysis\2025_Grade_Analysis_Report.html'

    if not os.path.exists(html_path) or not os.path.exists(data_path):
        print("Required files not found.")
        return

    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    with open(data_path, 'r', encoding='utf-8') as f:
        data_content = f.read()

    # Replace the external script tag with inline data
    target = '<script src="./scatter_data.js"></script>'
    replacement = f'<script>\n{data_content}\n</script>'
    
    if target in html_content:
        final_html = html_content.replace(target, replacement)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_html)
        print(f"Success! Final dashboard saved to: {output_path}")
    else:
        print("Could not find the scatter_data.js script tag in HTML.")

if __name__ == "__main__":
    merge()
