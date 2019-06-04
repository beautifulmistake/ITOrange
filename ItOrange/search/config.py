"""
全局的配置文件
"""

# redis host
REDIS_HOST = 'localhost'    # 默认为 localhost

# redis port
REDIS_PORT = 6379   # 为 int 类型

# redis password
REDIS_PASSWORD = None   # 若有填写你自己的，str 类型

# redis key
REDIS_KEY = 'request_ItJuZi'

# proxy 连接池的请求地址
PROXY_POOL_URL = 'your address'

# timeout
TIMEOUT = 10

# 请求最大尝试次数
MAX_FAILED_TIME = 20

# 有效的状态码
VALID_STATUSES = [200]
