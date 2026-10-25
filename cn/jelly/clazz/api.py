"""
clazz management module
对外 http 接口
负责接收请求、参数校验、调用 Service、返回统一响应、记日志
"""
import logging
from typing import Optional

from fastapi import APIRouter, Path
from pydantic import BaseModel, Field

from cn.jelly.clazz.service import ClazzService
from cn.jelly.common.response import *
from cn.jelly.common.config import MAX_PAGE_SIZE
from cn.jelly.common.exceptions import BizException


# api 层与 service 层交互
# 异常日志只在 API 层记一次，避免与 service 重复
# 使用 try/except ValueError/Exception 记录业务异常 4xx 和系统异常 5xx


# 模块日志记录
logger = logging.getLogger(__name__)

# 子路由
router = APIRouter(prefix="/clazz", tags=["clazz management"])


# 请求模型
class ClazzIn(BaseModel):
    # 全部加 Field 约束
    name: str = Field(..., min_length=1, max_length=50,
                      description="clazz name，1~50 strings")
    code: str = Field(..., min_length=1, max_length=50,
                      description="clazz code，1~50 strings")
    teacher_id: int = Field(..., gt=0, description="head teacher id, required and must > 0")
    address: Optional[str] = Field(None, max_length=100, description="clazz address, optional")


class ClazzUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    code: str = Field(..., min_length=1, max_length=50)
    teacher_id: int = Field(..., gt=0)
    address: Optional[str] = Field(None, max_length=100)


# 路由
@router.get("/list")
def list_clazzes():
    """show all clazzes"""
    service = ClazzService()
    try:
        data = service.list_clazzes()
        return ok(data)
    except Exception as e:
        # 系统异常：记录堆栈，返回通用失败
        logger.error(f"list clazzes error: {e}", exc_info=True)
        return fail(msg="fail to list clazzes", code=500, data=None)


@router.get("/page")
def get_by_page(page: int = 1, size: int = 10, keyword: str = ""):
    """查：班级分页列表（keyword 按班级名称模糊查询）"""
    if page <= 0:
        return fail("页码必须大于 0")
    if size <= 0 or size > MAX_PAGE_SIZE:
        return fail(f"每页条数必须在 1~{MAX_PAGE_SIZE} 之间")

    service = ClazzService()
    try:
        data = service.get_by_page(page, size, keyword)
        return ok(data)
    except Exception as e:
        logger.error(f"list clazzes by page error: {e}", exc_info=True)
        return fail(msg="fail to list clazzes by page", code=500, data=None)


@router.get("/{clazz_id}")
# Path(..., gt=0) 让非法 id（如 -1、abc）由 FastAPI 自动返回 422
def get_clazz(clazz_id: int = Path(..., gt=0)):
    """get one clazz"""
    service = ClazzService()
    try:
        return ok(service.get_clazz(clazz_id))
    except BizException as e:  # 捕获 BizException
        logger.warning(f"get clazz failed: {e.msg}")
        return fail(msg=e.msg, code=e.code)  # 动态获取自定义 code
    except Exception as e:
        logger.error(f"get clazz error: {e}", exc_info=True)
        return fail(msg="fail to get clazz", code=500, data=None)


@router.post("/add")
def add_clazz(clazz: ClazzIn):
    """add clazz to database"""
    service = ClazzService()
    try:
        new_id = service.add_clazz(
            clazz.name,
            clazz.code,
            clazz.teacher_id,
            clazz.address,
        )
        return ok(data={"id": new_id}, msg="add clazz success")
    except BizException as e:
        logger.warning(f"add clazz failed: {e.msg}")
        return fail(msg=e.msg, code=e.code)
    except Exception as e:
        # 系统异常：记录堆栈
        logger.error(f"add clazz error: {e}", exc_info=True)
        return fail(msg="fail to add clazz", code=500, data=None)


@router.put("/update/{clazz_id}")
# Path(..., gt=0) 让非法 id（如 -1、abc）由 FastAPI 自动返回 422
def update_clazz(
    clazz_id: int = Path(..., gt=0),
    clazz: ClazzUpdate = ...,
):
    """update clazz"""
    service = ClazzService()
    try:
        rowcount = service.update_clazz(
            clazz_id, clazz.name, clazz.code,
            clazz.teacher_id, clazz.address
        )
        return ok(data={"updated": rowcount}, msg="update clazz success")
    except BizException as e:
        logger.warning(f"update clazz failed: {e.msg}")
        return fail(msg=e.msg, code=e.code)
    except Exception as e:
        # 系统异常：记录堆栈
        logger.error(f"update clazz error: {e}", exc_info=True)
        return fail(msg="fail to update clazz", code=500, data=None)


@router.delete("/delete/{clazz_id}")
# Path(..., gt=0) 让非法 id（如 -1、abc）由 FastAPI 自动返回 422
def delete_clazz(clazz_id: int = Path(..., gt=0)):
    """delete clazz"""
    service = ClazzService()
    try:
        rowcount = service.delete_clazz(clazz_id)
        return ok(data={"deleted": rowcount}, msg="delete clazz success")
    except BizException as e:
        logger.warning(f"delete clazz failed: {e.msg}")
        return fail(msg=e.msg, code=e.code)
    except Exception as e:
        # 系统异常：记录堆栈
        logger.error(f"delete clazz error: {e}", exc_info=True)
        return fail(msg="fail to delete clazz", code=500, data=None)
