import sqlite3
import time
import numpy as np

DB_FILE = 'twk0425.db'

# 配置参数
NUM_USERS = 10000  # 玩家池大小
TOTAL_RECORDS = 1500*12*NUM_USERS  # 1.8亿条数据
BATCH_SIZE = 2_000_000  # 每批次插入 200万 条
START_TIMESTAMP = 1577836800 #1月1号
TIME_RANGE_SECONDS = 3600 * 24 * 365


def optimize_db_settings(cursor):
    """
    调整 SQLite 设置以获得极致写入性能
    注意：这些设置在断电等极端情况下可能导致数据库损坏，但用于生成测试数据非常完美。
    """
    cursor.execute("PRAGMA synchronous = OFF")  # 关闭磁盘同步，不等待物理写入
    cursor.execute("PRAGMA journal_mode = MEMORY")  # 日志存内存，减少IO
    cursor.execute("PRAGMA cache_size = 100000")  # 增大缓存
    cursor.execute("PRAGMA locking_mode = EXCLUSIVE")  # 独占模式


def generate_data_fast():
    t_start = time.time()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 1. 性能调优
    optimize_db_settings(cursor)

    # 2. 初始化表结构
    print("正在初始化数据库结构...")
    cursor.execute("DROP TABLE IF EXISTS event_log")
    cursor.execute("""
        CREATE TABLE event_log (
            user_id INTEGER,
            event_timestamp INTEGER
        )
    """)


    # 3. 准备用户池 (Numpy 数组)
    print("正在生成用户 ID 池...")
    user_pool = np.random.randint(1000000, 9999999, size=NUM_USERS, dtype=np.int32)

    total_batches = TOTAL_RECORDS // BATCH_SIZE
    print(f"开始生成数据: 总量 {TOTAL_RECORDS} 条, 分 {total_batches} 批插入...")

    for i in range(total_batches):
        t0 = time.time()

        # --- 核心优化区：使用 Numpy 瞬间生成数百万数据 ---

        # 1. 随机选择用户 (向量化操作)
        # 从 user_pool 中随机采样 BATCH_SIZE 个 ID
        batch_uids = user_pool[np.random.randint(0, NUM_USERS, size=BATCH_SIZE)]

        # 2. 随机生成时间戳 (向量化操作)
        batch_ts = np.random.randint(0, TIME_RANGE_SECONDS, size=BATCH_SIZE, dtype=np.int32) + START_TIMESTAMP

        # 3. 排序 (Numpy 排序极快)
        # 如果不需要严格排序，可以把下面两行注释掉，速度更快
        sort_indices = np.argsort(batch_ts)
        batch_uids = batch_uids[sort_indices]
        batch_ts = batch_ts[sort_indices]

        # 4. 数据组合
        # sqlite3 的 executemany 需要 Python 的 list/tuple 或者迭代器
        # 将 numpy 数组转为迭代器是目前最快的方法，避免一次性在大内存中建立巨大的 list
        data_iter = zip(batch_uids.tolist(), batch_ts.tolist())

        # 5. 批量写入
        cursor.executemany("INSERT INTO event_log (user_id, event_timestamp) VALUES (?, ?)", data_iter)
        conn.commit()  # 提交事务

        t1 = time.time()
        print(f"Batch {i + 1}/{total_batches} 完成. 耗时: {t1 - t0:.2f}s. 累计: {(i + 1) * BATCH_SIZE} 条")



    # 4. 数据插完后，创建索引 (这会花费一定时间，但比边插边建快得多)
    print("数据插入完成。正在构建索引 (这也需要一些时间)...")
    cursor.execute("CREATE INDEX idx_user_id ON event_log(user_id)")
    cursor.execute("CREATE INDEX idx_timestamp ON event_log(event_timestamp)")
    conn.commit()

    conn.close()

    t_end = time.time()
    print(f"全部完成! 总耗时: {t_end - t_start:.2f} 秒")
    print("\n--- 验证前 10 条数据 ---")

    # 验证
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM event_log LIMIT 10")
    for row in cursor.fetchall():
        print(row)
    conn.close()


if __name__ == "__main__":
    generate_data_fast()