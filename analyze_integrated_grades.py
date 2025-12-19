import pandas as pd
import glob
import os

# Define grading criteria
ABSOLUTE_CUTS = [
    (54, 1), (48, 2), (42, 3), (36, 4), (30, 5), (24, 6), (18, 7), (12, 8), (0, 9)
]

RELATIVE_CUTS = [
    (4, 1), (11, 2), (23, 3), (40, 4), (60, 5), (77, 6), (89, 7), (96, 8), (100, 9)
]

def get_absolute_grade(score):
    for cut, grade in ABSOLUTE_CUTS:
        if score >= cut:
            return grade
    return 9

def get_relative_grade(percentile):
    for cut, grade in RELATIVE_CUTS:
        if percentile <= cut:
            return grade
    return 9

def main():
    base_dir = r"c:\Users\user\projects\LT_data_analysis\2025_LT_11월_data"
    files = {
        'GT2': os.path.join(base_dir, "2025_11월_GT2.csv"),
        'MGT2': os.path.join(base_dir, "2025_11월_MGT2.csv"),
        'S2': os.path.join(base_dir, "2025_11월_S2.csv"),
        'MAG2': os.path.join(base_dir, "2025_11월_MAG2.csv")
    }

    all_students = []

    for level, file_path in files.items():
        if not os.path.exists(file_path):
            print(f"Warning: File not found {file_path}")
            continue
        
        print(f"Reading {file_path}...")
        df = pd.read_csv(file_path)
        
        # Calculate score per student
        # Assuming '정답여부' == 'Y' counts as 1 point.
        # Group by '학번' and '이름' to get unique students
        student_scores = df[df['정답여부'] == 'Y'].groupby(['학번', '이름']).size().reset_index(name='Score')
        
        # We also need to include students who might have got 0 score (if they exist in the file but have no 'Y')
        # So it's better to group by student first.
        unique_students = df[['학번', '이름']].drop_duplicates()
        
        # Merge scores
        student_data = pd.merge(unique_students, student_scores, on=['학번', '이름'], how='left')
        student_data['Score'] = student_data['Score'].fillna(0).astype(int)
        student_data['Level'] = level
        
        all_students.append(student_data)

    if not all_students:
        print("No data found.")
        return

    full_df = pd.concat(all_students, ignore_index=True)
    total_students = len(full_df)
    print(f"Total Combined Students (National 2nd Grade): {total_students}")

    # --- Absolute Grading ---
    full_df['Abs_Grade'] = full_df['Score'].apply(get_absolute_grade)

    # --- Relative Grading ---
    # Sort by score descending
    full_df = full_df.sort_values(by='Score', ascending=False)
    
    # Calculate Rank (Min method gives better rank for ties, e.g. 1, 1, 3. 
    # Use 'min' for rank to match standard competitive ranking, 
    # but for percentile cutoffs, checks are usually strictly <= N%.
    # Let's calculate percentile based on Rank.
    full_df['Rank'] = full_df['Score'].rank(method='min', ascending=False)
    full_df['Percentile'] = (full_df['Rank'] / total_students) * 100
    
    full_df['Rel_Grade'] = full_df['Percentile'].apply(get_relative_grade)

    # --- Analysis: Distribution by Level and Grade ---
    
    # Absolute Distribution
    abs_pivot = full_df.pivot_table(index='Abs_Grade', columns='Level', values='학번', aggfunc='count', fill_value=0)
    # Reorder columns if present
    desired_order = ['GT2', 'MGT2', 'S2', 'MAG2']
    cols = [c for c in desired_order if c in abs_pivot.columns]
    abs_pivot = abs_pivot[cols]
    
    # Add Total column
    abs_pivot['Total'] = abs_pivot.sum(axis=1)
    
    # Add Total Row
    # abs_pivot.loc['Total'] = abs_pivot.sum()

    print("\n[Absolute Evaluation Distribution (60 point scale)]")
    # Add grade descriptions
    print(abs_pivot)

    # Relative Distribution
    rel_pivot = full_df.pivot_table(index='Rel_Grade', columns='Level', values='학번', aggfunc='count', fill_value=0)
    rel_pivot = rel_pivot[cols]
    rel_pivot['Total'] = rel_pivot.sum(axis=1)

    print("\n[Relative Evaluation Distribution (Percentile based)]")
    print(rel_pivot)

    # Save detailed data for checking
    full_df.to_csv("integrated_grades_detail.csv", index=False)
    print("\nDetailed results saved to integrated_grades_detail.csv")

if __name__ == "__main__":
    main()
