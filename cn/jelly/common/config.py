"""
全局公共配置
"""

import logging

# 分页配置，每页最多显示100条
MAX_PAGE_SIZE = 100

# ==============伙伴服务（远程接口）配置===================== #
PARTNER_BASE_URL = "http://127.0.0.1:8002"   # 伙伴服务 cn_obj 在本机启动的地址和端口
PARTNER_STU_BY_TEA_PATH = "/student/teacher/{teacher_id}"   # 伙伴接口：按老师ID查询学生
REQUEST_TIMEOUT = 5   # 远程调用超时时间（秒），防止伙伴服务卡死时无限等待

# 可改变输出级别，优先级大于等于设定级别的全部输出
logging.basicConfig(
    # 配置日志输出优先级
    level=logging.INFO,
    # 格式化输出
    # 时间-线程-输出级别-模块名：日志信息
    format='%(asctime)s - %(threadName)s - [%(levelname)s] - %(name)s:%(message)s',
    handlers=[
        # 配置日志输出目标类型
        logging.FileHandler('../user information.log', encoding='utf-8'),
        # 控制台输出
        logging.StreamHandler()
    ],
)
