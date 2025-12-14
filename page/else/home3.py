import gradio as gr
import requests
import json
import gc
from datetime import datetime
import mysql.connector
from mysql.connector import Error
CUSTOM_CSS = """
.title {
    color: #6a1b9a;
    font-size: 2em !important;
    font-weight: 600;
    margin-bottom: 0.5em;
}
"""
chat_history = []
# ==============================
# 百度 Agent API 配置
# ==============================
BAIDU_APP_ID = "3w1mQE2Aq6EpDyddDwb7oX9jBmDSVE6H"
BAIDU_SECRET_KEY = "5PoAlwDvbVcnHeh5wH1N9NOKi83qsclP"
BAIDU_URL = "https://agentapi.baidu.com/assistant/getAnswer"



# ==============================
# 百度Agent调用
# ==============================
def call_baidu_agent(prompt: str) -> str:
    try:
        params = {"appId": BAIDU_APP_ID, "secretKey": BAIDU_SECRET_KEY}
        payload = {
            "message": {"content": {"type": "text", "value": {"showText": prompt}}},
            "source": "gradio_app",
            "from": "openapi",
            "openId": "psychology_user"
        }
        res = requests.post(BAIDU_URL, params=params, headers={"Content-Type": "application/json"}, json=payload)
        data = res.json()
        if data.get("status") == 0:
            return data["data"]["content"][0]["data"].strip()
        return f"❌ 请求失败：{data.get('message', '未知错误')}"
    except Exception as e:
        return f"⚠️ 出错：{e}"

# ==============================
# 咨询与报告函数
# ==============================
def generate_response(prompt):
    base_prompt = (
        "你是一位温暖、专业、富有同理心的心理咨询师。\n"
        "请用温和、支持性的语言回应用户，提供正向引导和建议。\n"
        "避免直接诊断，鼓励表达与自我觉察。\n"
        "每次回答结尾加上：\n\n【温馨提示】如果你需要更专业的帮助，请考虑联系心理咨询师。\n\n"
    )
    query = base_prompt + prompt
    return call_baidu_agent(query)

def predict(question):
    global chat_history
    question = question.strip()
    if not question:
        return "请输入你的困扰..."
    reply = generate_response(question)
    chat_history.append((question, reply))
    gc.collect()
    return reply

def generate_report():
    global chat_history
    if not chat_history:
        return "⚠️ 当前没有对话记录，请先进行咨询。"
    conversation_text = "\n".join([f"用户：{u}\n心理咨询AI：{a}" for u, a in chat_history])
    prompt = f"""
你是一位专业心理咨询总结助手。
请阅读以下咨询对话并输出严格JSON格式报告：
{{
  "topic": "主题或主要问题",
  "emotion_label": "主要情绪",
  "emotion_score": 0-5,
  "stress_level": 0-100,
  "core_issues": ["..."],
  "ai_suggestions": ["..."]
}}
对话如下：
{conversation_text}
"""
    result = call_baidu_agent(prompt)
    try:
        clean_result = result.strip().removeprefix("```json").removesuffix("```").strip()
        report_json = json.loads(clean_result)
        formatted = json.dumps(report_json, ensure_ascii=False, indent=2)
        display_text = f"🧾 心理咨询总结报告\n\n{formatted}"
    except Exception as e:
        display_text = f"⚠️ JSON解析失败：{e}\n原始结果：{result}"
    chat_history.clear()
    gc.collect()
    return display_text

# ==============================
# 页面函数（供 main.py 调用）
# ==============================
def home_page():
    with gr.Blocks(theme=gr.themes.Soft(primary_hue="purple"), css=CUSTOM_CSS) as demo:
        gr.HTML("<div class='title'>🧠 心灵守护者 - 百度Agent心理咨询</div>")

        with gr.Row():
            with gr.Column(scale=2):
                question_input = gr.Textbox(lines=3, placeholder="分享你的困扰...", label="当前状态/问题")
                with gr.Row():
                    submit_btn = gr.Button("发送咨询", variant="primary")
                    clear_btn = gr.Button("清除内容", variant="secondary")
                    end_btn = gr.Button("生成咨询总结", variant="stop")

                chat_count = gr.Textbox(value="当前对话轮数：0", label="对话统计", interactive=False)
            with gr.Column(scale=3):
                output_box = gr.Textbox(lines=15, label="AI回复 / 咨询总结报告", show_copy_button=True)

        def update_chat_count():
            return f"当前对话轮数：{len(chat_history)}"

        submit_btn.click(predict, inputs=question_input, outputs=output_box).then(update_chat_count, outputs=chat_count)
        clear_btn.click(lambda: ("", ""), None, [question_input, output_box]).then(update_chat_count, outputs=chat_count)
        end_btn.click(generate_report, outputs=output_box).then(lambda: "当前对话轮数：0", outputs=chat_count)

    return demo
