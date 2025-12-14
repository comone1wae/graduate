import gradio as gr
import mysql.connector
import pandas as pd
from datetime import datetime
# main.py
from database import fetch_reports



# ==============================
# 2️⃣ 报告过滤函数
# ==============================
def filter_reports(topic_keyword, emotion_label, start_date, end_date):
    df = fetch_reports()
    if topic_keyword:
        df = df[df["topic"].str.contains(topic_keyword, case=False, na=False)]
    if emotion_label and emotion_label != "All":
        df = df[df["emotion_label"] == emotion_label]

    # 处理日期范围过滤
    if start_date:
        start_date = pd.to_datetime(start_date)
        df = df[df["created_at"] >= start_date]
    if end_date:
        end_date = pd.to_datetime(end_date)
        end_date = end_date.replace(hour=23, minute=59, second=59)
        df = df[df["created_at"] <= end_date]

    return df[["id", "created_at", "topic", "emotion_label", "emotion_score", "stress_level"]]

# ==============================
# 3️⃣ 报告详情显示
# ==============================
def show_report_detail(report_id):
    df = fetch_reports()
    if df.empty:
        return "未找到任何报告记录"

    row = df[df["id"] == int(report_id)]
    if row.empty:
        return f"报告 ID {report_id} 不存在"

    row = row.iloc[0]

    # 安全解析
    try:
        core_issues = eval(row["core_issues"]) if pd.notna(row["core_issues"]) else []
        ai_suggestions = eval(row["ai_suggestions"]) if pd.notna(row["ai_suggestions"]) else []
    except Exception:
        core_issues, ai_suggestions = [], []

    core_issues_text = "\n".join([f"- {i}" for i in core_issues]) or "无数据"
    ai_suggestions_text = "\n".join([f"- {s}" for s in ai_suggestions]) or "无数据"

    md = f"""
    ## 🧾 心理咨询报告 - {row['created_at']}
    **主题**：{row['topic']}  
    **情绪标签**：{row['emotion_label']}  
    **情绪评分**：{row['emotion_score']} / 5  
    **压力值**：{row['stress_level']} / 100  
    ---

    ### 🧩 核心问题
    {core_issues_text}

    ### 💡 AI 建议
    {ai_suggestions_text}

    ### 🗣️ 对话摘录
    > {row['conversation_text'] if pd.notna(row['conversation_text']) else '无对话内容'}
    """
    return md

# ==============================
# 4️⃣ 页面功能函数
# ==============================
def query_reports(topic_keyword, emotion_label, start_date, end_date):
    return filter_reports(topic_keyword, emotion_label, start_date, end_date)

def reset_filters():
    return "", "All", "", ""

def load_initial_data():
    return filter_reports("", "All", "", "")

# ==============================
# 5️⃣ Gradio 页面模块函数（主函数）
# ==============================
def history_page():
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 📜 心理咨询历史档案")
        gr.Markdown("在这里可以按主题、情绪或日期筛选历史咨询报告，并查看详情。")

        with gr.Row():
            topic_input = gr.Textbox(label="🔍 主题关键字", placeholder="输入主题，如：焦虑、家庭、人际关系")
            emotion_dropdown = gr.Dropdown(
                label="🙂 情绪过滤",
                choices=["All", "平静", "焦虑", "愤怒", "疲惫", "紧张"],
                value="All"
            )

        with gr.Row():
            start_date = gr.Textbox(label="📅 开始日期 (YYYY-MM-DD)")
            end_date = gr.Textbox(label="📅 结束日期 (YYYY-MM-DD)")

        with gr.Row():
            search_btn = gr.Button("🔎 搜索报告")
            reset_btn = gr.Button("♻️ 重置筛选")

        reports_df = gr.DataFrame(
            headers=["id", "created_at", "topic", "emotion_label", "emotion_score", "stress_level"],
            label="🧾 历史报告列表",
            interactive=False
        )

        with gr.Row():
            report_id_input = gr.Number(label="报告 ID", value=1, precision=0)
            view_btn = gr.Button("📖 查看详情")

        report_detail = gr.Markdown(label="报告详情")

        # 🔄 交互逻辑
        search_btn.click(query_reports, inputs=[topic_input, emotion_dropdown, start_date, end_date], outputs=[reports_df])
        reset_btn.click(reset_filters, outputs=[topic_input, emotion_dropdown, start_date, end_date])
        view_btn.click(show_report_detail, inputs=[report_id_input], outputs=[report_detail])
        demo.load(load_initial_data, outputs=[reports_df])

    return demo

# ==============================
# 6️⃣ 单独运行调试
# ==============================
if __name__ == "__main__":
    history_page().launch()
