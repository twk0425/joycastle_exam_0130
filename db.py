import sqlite3
from conf import DB_FILE
import os

def execute_sql(mysql):
    """初始化数据库：创建用户表，插入测试用户（仅首次运行时执行）"""
    # 连接数据库（不存在则自动创建）
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(mysql)
    op=cursor.fetchall()
    cursor.close()
    conn.close()
    return op