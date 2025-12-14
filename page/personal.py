import gradio as gr
import pymysql
import pandas as pd
import matplotlib.pyplot as plt
import json
import re
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
# 数据读取函数
# ==============================
def fetch_data():
    conn = pymysql.connect(**DB_CONFIG)
    query = "SELECT * FROM session_reports_main ORDER BY created_at ASC"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ==============================
# 概况统计函数
# ==============================
def get_overview(df):
    if df.empty:
        return "<p>No data available.</p>"

    latest = df.iloc[-1]
    avg_emotion = df["emotion_score"].mean()
    avg_stress = df["stress_level"].mean()

    overview_md = f"""
    <div style='font-size:16px'>
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
import json
from agent_utils import call_baidu_agent  # 你之前已经在项目中用过的 Baidu Agent 调用函数
def ai_analyze_trends(df):
    """
    用 AI 模型分析情绪和压力趋势
    """
    if df.empty:
        return "暂无数据，无法生成分析。", "请先完成至少一次心理测评。"

    # ✅ 修复：将 Timestamp 转为字符串，避免 json.dumps 报错
    df = df.copy()
    df["created_at"] = df["created_at"].astype(str)

    # 提取必要字段
    records = df[["created_at", "emotion_label", "emotion_score", "stress_level"]].to_dict(orient="records")

    # 汇总信息
    summary = {
        "avg_emotion": round(df["emotion_score"].mean(), 2),
        "avg_stress": round(df["stress_level"].mean(), 2),
        "last_emotion": df.iloc[-1]["emotion_label"],
        "session_count": len(df)
    }

    # 构造 prompt
    prompt = f"""
你是一名专业心理趋势分析AI。
以下是用户的历史心理数据，请分析趋势并输出JSON格式结果：
{json.dumps({"records": records, "summary": summary}, ensure_ascii=False, indent=2)}

输出格式示例：
{{
  "analysis": "过去一周情绪总体下降，压力上升。",
  "advice": "建议保持规律作息，进行适度运动。",
  "trend_summary": "情绪下降，压力升高"
}}
    """

    try:
        result = call_baidu_agent(prompt)
        print('asdhias', result)
        
        # 使用正则表达式提取 JSON 部分
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            parsed = json.loads(json_str)
            analysis = parsed.get("analysis", "未提供分析。")
            advice = parsed.get("advice", "未提供建议。")
        else:
            analysis, advice = "未找到有效数据", "未找到有效数据"
        return analysis, advice
    except json.JSONDecodeError:
        # AI 返回非 JSON 时
        return "AI 分析结果格式异常。", result
    except Exception as e:
        # 其他错误
        return "AI 分析失败，请稍后再试。", str(e)


# ==============================
# 主逻辑：生成页面内容
# ==============================
def load_dashboard():
    df = fetch_data()
    overview = get_overview(df)
    fig1 = plot_emotion_trend(df)
    fig2 = plot_dual_axis(df)
    return overview, fig1, fig2

# ==============================
# Gradio 页面函数
# ==============================
def personal_page():
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🩵 Personal Psychological Dashboard")

        with gr.Row():
            overview_html = gr.HTML()

        with gr.Row():
            fig_emotion = gr.Plot(label="Emotion Trend")
            fig_compare = gr.Plot(label="Emotion vs Stress")

        # 🔹 新增区域：AI 趋势分析模块
        with gr.Accordion("🧠 AI 情绪与压力趋势分析", open=True):
            ai_analysis_box = gr.Textbox(label="AI Analysis", lines=4, interactive=False)
            ai_advice_box = gr.Textbox(label="AI Advice", lines=4, interactive=False)
            ai_btn = gr.Button("✨ 生成AI分析")

        # 原有刷新按钮
        refresh_btn = gr.Button("🔄 Refresh Data")

        # 定义刷新逻辑
        refresh_btn.click(fn=load_dashboard, outputs=[overview_html, fig_emotion, fig_compare])

        # 定义 AI 分析按钮逻辑
        ai_btn.click(fn=lambda: ai_analyze_trends(fetch_data()), 
                     outputs=[ai_analysis_box, ai_advice_box])

        # 页面加载自动显示概况和图表
        demo.load(fn=load_dashboard, outputs=[overview_html, fig_emotion, fig_compare])

    return demo

