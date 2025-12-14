import gradio as gr
import mysql.connector
import pandas as pd
from datetime import datetime
import os

# ==============================
# 数据库配置
# ==============================
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "112233",
    "database": "heartreport",
    "charset": "utf8mb4"
}

# ==============================
# 1️⃣ 数据获取函数
# ==============================
def fetch_reports():
    conn = mysql.connector.connect(**DB_CONFIG)
    query = "SELECT * FROM session_reports_main ORDER BY created_at DESC"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

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
        # 将结束日期设置为当天的最后一刻
        end_date = end_date.replace(hour=23, minute=59, second=59)
        df = df[df["created_at"] <= end_date]
    
    return df[["id", "created_at", "topic", "emotion_label", "emotion_score", "stress_level"]]

# ==============================
# 3️⃣ 报告详情显示
# ==============================
def show_report_detail(report_id):
    df = fetch_reports()
    if df.empty:
        return "未找到对应的报告"
    
    row = df[df["id"] == int(report_id)]
    if row.empty:
        return "报告ID不存在"
    
    row = row.iloc[0]

    # 安全地处理可能为空的字段
    core_issues = eval(row["core_issues"]) if pd.notna(row["core_issues"]) else []
    ai_suggestions = eval(row["ai_suggestions"]) if pd.notna(row["ai_suggestions"]) else []
    
    core_issues_text = "\n".join([f"- {i}" for i in core_issues])
    ai_suggestions_text = "\n".join([f"- {s}" for s in ai_suggestions])

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
# 4️⃣ 主界面布局
# ==============================
def query_reports(topic_keyword, emotion_label, start_date, end_date):
    df = filter_reports(topic_keyword, emotion_label, start_date, end_date)
    return df

def reset_filters():
    return "", "All", "", ""

def load_initial_data():
    return filter_reports("", "All", "", "")

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 📜 History Archive — 心理咨询历史档案")

    with gr.Row():
        topic_input = gr.Textbox(label="🔍 Topic Keyword", placeholder="输入主题关键字，如：焦虑、工作、家庭")
        emotion_dropdown = gr.Dropdown(label="🙂 Emotion Filter", choices=["All", "平静", "焦虑", "愤怒", "疲惫", "紧张"], value="All")
    
    with gr.Row():
        start_date = gr.Textbox(label="📅 Start Date (YYYY-MM-DD)", placeholder="开始日期，如：2024-01-01")
        end_date = gr.Textbox(label="📅 End Date (YYYY-MM-DD)", placeholder="结束日期，如：2024-12-31")
    
    with gr.Row():
        search_btn = gr.Button("🔎 Search")
        reset_btn = gr.Button("♻️ Reset")

    reports_df = gr.DataFrame(
        headers=["id", "created_at", "topic", "emotion_label", "emotion_score", "stress_level"],
        label="🧾 历史报告列表",
        interactive=False
    )

    with gr.Row():
        report_id_input = gr.Number(label="Report ID", value=1, precision=0)
        view_btn = gr.Button("📖 查看详情")

    report_detail = gr.Markdown(label="Report Detail")

    # 点击搜索
    search_btn.click(query_reports, inputs=[topic_input, emotion_dropdown, start_date, end_date], outputs=[reports_df])
    reset_btn.click(reset_filters, outputs=[topic_input, emotion_dropdown, start_date, end_date])

    # 查看详情
    view_btn.click(show_report_detail, inputs=[report_id_input], outputs=[report_detail])

    # 默认加载最近报告
    demo.load(load_initial_data, outputs=[reports_df])

if __name__ == "__main__":
    demo.launch()