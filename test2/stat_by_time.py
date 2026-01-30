import sqlite3
import time
import datetime

DB_FILE = 'twk0425.db'


def get_timestamp(date_str):
    """辅助函数：将 '2020-09-01' 转为 Unix 时间戳整数"""
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    return int(dt.timestamp())


def run_optimized_query():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 1. 基础性能参数 (针对只读查询，只需增大缓存即可)
    cursor.execute("PRAGMA cache_size = 200000")  # 约 200MB 缓存
    cursor.execute("PRAGMA temp_store = MEMORY")  # 临时结果存内存

    print("正在检查索引...")
    t_start_index = time.time()



    # 【核心优化 2】在 Python 端计算时间戳，避免 SQL 每一行都调 strftime 函数
    start_ts = get_timestamp('2020-09-01 00:00:00')
    end_ts = get_timestamp('2020-10-01 00:00:00')

    print(f"正在执行查询 (时间范围: {start_ts} - {end_ts})...")
    t_start_query = time.time()

    sql = """
    SELECT COUNT(*) AS user_count
    FROM (
        SELECT user_id
        FROM event_log
        WHERE event_timestamp >= ? AND event_timestamp < ?
        GROUP BY user_id
        HAVING COUNT(*) >= 1000 AND COUNT(*) < 2000
    );
    """

    # 【修正错误】cursor.execute 返回的是游标对象，不是结果，必须用 fetchone 获取数据
    cursor.execute(sql, (start_ts, end_ts))
    result = cursor.fetchone()

    t_end = time.time()

    if result:
        print(f"查询结果 (user_count): {result[0]}")
    else:
        print("未查询到符合条件的数据")

    print(f"查询耗时: {t_end - t_start_query:.2f}s")

    # 验证是否使用了索引
    print("\n--- 查询计划解释 (Query Plan) ---")
    cursor.execute(f"EXPLAIN QUERY PLAN {sql}", (start_ts, end_ts))
    for row in cursor.fetchall():
        print(row)
        # 理想结果应该包含: "USING COVERING INDEX idx_ts_user"
        # 如果看到 "SCAN TABLE"，说明全表扫描，性能极差

    conn.close()


if __name__ == "__main__":
    run_optimized_query()