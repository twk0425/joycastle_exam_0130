from db import execute_sql

sql="""
SELECT COUNT(*) AS user_count
FROM (
    -- 第一步：统计每个用户2020年9月的关卡开启次数
    SELECT user_id, COUNT(*) AS open_level_count
    FROM event_log
    WHERE 
        event_timestamp >= strftime('%s', '2020-09-01 00:00:00')
        AND event_timestamp < strftime('%s', '2020-10-01 00:00:00')
    GROUP BY user_id
    -- 筛选出开启次数≥1000且<2000的用户
    HAVING open_level_count >= 1000 AND open_level_count < 2000
) AS level_open_stats;
"""
op=execute_sql(sql)
print(op)