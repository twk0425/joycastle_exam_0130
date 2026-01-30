from db import execute_sql
execute_sql("""
CREATE TABLE IF NOT EXISTS event_log (
    user_id INTEGER,          -- 玩家ID
    event_timestamp INTEGER   -- 开启关卡的时间戳 (Unix Timestamp)
);
""")
#为了查询效率，通常会给时间和用户ID加索引
execute_sql("""
CREATE INDEX idx_event_time ON event_log(event_timestamp);
""")
execute_sql("""
CREATE INDEX idx_user_id ON event_log(user_id);
""")

