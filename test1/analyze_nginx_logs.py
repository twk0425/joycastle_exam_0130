import re
from datetime import datetime

# 定义正则模式
# 对应示例: 47.xx... - - [28/Feb/2019:13:17:10 +0000] "GET..." 200 5316 "https://..." "Mozilla..."
# Group 1: 时间戳 (28/Feb/2019:13:17:10 +0000)
# Group 2: 状态码 (200)
# Group 3: URL/Referer ("https://domain1.com/?p=1")
log_pattern = re.compile(r'.*?\[(.*?)\].*?\"\w+ .*?\" (\d{3}) \d+ \"(.*?)\".*')


def count_https_domain(file_path, domain):
    """
    统计指定指标：
    目标域名的 HTTPS 请求数量

    :param file_path: 日志文件路径
    :param domain: 目标域名，例如 domain1.com
    """
    # 计数器
    https_domain_count = 0
    print(f"开始分析日志文件: {file_path} ...")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                # 解析行
                match = log_pattern.match(line)
                if not match:
                    continue

                url_field = match.group(3)

                # --- 任务 : 统计 HTTPS 且域名为 domain1.com ---
                # 逻辑: URL 以 https:// 开头，且主机部分正好是 domain1.com
                if url_field.startswith("https://"):
                    # 去掉 'https://'，取剩下的部分，再按 '/' 分割取第一个元素即为域名
                    # 例如 "https://domain1.com/?p=1" -> "domain1.com"
                    try:
                        domain_part = url_field[8:].split('/', 1)[0]
                        # 剔除可能存在的端口号 (如 domain1.com:443)
                        domain_part = domain_part.split(':', 1)[0]

                        if domain_part == domain:
                            https_domain_count += 1
                    except IndexError:
                        pass
    except FileNotFoundError:
        print("错误: 找不到日志文件。")
        return

    # 输出报告
    print("-" * 30)
    print("分析结果报告")
    print(f"域名为 {domain} 的 HTTPS 请求总数: {https_domain_count}")
    return https_domain_count

def success_rate_by_date(file_path, target_date_str):
    """
    统计指定指标：
    指定日期的请求成功率 (状态码 < 400)

    :param file_path: 日志文件路径
    :param target_date_str: 目标日期，格式 "YYYY-MM-DD" (例如 "2019-02-28")
    """
    # 预处理日期格式
    # 将输入的 "2019-02-28" 转换为 Nginx 日志格式 "28/Feb/2019"
    # 这样可以在循环中只做字符串比对，大幅提高 1000万 行的处理速度
    try:
        target_date_obj = datetime.strptime(target_date_str, "%Y-%m-%d")
        target_log_date = target_date_obj.strftime("%d/%b/%Y")
    except ValueError:
        print("日期格式错误，请使用 YYYY-MM-DD 格式")
        return
    # 计数器
    date_total_requests = 0
    date_success_requests = 0

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                # 解析行
                match = log_pattern.match(line)
                if not match:
                    continue

                timestamp_str = match.group(1)
                status_code = int(match.group(2))

                # --- 任务 : 统计指定日期的成功率 ---
                # 利用字符串包含快速锁定是否为当日日志 (UTC时间都在时间戳字符串里)
                if target_log_date in timestamp_str:
                    date_total_requests += 1
                    # 定义成功：状态码小于 400 (即 2xx 和 3xx)
                    if status_code < 400:
                        date_success_requests += 1

    except FileNotFoundError:
        print("错误: 找不到日志文件。")
        return

    # 计算结果
    success_rate = 0.0
    if date_total_requests > 0:
        success_rate = (date_success_requests / date_total_requests) * 100

    # 输出报告
    print("-" * 30)
    print("分析结果报告")
    print("-" * 30)
    print(f"日期 {target_date_str} (UTC) 数据统计:")
    print(f"   - 当日总请求数: {date_total_requests}")
    print(f"   - 当日成功请求数 (Status < 400): {date_success_requests}")
    print(f"   - 请求成功比例: {success_rate:.2f}%")




# 使用示例 (请替换为实际文件路径)
if __name__ == "__main__":
    count_https_domain("./test1/nginx.log", "domain1.com")
    # 假设日志文件名为 nginx.log，要查询的日期是 2019年2月28日
    success_rate_by_date("./test1/nginx.log", "2019-02-28")
