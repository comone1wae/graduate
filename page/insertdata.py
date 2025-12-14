import mysql.connector
import json
from datetime import datetime

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
# 模拟数据（10条）
# ==============================
mock_data = [
    {
        "session_id": "20251018100101",
        "topic": "工作压力与焦虑",
        "emotion_label": "焦虑",
        "emotion_score": 2.1,
        "stress_level": 78,
        "core_issues": ["工作任务过重", "缺乏上级支持"],
        "ai_suggestions": ["尝试分解任务", "保持规律作息", "进行呼吸放松训练"],
        "conversation_text": "用户：最近任务太多，总是焦虑。\n心理咨询AI：我们可以从调整时间管理开始……"
    },
    {
        "session_id": "20251018100202",
        "topic": "恋爱关系不稳定",
        "emotion_label": "伤心",
        "emotion_score": 1.8,
        "stress_level": 65,
        "core_issues": ["沟通不足", "安全感缺失"],
        "ai_suggestions": ["表达真实感受", "建立信任沟通", "设定边界"],
        "conversation_text": "用户：我们最近总吵架。\n心理咨询AI：可能需要探讨双方的情绪表达方式……"
    },
    {
        "session_id": "20251018100303",
        "topic": "家庭矛盾与亲子冲突",
        "emotion_label": "愤怒",
        "emotion_score": 1.5,
        "stress_level": 82,
        "core_issues": ["父母控制欲强", "情绪表达失衡"],
        "ai_suggestions": ["建立对话机制", "学习情绪调节技巧"],
        "conversation_text": "用户：父母总干涉我的决定。\n心理咨询AI：这种情绪是可以理解的，我们来看看怎样表达更有效……"
    },
    {
        "session_id": "20251018100404",
        "topic": "职业方向迷茫",
        "emotion_label": "困惑",
        "emotion_score": 2.8,
        "stress_level": 55,
        "core_issues": ["缺乏目标", "对未来不确定感"],
        "ai_suggestions": ["设立短期目标", "列出兴趣清单", "寻找导师指导"],
        "conversation_text": "用户：我不知道该不该换工作。\n心理咨询AI：我们可以先评估你的价值观与长期目标……"
    },
    {
        "session_id": "20251018100505",
        "topic": "自我价值感低落",
        "emotion_label": "自卑",
        "emotion_score": 1.9,
        "stress_level": 72,
        "core_issues": ["他人评价敏感", "过度自我批评"],
        "ai_suggestions": ["列出自身优点", "练习积极自我对话"],
        "conversation_text": "用户：我觉得自己不如别人。\n心理咨询AI：可以尝试重塑自我评价体系……"
    },
    {
        "session_id": "20251018100606",
        "topic": "社交焦虑与孤独感",
        "emotion_label": "紧张",
        "emotion_score": 2.2,
        "stress_level": 70,
        "core_issues": ["社交恐惧", "缺乏自信"],
        "ai_suggestions": ["从小型社交开始", "练习眼神交流", "记录社交成功经验"],
        "conversation_text": "用户：我在人多的场合会很紧张。\n心理咨询AI：那我们可以练习逐步暴露法……"
    },
    {
        "session_id": "20251018100707",
        "topic": "学习压力与拖延",
        "emotion_label": "沮丧",
        "emotion_score": 2.5,
        "stress_level": 68,
        "core_issues": ["任务规划不清晰", "缺乏内在动机"],
        "ai_suggestions": ["使用番茄工作法", "建立奖励机制"],
        "conversation_text": "用户：我总是拖延复习。\n心理咨询AI：我们可以试试设定更小的学习目标……"
    },
    {
        "session_id": "20251018100808",
        "topic": "睡眠障碍与失眠",
        "emotion_label": "疲惫",
        "emotion_score": 1.6,
        "stress_level": 80,
        "core_issues": ["入睡困难", "思维活跃过度"],
        "ai_suggestions": ["固定入睡时间", "避免睡前使用电子设备", "练习呼吸放松法"],
        "conversation_text": "用户：晚上总是睡不着。\n心理咨询AI：可以先调整睡眠环境与习惯……"
    },
    {
        "session_id": "20251018100909",
        "topic": "情绪恢复与积极转变",
        "emotion_label": "平静",
        "emotion_score": 4.1,
        "stress_level": 35,
        "core_issues": ["学会情绪觉察", "提升自我接纳"],
        "ai_suggestions": ["持续正念冥想", "保持运动", "记录每日情绪"],
        "conversation_text": "用户：最近我能更快冷静下来了。\n心理咨询AI：非常好，这说明你的情绪调节能力在提升……"
    },
    {
        "session_id": "20251018101010",
        "topic": "目标设定与成长规划",
        "emotion_label": "积极",
        "emotion_score": 4.5,
        "stress_level": 25,
        "core_issues": ["目标清晰", "行动力增强"],
        "ai_suggestions": ["继续执行阶段计划", "定期回顾成果"],
        "conversation_text": "用户：我感觉自己越来越有方向。\n心理咨询AI：保持这种动力，我们一起规划下一步目标……"
    }
]

# ==============================
# 插入数据库
# ==============================
def insert_mock_data():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        for d in mock_data:
            cursor.execute("""
                INSERT INTO session_reports_main
                (session_id, created_at, topic, emotion_label, emotion_score, stress_level, core_issues, ai_suggestions, conversation_text)
                VALUES (%s, NOW(), %s, %s, %s, %s, %s, %s, %s)
            """, (
                d["session_id"],
                d["topic"],
                d["emotion_label"],
                d["emotion_score"],
                d["stress_level"],
                json.dumps(d["core_issues"], ensure_ascii=False),
                json.dumps(d["ai_suggestions"], ensure_ascii=False),
                d["conversation_text"]
            ))

        connection.commit()
        print("✅ 成功插入 10 条测试数据！")

    except mysql.connector.Error as e:
        print(f"⚠️ 数据库错误：{e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# ==============================
# 主程序入口
# ==============================
if __name__ == "__main__":
    insert_mock_data()
