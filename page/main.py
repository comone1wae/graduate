import gradio as gr
from home import home_page
from mbti import mbti_page
from history import history_page
from personal import personal_page

# ======== 加载四个子页面 ========
home = home_page()
mbti = mbti_page()
history = history_page()
personal = personal_page()

# ======== 主界面 ========
with gr.Blocks(title="心理测试系统", theme=gr.themes.Soft()) as demo:
    # --- 导航栏 ---
    with gr.Row(elem_id="nav-bar"):
        gr.Markdown("### 🧭 导航栏")
        btn_home = gr.Button("🏠 主页")
        btn_mbti = gr.Button("🧩 MBTI 测试")
        btn_history = gr.Button("📜 历史档案")
        btn_personal = gr.Button("👤 个人主页")

    # --- 页面容器 ---
    with gr.Column(visible=True) as home_container:
        home.render()
    
    with gr.Column(visible=False) as mbti_container:
        mbti.render()
    
    with gr.Column(visible=False) as history_container:
        history.render()
    
    with gr.Column(visible=False) as personal_container:
        personal.render()

    # --- 页面切换函数 ---
    def show_page(selected_page):
        return [
            gr.update(visible=(selected_page == "home")),
            gr.update(visible=(selected_page == "mbti")),
            gr.update(visible=(selected_page == "history")),
            gr.update(visible=(selected_page == "personal"))
        ]

    # --- 页面切换逻辑 ---
    btn_home.click(
        lambda: show_page("home"),
        outputs=[home_container, mbti_container, history_container, personal_container]
    )
    btn_mbti.click(
        lambda: show_page("mbti"),
        outputs=[home_container, mbti_container, history_container, personal_container]
    )
    btn_history.click(
        lambda: show_page("history"),
        outputs=[home_container, mbti_container, history_container, personal_container]
    )
    btn_personal.click(
        lambda: show_page("personal"),
        outputs=[home_container, mbti_container, history_container, personal_container]
    )

# ======== 启动 ========
if __name__ == "__main__":
    demo.launch()