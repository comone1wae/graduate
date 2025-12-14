import gradio as gr
import pymysql
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
# main.py
from database import fetch_reports


# ==============================
# 数据库配置
# ==============================
# DB_CONFIG = {
#     "host": "localhost",
#     "user": "root",
#     "password": "112233",
#     "database": "heartreport",
#     "charset": "utf8mb4"
# }


# ==============================
# 数据读取函数
# ==============================
# def fetch_data():
#     conn = pymysql.connect(**DB_CONFIG)
#     query = "SELECT * FROM session_reports_main ORDER BY created_at ASC"
#     df = pd.read_sql(query, conn)
#     conn.close()
#     return df


# ==============================
# 概况统计函数
# ==============================
def get_overview(df):
    latest = df.iloc[-1]
    avg_emotion = df["emotion_score"].mean()
    avg_stress = df["stress_level"].mean()

    overview_md = f"""
    <div>
        <h3>🧠 User Mental Overview</h3>
        <p>😐 <b>Latest Emotion:</b> {latest['emotion_label']}</p>
        <p>💓 <b>Average Emotion Score:</b> {avg_emotion:.2f} / 5</p>
        <p>⚡ <b>Average Stress Level:</b> {avg_stress:.1f} / 100</p>
        <p>🕒 <b>Last Session Time:</b> {latest['created_at']}</p>
    </div>
    """
    return overview_md


# ==============================
# 图表 1：情绪趋势图
# ==============================
def plot_emotion_trend(df):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(df["created_at"], df["emotion_score"], marker="o", color="blue", label="Emotion Score")
    ax.fill_between(df["created_at"], df["stress_level"]/20, alpha=0.2, color="red", label="Stress Level / 20")
    ax.set_title("Emotion Trend", fontsize=14)
    ax.set_xlabel("Time")
    ax.set_ylabel("Emotion Score")
    ax.legend()
    fig.autofmt_xdate()
    return fig


# ==============================
# 图表 2：压力趋势与情绪对比
# ==============================
def plot_dual_axis(df):
    fig, ax1 = plt.subplots(figsize=(6, 4))

    ax2 = ax1.twinx()
    ax1.plot(df["created_at"], df["emotion_score"], color="blue", marker="o", label="Emotion Score")
    ax2.plot(df["created_at"], df["stress_level"], color="red", linestyle="--", label="Stress Level")

    ax1.set_xlabel("Time")
    ax1.set_ylabel("Emotion Score", color="blue")
    ax2.set_ylabel("Stress Level", color="red")
    ax1.set_title("Emotion vs Stress Trend")
    fig.autofmt_xdate()

    return fig


# ==============================
# 主逻辑：生成页面
# ==============================
def load_dashboard():
    df = fetch_reports()
    overview = get_overview(df)
    fig1 = plot_emotion_trend(df)
    fig2 = plot_dual_axis(df)
    return overview, fig1, fig2


# ==============================
# Gradio界面
# ==============================
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🩵 Personal Psychological Dashboard")

    with gr.Row():
        overview_html = gr.HTML(label="User Overview")

    with gr.Row():
        fig_emotion = gr.Plot(label="Emotion Trend")
        fig_compare = gr.Plot(label="Emotion vs Stress")

    refresh_btn = gr.Button("🔄 Refresh Data")
    refresh_btn.click(fn=load_dashboard, outputs=[overview_html, fig_emotion, fig_compare])
    
    # 默认首次加载
    demo.load(fn=load_dashboard, outputs=[overview_html, fig_emotion, fig_compare])

if __name__ == "__main__":
    demo.launch()
