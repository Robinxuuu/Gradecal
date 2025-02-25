import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import matplotlib

# 设置 Matplotlib 使用 SimHei 字体，防止中文乱码
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 黑体
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


def get_user_input():
    st.title("成绩计算仪表盘")
    courses = []
    num_courses = st.number_input("输入课程数量", min_value=1, step=1)
    for i in range(num_courses):
        course_name = st.text_input(f"输入课程 {i + 1} 的名称:")
        credits = st.number_input(f"请输入 {course_name} 的学分:", min_value=1.0, step=1.0)
        max_score = st.number_input(f"请输入 {course_name} 的评分满分 (如100, 4.0, 20等):", min_value=1.0, step=1.0)
        assignments = []
        num_assignments = st.number_input(f"输入 {course_name} 的作业/考试数量:", min_value=1, step=1)
        for j in range(num_assignments):
            assignment_name = st.text_input(f"  输入 {course_name} 的作业/考试 {j + 1} 名称:",
                                            key=f"{course_name}_{j}_name")
            weight = st.number_input(f"  请输入 {assignment_name} 在 {course_name} 中的占比 (如 0.3 表示 30%):",
                                     min_value=0.0, max_value=1.0, step=0.01, key=f"{course_name}_{j}_weight")
            score_input = st.text_input(
                f"  请输入 {assignment_name} 已出成绩 (如未出分则输入 'NA'):",
                key=f"{course_name}_{assignment_name}_score"
            )

            if not score_input.strip():
                score = None
            elif score_input.lower() == 'na':
                score = None
            else:
                try:
                    score = float(score_input)
                    score = (score / max_score) * 100  # 标准化到100分制
                except ValueError:
                    score = None  # 如果输入无效，设为 None

            assignments.append({'name': assignment_name, 'weight': weight, 'score': score})
        courses.append({'name': course_name, 'credits': credits, 'max_score': max_score, 'assignments': assignments})
    return courses


def calculate_current_average(courses):
    total_credits = sum(course['credits'] for course in courses)
    known_weighted_score = 0
    known_weight = 0
    remaining_assignments = []
    course_scores = {}

    for course in courses:
        course_weight = course['credits'] / total_credits
        course_final_score = 0
        total_weight = 0
        for assignment in course['assignments']:
            if assignment['score'] is not None:
                course_final_score += assignment['score'] * assignment['weight']
                total_weight += assignment['weight']
            else:
                remaining_assignments.append((course, assignment, course_weight))
        if total_weight > 0:
            course_final_score /= total_weight
            known_weighted_score += course_final_score * course_weight
            known_weight += course_weight
            course_scores[course['name']] = course_final_score
    return known_weighted_score, known_weight, remaining_assignments, course_scores


def predict_needed_scores(courses, target_avg):
    current_weighted_score, known_weight, remaining_assignments, course_scores = calculate_current_average(courses)
    remaining_weight = 1 - known_weight
    if remaining_weight <= 0:
        return "所有分数已出，无法预测未出分的需求", course_scores
    required_score = (target_avg - current_weighted_score) / remaining_weight
    return f"为了达到 {target_avg:.2f}，你在未出分部分需要平均 {required_score:.2f} 分。", course_scores


def plot_score_distribution(course_scores, target_avg):
    courses = list(course_scores.keys())
    scores = list(course_scores.values())

    fig, ax = plt.subplots()
    ax.bar(courses, scores, color='blue', alpha=0.7, label='Current score')
    ax.axhline(y=target_avg, color='r', linestyle='--', label=f'Aimed score: {target_avg}')
    ax.set_xlabel('Modules')
    ax.set_ylabel('Score')
    ax.set_title('Results')
    ax.legend()
    st.pyplot(fig)


def main():
    courses = get_user_input()
    target_avg = st.number_input("请输入你的目标最终成绩:", min_value=0.0, max_value=100.0, step=0.1)
    prediction, course_scores = predict_needed_scores(courses, target_avg)
    st.write(prediction)
    plot_score_distribution(course_scores, target_avg)

    simulate_choice = st.checkbox("是否要模拟不同情况？")
    if simulate_choice:
        course_name = st.selectbox("选择你想调整的课程:", [c['name'] for c in courses])
        new_score = st.number_input(f"请输入 {course_name} 的新分数:", min_value=0.0, max_value=100.0, step=0.1)
        for course in courses:
            if course['name'] == course_name:
                max_score = course['max_score']
                new_score = (new_score / max_score) * 100  # 标准化
                for assignment in course['assignments']:
                    if assignment['score'] is not None:
                        assignment['score'] = new_score
        st.write("模拟调整后的成绩预测：")
        prediction, course_scores = predict_needed_scores(courses, target_avg)
        st.write(prediction)
        plot_score_distribution(course_scores, target_avg)


if __name__ == "__main__":
    main()