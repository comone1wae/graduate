# agent_utils.py
import requests

# 配置常量
# APP_ID = "3w1mQE2Aq6EpDyddDwb7oX9jBmDSVE6H"
# SECRET_KEY = "5PoAlwDvbVcnHeh5wH1N9NOKi83qsclP"
# URL = "https://agentapi.baidu.com/assistant/getAnswer"

APP_ID = "z8LAANykWw1MhzplcfVrrRUlwDXh1DRI"
SECRET_KEY = "WNHY3vKtWbpj9Rz1cpsOWlayxtSS0Ojp"
URL = "https://agentapi.baidu.com/assistant/getAnswer"
def call_baidu_agent(prompt: str) -> str:
    """调用百度Agent的通用函数"""
    try:
        params = {"appId": APP_ID, "secretKey": SECRET_KEY}
        payload = {
            "message": {"content": {"type": "text", "value": {"showText": prompt}}},
            "source": "gradio_app",
            "from": "openapi",
            "openId": "psychology_user"
        }
        res = requests.post(URL, params=params, headers={"Content-Type": "application/json"}, json=payload)
        data = res.json()
        if data.get("status") == 0:
            return data["data"]["content"][0]["data"].strip()
        return f"❌ 请求失败：{data.get('message', '未知错误')}"
    except Exception as e:
        return f"⚠️ 出错：{e}"