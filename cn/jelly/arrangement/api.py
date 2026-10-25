"""
arrangement management module
对外 http 接口
负责接收请求、参数校验、调用 Service、返回统一响应、记日志
"""
import logging
from typing import Optional

from fastapi import APIRouter, Path
from pydantic import BaseModel, Field

from cn.jelly.arrangement.service import ArrangementService
from cn.jelly.common.response import *
from cn.jelly.common.config import MAX_PAGE_SIZE
from cn.jelly.common.exceptions import BizException


# api 层与 service 层交互
# 异常日志只在 API 层记一次，避免与 service 重复
# 使用 try/except ValueError/Exception 记录业务异常 4xx 和系统异常 5xx


# 模块日志记录
logger = logging.getLogger(__name__)

# 子路由
router = APIRouter(prefix="/arrangement", tags=["arrangement management"])


# 请求模型
class ArrangementIn(BaseModel):
    # 全部加 Field 约束
    course_id: int = Field(..., gt=0, description="course id, required and must > 0")
    teacher_id: int = Field(..., gt=0, description="teacher id, required and must > 0")
    term: Optional[str] = Field(None, max_length=20,
                                description="term like 2026-2027-1, default current term")
    classroom: str = Field(..., min_length=1, max_length=50,
                           description="classroom，1~50 strings")
    class_time: str = Field(..., min_length=1, max_length=50,
                            description="class time，1~50 strings")


class ArrangementUpdate(BaseModel):
    course_id: int = Field(..., gt=0)
    teacher_id: int = Field(..., gt=0)
    term: str = Field(..., min_length=1, max_length=20)
    classroom: str = Field(..., min_length=1, max_length=50)
    class_time: str = Field(..., min_length=1, max_length=50)


# 路由
@router.get("/list")
def list_arrangements():
    """show all arrangements"""
    service = ArrangementService()
    try:
        data = service.list_arrangements()
        return ok(data)
    except Exception as e:
        # 系统异常：记录堆栈，返回通用失败
        logger.error(f"list arrangements error: {e}", exc_info=True)
        return fail(msg="fail to list arrangements", code=500, data=None)


@router.get("/page")
def get_by_page(page: int = 1, size: int = 10, keyword: str = ""):
    """查：排课分页列表（keyword 按学期/上课教室模糊查询）"""
    if page <= 0:
        return fail("页码必须大于 0")
    if size <= 0 or size > MAX_PAGE_SIZE:
        return fail(f"每页条数必须在 1~{MAX_PAGE_SIZE} 之间")

    service = ArrangementService()
    try:
        data = service.get_by_page(page, size, keyword)
        return ok(data)
    except Exception as e:
        logger.error(f"list arrangements by page error: {e}", exc_info=True)
        return fail(msg="fail to list arrangements by page", code=500, data=None)


@router.get("/{arrangement_id}")
# Path(..., gt=0) 让非法 id（如 -1、abc）由 FastAPI 自动返回 422
def get_arrangement(arrangement_id: int = Path(..., gt=0)):
    """get one arrangement"""
    service = ArrangementService()
    try:
        return ok(service.get_arrangement(arrangement_id))
    except BizException as e:  # 捕获 BizException
        logger.warning(f"get arrangement failed: {e.msg}")
        return fail(msg=e.msg, code=e.code)  # 动态获取自定义 code
    except Exception as e:
        logger.error(f"get arrangement error: {e}", exc_info=True)
        return fail(msg="fail to get arrangement", code=500, data=None)


@router.post("/add")
def add_arrangement(arr: ArrangementIn):
    """add arrangement to database"""
    service = ArrangementService()
    try:
        new_id = service.add_arrangement(
            arr.course_id,
            arr.teacher_id,
            arr.term,
            arr.classroom,
            arr.class_time,
        )
        return ok(data={"id": new_id}, msg="add arrangement success")
    except BizException as e:
        logger.warning(f"add arrangement failed: {e.msg}")
        return fail(msg=e.msg, code=e.code)
    except Exception as e:
        # 系统异常：记录堆栈
        logger.error(f"add arrangement error: {e}", exc_info=True)
        return fail(msg="fail to add arrangement", code=500, data=None)


@router.put("/update/{arrangement_id}")
# Path(..., gt=0) 让非法 id（如 -1、abc）由 FastAPI 自动返回 422
def update_arrangement(
    arrangement_id: int = Path(..., gt=0),
    arr: ArrangementUpdate = ...,
):
    """update arrangement"""
    service = ArrangementService()
    try:
        rowcount = service.update_arrangement(
            arrangement_id, arr.course_id, arr.teacher_id,
            arr.term, arr.classroom, arr.class_time
        )
        return ok(data={"updated": rowcount}, msg="update arrangement success")
    except BizException as e:
        logger.warning(f"update arrangement failed: {e.msg}")
        return fail(msg=e.msg, code=e.code)
    except Exception as e:
        # 系统异常：记录堆栈
        logger.error(f"update arrangement error: {e}", exc_info=True)
        return fail(msg="fail to update arrangement", code=500, data=None)


@router.delete("/delete/{arrangement_id}")
# Path(..., gt=0) 让非法 id（如 -1、abc）由 FastAPI 自动返回 422
def delete_arrangement(arrangement_id: int = Path(..., gt=0)):
    """delete arrangement"""
    service = ArrangementService()
    try:
        rowcount = service.delete_arrangement(arrangement_id)
        return ok(data={"deleted": rowcount}, msg="delete arrangement success")
    except BizException as e:
        logger.warning(f"delete arrangement failed: {e.msg}")
        return fail(msg=e.msg, code=e.code)
    except Exception as e:
        # 系统异常：记录堆栈
        logger.error(f"delete arrangement error: {e}", exc_info=True)
        return fail(msg="fail to delete arrangement", code=500, data=None)
