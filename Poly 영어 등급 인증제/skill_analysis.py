import pandas as pd
import os

def analyze_student_performance_for_parent_report(data_folder, student_name, student_level):
    all_level_files = {
        "GT2": "2025_11월_GT2.csv",
        "MGT2": "2025_11월_MGT2.csv",
        "S2": "2025_11월_S2.csv",
        "MAG2": "2025_11월_MAG2.csv",
    }

    # 전국 2학년 전체 학생 데이터 로드
    national_data_frames = []
    for level, filename in all_level_files.items():
        filepath = os.path.join(data_folder, filename)
        df_level = pd.read_csv(filepath)
        df_level['교육과정'] = level # 레벨 정보 추가
        national_data_frames.append(df_level)

    national_df = pd.concat(national_data_frames)
    national_df['correct'] = national_df['정답여부'].apply(lambda x: 1 if x == 'Y' else 0)

    # 김지우 학생 데이터 필터링 (MGT2 레벨에서 찾음)
    student_data_filepath = os.path.join(data_folder, all_level_files[student_level])
    student_raw_df = pd.read_csv(student_data_filepath)
    kim_jiwoo_df = student_raw_df[student_raw_df['이름'] == student_name]

    if kim_jiwoo_df.empty:
        return {f"{student_name} 학생 데이터를 찾을 수 없습니다."}

    kim_jiwoo_df = kim_jiwoo_df.copy()
    kim_jiwoo_df['correct'] = kim_jiwoo_df['정답여부'].apply(lambda x: 1 if x == 'Y' else 0)
    kim_jiwoo_df['incorrect'] = kim_jiwoo_df['정답여부'].apply(lambda x: 1 if x == 'N' else 0)

    # 과목별 세부 의견 생성
    parent_report_details = {}
    for subject in kim_jiwoo_df['시험과목'].unique():
        subject_detail = {
            "national_rank_percentile": "분석 불가",
            "strongest_skill": "정보 없음",
            "weakest_skill": "정보 없음"
        }

        # 김지우 학생의 해당 과목 점수 계산
        jiwoo_subject_df = kim_jiwoo_df[kim_jiwoo_df['시험과목'] == subject]
        jiwoo_total_score = jiwoo_subject_df['correct'].sum()
        jiwoo_total_questions = len(jiwoo_subject_df['문항 순번'].unique())

        # 전국 학생들의 해당 과목 점수 분포 계산
        national_subject_df = national_df[national_df['시험과목'] == subject]
        national_student_scores = national_subject_df.groupby(['학번', '이름'])['correct'].sum().reset_index()
        national_scores = national_student_scores['correct'].tolist()

        if jiwoo_total_questions > 0 and national_scores:
            percentile = (pd.Series(national_scores) < jiwoo_total_score).mean() * 100
            subject_detail["national_rank_percentile"] = f"상위 {(100 - percentile):.1f}%"

            # 스킬별 상세 분석
            skill_performance = jiwoo_subject_df.groupby(['스킬']).agg(
                correct_count=('correct', 'sum'),
                incorrect_count=('incorrect', 'sum')
            ).reset_index()

            if not skill_performance.empty:
                # 가장 많이 맞춘 스킬
                most_correct_skill = skill_performance.loc[skill_performance['correct_count'].idxmax()]
                if most_correct_skill['correct_count'] > 0:
                    subject_detail["strongest_skill"] = f"'{most_correct_skill['스킬']}' ({most_correct_skill['correct_count']}개)"

                # 가장 적게 맞춘 스킬
                most_incorrect_skill = skill_performance.loc[skill_performance['incorrect_count'].idxmax()]
                if most_incorrect_skill['incorrect_count'] > 0:
                    subject_detail["weakest_skill"] = f"'{most_incorrect_skill['스킬']}' ({most_incorrect_skill['incorrect_count']}개)"
        
        parent_report_details[subject] = subject_detail

    return parent_report_details

if __name__ == "__main__":
    data_folder = "2025_LT_11월_data"
    student_name = "김지우"
    student_level = "MGT2"
    
    report_details = analyze_student_performance_for_parent_report(data_folder, student_name, student_level)
    for subject, details in report_details.items():
        print(f"과목: {subject}")
        print(f"  전국 순위: {details['national_rank_percentile']}")
        print(f"  강점 스킬: {details['strongest_skill']}")
        print(f"  보완 스킬: {details['weakest_skill']}\n")
