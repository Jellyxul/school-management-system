"""
全局统一响应处理
"""

# 业务状态码
CODE_OK = 0     # 成功
CODE_FAIL = 1   # 通用失败（不传 code 时用）


def ok(data=None, msg="success"):
    """成功返回：code 固定为 0"""
    return {"code": CODE_OK, "msg": msg, "data": data}


def fail(msg: str = "操作失败", code=CODE_FAIL, data=None):
    """失败返回：默认 code 为 1"""
    return {"code": code, "msg": msg, "data": data}