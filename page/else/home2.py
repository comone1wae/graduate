import gradio as gr
import requests
import json
import gc
from datetime import datetime
import mysql.connector
from mysql.connector import Error

# ==============================
# 百度 Agent API 配置
# ==============================
BAIDU_APP_ID = "3w1mQE2Aq6EpDyddDwb7oX9jBmDSVE6H"
BAIDU_SECRET_KEY = "5PoAlwDvbVcnHeh5wH1N9NOKi83qsclP"
BAIDU_URL = "https://agentapi.baidu.com/assistant/getAnswer"

# ==============================
# 全局对话记录
# ==============================
chat_history = []  # 存储 [(用户, AI回复), ...]

# ==============================
# 自定义样式
# ==============================
CUSTOM_CSS = """
.title {
    color: #6a1b9a;
    font-size: 2em !important;
    font-weight: 600;
    margin-bottom: 0.5em;
}
"""

# ==============================
# 调用百度 Agent API
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
        headers = {"Content-Type": "application/json"}
        res = requests.post(BAIDU_URL, params=params, headers=headers, json=payload)
        data = res.json()
        if data.get("status") == 0:
            return data["data"]["content"][0]["data"].strip()
        return f"❌ 请求失败：{data.get('message', '未知错误')}"
    except Exception as e:
        return f"⚠️ 出错：{e}"

# ==============================
# 心理咨询回复
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

# ==============================
# 对话推理函数
# ==============================
def predict(question):
    """单轮对话推理"""
    global chat_history
    question = question.strip()
    if not question:
        return "请输入你的困扰..."

    reply = generate_response(question)
    chat_history.append((question, reply))  # 保存记录
    gc.collect()
    return reply

# ==============================
# 生成结构化总结报告
# ==============================
def generate_report():
    """生成心理咨询总结报告，并保存到 MySQL 数据库"""
    global chat_history

    if not chat_history:
        return "⚠️ 当前没有对话记录，请先进行咨询。"

    # 1️⃣ 拼接完整对话内容
    conversation_text = ""
    for user, ai in chat_history:
        conversation_text += f"用户：{user}\n心理咨询AI：{ai}\n\n"

    # 2️⃣ 生成报告提示词
    prompt = f"""
你是一位专业的心理咨询总结助手。
请阅读以下完整咨询对话内容，并生成结构化心理咨询报告。
报告应帮助用户回顾此次交流的重点、情绪、建议与后续方向。
请输出如下JSON格式（严格JSON格式）：

{{
  "主题": "...",
  "用户情绪": "...",
  "核心问题": ["..."],
  "AI建议": ["..."],
  "后续关注点": "..."
}}

对话内容如下：
{conversation_text}
"""

    # 3️⃣ 调用百度模型生成报告
    result = call_baidu_agent(prompt)
    report_json = None

    # 4️⃣ 尝试解析JSON
    clean_result = result.strip()
    if clean_result.startswith("```json"):
        clean_result = clean_result[len("```json"):].strip()
    if clean_result.endswith("```"):
        clean_result = clean_result[:-3].strip()

    # 尝试解析
    try:
        report_json = json.loads(clean_result)
        formatted = json.dumps(report_json, ensure_ascii=False, indent=2)
        display_text = f"🧾 心理咨询总结报告\n\n{formatted}"
    except Exception as e:
        report_json = None  # 解析失败
        display_text = f"🧾 心理咨询总结报告\n\n{result}"

    # 5️⃣ 保存进 MySQL 数据库
    try:
        connection = mysql.connector.connect(
            host="localhost",           # 根据实际情况改
            user="root",                # 你的 MySQL 用户名
            password="112233",         # 你的 MySQL 密码
            database="heartreport",     # 数据库名
            charset="utf8mb4"
        )

        if connection.is_connected():
            cursor = connection.cursor()
            session_id = datetime.now().strftime("%Y%m%d%H%M%S")
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                INSERT INTO session_reports (user_id, session_id, created_at, report_json, raw_text)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                "psychology_user",
                session_id,
                created_at,
                json.dumps(report_json, ensure_ascii=False) if report_json else None,
                result
            ))

            connection.commit()
            cursor.close()
            connection.close()

            display_text += f"\n\n💾 报告已保存到数据库（会话ID：{session_id}）"
    except Error as e:
        display_text += f"\n⚠️ 数据库保存失败：{e}"

    # 6️⃣ 清理缓存
    chat_history.clear()
    gc.collect()

    return display_text





# ==============================
# 创建 Gradio 界面
# ==============================
def create_interface():
    with gr.Blocks(theme=gr.themes.Soft(primary_hue="purple"), css=CUSTOM_CSS) as demo:
        gr.HTML("<div class='title'>🧠 心灵守护者 - 百度Agent心理咨询</div>")

        with gr.Row():
            with gr.Column(scale=2):
                question_input = gr.Textbox(
                    lines=3, placeholder="分享你的困扰...", label="当前状态/问题"
                )

                with gr.Row():
                    submit_btn = gr.Button("发送咨询", variant="primary")
                    clear_btn = gr.Button("清除内容", variant="secondary")
                    end_btn = gr.Button("生成咨询总结", variant="stop")  # 使用stop样式突出显示

                examples = gr.Examples(
                    examples=[
                        ["最近总是失眠，睡不着觉"],
                        ["和恋人吵架后心情很糟糕"],
                        ["工作压力大，感觉喘不过气"],
                        ["经常感到焦虑不安，不知道为什么"],
                        ["想改善和父母的沟通方式"]
                    ],
                    inputs=question_input,
                    label="常见咨询场景"
                )

                # 添加对话计数显示
                chat_count = gr.Textbox(
                    value="当前对话轮数：0",
                    label="对话统计",
                    interactive=False
                )

            with gr.Column(scale=3):
                output_box = gr.Textbox(
                    lines=15,  # 增加行数以容纳更长的报告
                    label="AI回复 / 咨询总结报告", 
                    show_copy_button=True
                )

        # 更新对话计数的函数
        def update_chat_count():
            return f"当前对话轮数：{len(chat_history)}"

        # 事件绑定
        submit_btn.click(
            fn=predict,
            inputs=question_input,
            outputs=output_box
        ).then(
            fn=update_chat_count,
            outputs=chat_count
        )
        
        clear_btn.click(
            lambda: ("", "请输入你的困扰..."), 
            None, 
            [question_input, output_box]
        ).then(
            fn=update_chat_count,
            outputs=chat_count
        )
        
        end_btn.click(
            fn=generate_report,
            outputs=output_box
        ).then(
            fn=lambda: "当前对话轮数：0",
            outputs=chat_count
        )

    return demo

# ==============================
# 启动
# ==============================
if __name__ == "__main__":
    demo = create_interface()
    demo.launch()