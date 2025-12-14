import json
import gradio as gr
import requests
# 假设 generate_response 已经按你提供的方式导入
# from your_model_file import generate_response
BAIDU_APP_ID = "3w1mQE2Aq6EpDyddDwb7oX9jBmDSVE6H"
BAIDU_SECRET_KEY = "5PoAlwDvbVcnHeh5wH1N9NOKi83qsclP"  # 你的 secretKey
BAIDU_URL = "https://agentapi.baidu.com/assistant/getAnswer"

# ==============================
# 自定义样式（保持原有美观）
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
.example {
    border: 1px solid #e0e0e0;
    padding: 0.8em;
    border-radius: 12px;
    transition: all 0.3s ease;
}
.example:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(106, 27, 154, 0.1);
    background-color: #f3e5f5;
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
# 调用百度 Agent API
# ==============================
def call_baidu_agent(prompt: str) -> str:
    """调用百度 Agent API"""
    try:
        params = {
            "appId": BAIDU_APP_ID,
            "secretKey": BAIDU_SECRET_KEY
        }

        payload = {
            "message": {
                "content": {
                    "type": "text",
                    "value": {"showText": prompt}
                }
            },
            "source": "gradio_app",
            "from": "openapi",
            "openId": "psychology_user"
        }

        headers = {"Content-Type": "application/json"}

        res = requests.post(BAIDU_URL, params=params, headers=headers, json=payload)
        res.raise_for_status()
        data = res.json()

        if data.get("status") == 0:
            answer = data["data"]["content"][0]["data"]
            return answer.strip()
        else:
            return f"❌ 请求失败：{data.get('message', '未知错误')}"

    except Exception as e:
        return f"⚠️ 出错：{e}"

# ==============================
# 心理咨询生成函数
# ==============================
def generate_response(prompt):
    """心理咨询风格包装 + 调用百度 API"""
    base_prompt = (
        "你是一位温暖、专业、富有同理心的心理咨询师。\n"
        "请用温和、支持性的语言回应用户，提供正向引导和建议。\n"
        "避免直接诊断，鼓励表达与自我觉察。\n"
        "每次回答结尾加上：\n\n【温馨提示】如果你需要更专业的帮助，请考虑联系心理咨询师。\n\n"
    )
    query = base_prompt + prompt
    reply = call_baidu_agent(query)

    # 确保提示语存在
    if "【温馨提示】" not in reply:
        reply += "\n\n【温馨提示】如果你需要更专业的帮助，请考虑联系心理咨询师。"

    return reply
# -----------------------------
# 1️⃣ 读取题库
# -----------------------------
with open("mbti_questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

# -----------------------------
# 2️⃣ 提交问卷函数
# -----------------------------
def submit_answers(*answers):
    # 构建结果列表（可选，方便存储/调试）
    result = []
    for q, a in zip(questions, answers):
        result.append({"question": q["question"], "answer": a})
    
    # -----------------------------
    # 生成 prompt 给模型
    # -----------------------------
    prompt_text = "以下 为MBTI 问卷\n"
    # prompt_text += "请根据以下 MBTI 问卷回答分析用户性格：\n\n"
    for item in result:
        prompt_text += f"{item['question']} -> {item['answer']}\n"
    prompt_text += "\n这是一个mbti测试问卷。"
    print(prompt_text)
    # 调用你已有的百度 Agent API 封装函数
    analysis = generate_response(prompt_text)

    return analysis

# -----------------------------
# 3️⃣ 构建 Gradio 界面
# -----------------------------
inputs = [gr.Radio(label=f"Q{i+1}. {q['question']}", choices=q["options"]) for i, q in enumerate(questions)]
output = gr.Textbox(label="MBTI 分析结果（来自模型）", lines=20, show_copy_button=True)

iface = gr.Interface(
    fn=submit_answers,
    inputs=inputs,
    outputs=output,
    title="MBTI 测试问卷",
    description="请选择每个问题最符合你的选项，填写完毕后点击“提交”即可查看性格分析。"
)

# -----------------------------
# 4️⃣ 启动页面
# -----------------------------
if __name__ == "__main__":
    iface.launch()
