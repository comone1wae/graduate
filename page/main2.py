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

# ======== CSS样式 ========
custom_css = """
#nav-bar {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    padding: 15px 20px;
    border-radius: 15px;
    margin-bottom: 20px;
    border: 1px solid #2d4263;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.nav-title {
    color: #e94560 !important;
    font-weight: 700;
    font-size: 24px !important;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    gap: 10px;
}

.nav-buttons {
    display: flex;
    gap: 10px;
    align-items: center;
}

.nav-button {
    background: linear-gradient(135deg, #2d4263 0%, #1a1a2e 100%) !important;
    color: white !important;
    border: 1px solid #e94560 !important;
    border-radius: 25px !important;
    padding: 10px 20px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

.nav-button:hover {
    background: linear-gradient(135deg, #e94560 0%, #2d4263 100%) !important;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(233, 69, 96, 0.4) !important;
}

.system-name {
    background: linear-gradient(45deg, #e94560, #f39c12);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 800;
    font-size: 26px;
}
"""

# ======== 主界面 ========
with gr.Blocks(
    title="心灵守护者 - 心理测试系统", 
    theme=gr.themes.Soft(primary_hue="purple"),
    css=custom_css
) as demo:
    
    # --- 导航栏 ---
    with gr.Row(elem_id="nav-bar"):
        with gr.Column(scale=2):
            gr.HTML("""
            <div class="nav-title">
                <span>🧠</span>
                <span class="system-name">心灵守护者</span>
                <span>| 心理测试系统</span>
            </div>
            """)
        
        with gr.Column(scale=3):
            with gr.Row(elem_classes="nav-buttons"):
                btn_home = gr.Button("🏠 主页", elem_classes="nav-button")
                btn_mbti = gr.Button("🧩 MBTI 测试", elem_classes="nav-button")
                btn_history = gr.Button("📜 历史档案", elem_classes="nav-button")
                btn_personal = gr.Button("👤 个人主页", elem_classes="nav-button")

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