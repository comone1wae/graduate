import json
import gradio as gr
import requests
from agent_utils import call_baidu_agent
import re
# ==============================
# 百度 Agent API 配置
# ==============================

# ==============================
# 自定义样式
# ==============================
CUSTOM_CSS = """
.app-container {
    font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
    background: linear-gradient(135deg, #f8f5ff 0%, #fffefc 100%);
}
.title {
    color: #6a1b9a;
    font-size: 2.2em !important;
    font-weight: 600;
    margin-bottom: 0.5em;
}
.description {
    color: #4a148c;
    font-size: 1.1em;
    margin-bottom: 2em;
    opacity: 0.8;
}
.input-textbox textarea {
    font-size: 1.1em;
    padding: 1em;
    border-radius: 10px;
    border: 2px solid #ce93d8;
}
.output-textbox textarea {
    font-size: 1.1em;
    padding: 1em;
    border-radius: 10px;
    background-color: #f3e5f5;
    border: none;
}
.button-primary {
    background-color: #8e24aa !important;
    border-color: #8e24aa !important;
    font-weight: 600;
    padding: 0.6em 1.5em;
    border-radius: 25px;
    transition: all 0.3s ease;
}
.button-primary:hover {
    background-color: #6a1b9a !important;
    transform: scale(1.05);
}
"""


# ==============================
# 封装心理咨询风格
# ==============================
def generate_response(prompt):
    """心理咨询风格包装 + 调用百度 API"""
    base_prompt = (
        "请根据以下 MBTI 问卷结果，分析用户的性格特征、优势与潜在盲点。\n"
    )
    query = base_prompt + prompt
    reply = call_baidu_agent(query)

    return reply

# ==============================
# 读取题库
# ==============================
with open("mbti_questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

# ==============================
# 提交问卷
# ==============================
import re
import gradio as gr

# 假设 questions 和 generate_response 已经定义
# questions = [...]
# from your_module import generate_response

# ==============================
# 提交函数
# ==============================
def submit_answers(*answers):
    result = [{"question": q["question"], "answer": a} for q, a in zip(questions, answers)]

    prompt_text = "以下是 MBTI 测试问卷回答：\n"
    for item in result:
        prompt_text += f"{item['question']} -> {item['answer']}\n"
    prompt_text += "\n请综合分析此人的 MBTI 类型及性格特征。"

    analysis = generate_response(prompt_text)
    
    # 最简版本：直接按第一个换行符分割
    if '\n' in analysis:
        first_line, text = analysis.split('\n', 1)
        link = first_line.replace('[', '').replace(']', '').replace('"', '').strip()
    else:
        link = None
        text = analysis
    
    return text, link


# ==============================
# Gradio 页面函数
# ==============================
def mbti_page():
    with gr.Blocks(css=CUSTOM_CSS, theme=gr.themes.Soft()) as demo:
        gr.Markdown("<div class='title'>🧩 MBTI 性格测试</div>")
        gr.Markdown("<div class='description'>请选择每个问题最符合你的选项，填写完毕后点击“提交”即可查看分析。</div>")

        with gr.Column():
            inputs = [gr.Radio(label=f"Q{i+1}. {q['question']}", choices=q["options"]) for i, q in enumerate(questions)]

        submit_btn = gr.Button("✨ 提交问卷分析", elem_classes="button-primary")
  
        # 两个输出组件：文本 + 图片
        with gr.Row():
            output_txt = gr.Textbox(label="MBTI 分析结果", lines=20, show_copy_button=True, elem_classes="output-textbox")
            output_img = gr.Image(label="MBTI 性格镜像结果", elem_classes="output-image", height=400)

        # 点击提交后同时输出文字与图片
        submit_btn.click(
            fn=submit_answers,
            inputs=inputs,
            outputs=[output_txt, output_img]  # 注意这里
        )

    return demo


# ==============================
# 独立运行测试
# ==============================
if __name__ == "__main__":
    mbti_page().launch()
