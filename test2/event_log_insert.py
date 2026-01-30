import sqlite3
import random
import time
from conf import DB_FILE

# 配置参数
NUM_USERS = 10000  # 模拟 10000 个独立玩家
TOTAL_RECORDS = 1500*12*NUM_USERS  # 总共产生 180 000 000 条开启关卡的记录
START_TIMESTAMP = 1577836800  # 参考图片的起始时间 (约2020年1月)
TIME_RANGE_SECONDS = 3600 * 24 * 365 # 模拟数据分布在 12 个月内


def generate_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 1. 建表
    print("正在创建表 event_log...")

    cursor.execute("DELETE FROM event_log")

    # 2. 生成模拟数据
    print(f"正在生成 {TOTAL_RECORDS} 条模拟数据...")

    # 第一步：生成一批固定的玩家 ID池 (7位数字，如 8373613)
    # 现实中玩家是重复出现的，所以先建立用户池
    user_pool = [random.randint(1000000, 9999999) for _ in range(NUM_USERS)]

    data_batch = []

    for _ in range(TOTAL_RECORDS):
        # 随机从用户池中选一个玩家
        uid = random.choice(user_pool)

        # 随机生成一个时间戳（在起始时间后的3个月内）
        # 增加一点随机扰动模拟真实操作间隔
        ts = START_TIMESTAMP + random.randint(0, TIME_RANGE_SECONDS)

        data_batch.append((uid, ts))

    # 为了模拟日志的自然顺序，通常按时间戳排序（虽然可以乱序插入，但排序后看着更像日志）
    data_batch.sort(key=lambda x: x[1])

    # 3. 批量插入数据 (比一条条插入快很多)
    cursor.executemany("INSERT INTO event_log (user_id, event_timestamp) VALUES (?, ?)", data_batch)

    conn.commit()
    print("数据插入完成。")

    # 4. 验证结果：打印前 10 行，模仿题目图片的效果
    print("\n--- 数据库当前数据预览 (Top 10) ---")
    print(f"{'user_id':<15} | {'event_timestamp':<15}")
    print("-" * 35)

    conn.close()


if __name__ == "__main__":
    generate_data()