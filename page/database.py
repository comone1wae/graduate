# database.py
import mysql.connector
import pandas as pd

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
# 1️⃣ 数据获取函数
# ==============================
def fetch_reports():
    conn = mysql.connector.connect(**DB_CONFIG)
    query = "SELECT * FROM session_reports_main ORDER BY created_at DESC"
    df = pd.read_sql(query, conn)
    conn.close()
    return df