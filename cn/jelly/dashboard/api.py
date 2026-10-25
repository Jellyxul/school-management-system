"""
dashboard module
对外 http 接口
负责接收请求、调用 Service、返回统一响应、记日志
"""
import logging

from fastapi import APIRouter

from cn.jelly.common.response import *
from cn.jelly.common.exceptions import BizException
from cn.jelly.dashboard.service import DashboardService


# api 层与 service 层交互
# 异常日志只在 API 层记一次，避免与 service 重复
# 使用 try/except ValueError/Exception 记录业务异常 4xx 和系统异常 5xx


# 模块日志记录
logger = logging.getLogger(__name__)

# 子路由
router = APIRouter(prefix="/dashboard", tags=["dashboard management"])


# 路由
@router.get("/stats")
def get_stats():
    """首页看板统计：学生/教师/课程/班级总数"""
    service = DashboardService()
    try:
        return ok(service.get_stats())
    except BizException as e:  # 捕获 BizException
        logger.warning(f"get dashboard stats failed: {e.msg}")
        return fail(msg=e.msg, code=e.code)  # 动态获取自定义 code
    except Exception as e:
        # 系统异常：记录堆栈，返回通用失败
        logger.error(f"get dashboard stats error: {e}", exc_info=True)
        return fail(msg="fail to get dashboard stats", code=500, data=None)
