import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import matplotlib.font_manager as fm

# Set font for Korean support (adjust if necessary for the specific environment)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def analyze_and_visualize():
    # Load data
    file_path = 'data/2024_5월_문항난이도별결과.csv'
    df = None
    encodings = ['utf-8', 'cp949', 'euc-kr']
    
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            print(f"Successfully read with encoding: {enc}")
            break
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"Error reading with {enc}: {e}")
            
    if df is None:
        print("Failed to read the file with tried encodings.")
        return

    print("Columns found:", df.columns.tolist())

    # Filter for specific levels
    target_levels = ['GT1', 'MGT1', 'S1', 'MAG1']
    
    # Check if columns exist
    if '레벨' not in df.columns or '전체정답' not in df.columns:
        print("Required columns '레벨' or '전체정답' not found.")
        return

    df_filtered = df[df['레벨'].isin(target_levels)].copy()

    if df_filtered.empty:
        print("No data found for the specified levels.")
        return

    # Define segments
    def classify_segment(score):
        if 0 <= score <= 9:
            return 'below2'
        elif 10 <= score <= 11:
            return 'below1'
        elif 12 <= score <= 15:
            return 'on'
        elif 16 <= score <= 17:
            return 'above1'
        elif 18 <= score <= 20:
            return 'above2'
        else:
            return 'unknown'

    df_filtered['segment'] = df_filtered['전체정답'].apply(classify_segment)

    # Calculate counts per segment for each level
    segment_order = ['below2', 'below1', 'on', 'above1', 'above2']
    counts = df_filtered.groupby(['레벨', 'segment']).size().unstack(fill_value=0)
    
    # Ensure all segments are present
    for seg in segment_order:
        if seg not in counts.columns:
            counts[seg] = 0
            
    counts = counts[segment_order] # Reorder columns
    
    print("Student Counts per Segment by Level:")
    print(counts)
    
    # Visualization
    plt.figure(figsize=(14, 8))
    
    colors = {'GT1': 'red', 'MGT1': 'blue', 'S1': 'green', 'MAG1': 'orange'}
    
    x = np.linspace(0, 20, 200)
    
    for level in target_levels:
        subset = df_filtered[df_filtered['레벨'] == level]
        if len(subset) > 1:
            mu = subset['전체정답'].mean()
            sigma = subset['전체정답'].std()
            
            y = stats.norm.pdf(x, mu, sigma)
            plt.plot(x, y, label=f'{level} (μ={mu:.2f}, σ={sigma:.2f})', color=colors.get(level, 'black'), alpha=0.7)
            plt.fill_between(x, y, color=colors.get(level, 'black'), alpha=0.1)
        else:
            print(f"Not enough data to plot distribution for {level}")

    # Add segment boundaries
    boundaries = [9.5, 11.5, 15.5, 17.5] # Midpoints between integer boundaries
    for b in boundaries:
        plt.axvline(b, color='gray', linestyle='--', alpha=0.5)

    # Add text labels for segments (approximate positions)
    plt.text(4.5, 0.01, 'below2', ha='center', alpha=0.5)
    plt.text(10.5, 0.01, 'below1', ha='center', alpha=0.5)
    plt.text(13.5, 0.01, 'on', ha='center', alpha=0.5)
    plt.text(16.5, 0.01, 'above1', ha='center', alpha=0.5)
    plt.text(19, 0.01, 'above2', ha='center', alpha=0.5)

    plt.title('2024년 5월 레벨별 학생 성적 정규분포 (Standard B)')
    plt.xlabel('전체 정답 수 (점수)')
    plt.ylabel('확률 밀도')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim(0, 20)
    
    output_file = 'standard_test_B_distribution.png'
    plt.savefig(output_file)
    print(f"Visualization saved to {output_file}")

if __name__ == "__main__":
    analyze_and_visualize()
