"""
enrollment management module
对外 http 接口
负责接收请求、参数校验、调用 Service、返回统一响应、记日志
"""
import logging
from typing import Optional

from fastapi import APIRouter, Path
from pydantic import BaseModel, Field

from cn.jelly.enrollment.service import EnrollmentService
from cn.jelly.common.response import *
from cn.jelly.common.config import MAX_PAGE_SIZE
from cn.jelly.common.exceptions import BizException


# api 层与 service 层交互
# 异常日志只在 API 层记一次，避免与 service 重复
# 使用 try/except ValueError/Exception 记录业务异常 4xx 和系统异常 5xx


# 模块日志记录
logger = logging.getLogger(__name__)

# 子路由
router = APIRouter(prefix="/enrollment", tags=["enrollment management"])


# 请求模型
class EnrollmentIn(BaseModel):
    # 全部加 Field 约束
    student_id: int = Field(..., gt=0, description="student id, required and must > 0")
    course_id: int = Field(..., gt=0, description="course id, required and must > 0")
    term: Optional[str] = Field(None, max_length=20,
                                description="term like 2026-2027-1, default current term")
    score: Optional[int] = Field(None, ge=0, le=100,
                                 description="score 0~100, default empty (not entered)")
    status: str = Field("已选", min_length=1, max_length=10,
                        description="status, default 已选")


class EnrollmentUpdate(BaseModel):
    student_id: int = Field(..., gt=0)
    course_id: int = Field(..., gt=0)
    term: str = Field(..., min_length=1, max_length=20)
    status: str = Field(..., min_length=1, max_length=10)


class ScoreIn(BaseModel):
    score: Optional[int] = Field(None, ge=0, le=100,
                                 description="score 0~100, empty means not entered")
    status: str = Field(..., min_length=1, max_length=10)


# 路由
@router.get("/list")
def list_enrollments():
    """show all enrollments"""
    service = EnrollmentService()
    try:
        data = service.list_enrollments()
        return ok(data)
    except Exception as e:
        # 系统异常：记录堆栈，返回通用失败
        logger.error(f"list enrollments error: {e}", exc_info=True)
        return fail(msg="fail to list enrollments", code=500, data=None)


@router.get("/page")
def get_by_page(page: int = 1, size: int = 10, keyword: str = ""):
    """查：选课分页列表（keyword 按学期/学生姓名/课程名称模糊查询）"""
    if page <= 0:
        return fail("页码必须大于 0")
    if size <= 0 or size > MAX_PAGE_SIZE:
        return fail(f"每页条数必须在 1~{MAX_PAGE_SIZE} 之间")

    service = EnrollmentService()
    try:
        data = service.get_by_page(page, size, keyword)
        return ok(data)
    except Exception as e:
        logger.error(f"list enrollments by page error: {e}", exc_info=True)
        return fail(msg="fail to list enrollments by page", code=500, data=None)


@router.get("/{enrollment_id}")
# Path(..., gt=0) 让非法 id（如 -1、abc）由 FastAPI 自动返回 422
def get_enrollment(enrollment_id: int = Path(..., gt=0)):
    """get one enrollment"""
    service = EnrollmentService()
    try:
        return ok(service.get_enrollment(enrollment_id))
    except BizException as e:  # 捕获 BizException
        logger.warning(f"get enrollment failed: {e.msg}")
        return fail(msg=e.msg, code=e.code)  # 动态获取自定义 code
    except Exception as e:
        logger.error(f"get enrollment error: {e}", exc_info=True)
        return fail(msg="fail to get enrollment", code=500, data=None)


@router.post("/add")
def add_enrollment(enr: EnrollmentIn):
    """add enrollment to database"""
    service = EnrollmentService()
    try:
        new_id = service.add_enrollment(
            enr.student_id,
            enr.course_id,
            enr.term,
            enr.score,
            enr.status,
        )
        return ok(data={"id": new_id}, msg="add enrollment success")
    except BizException as e:
        logger.warning(f"add enrollment failed: {e.msg}")
        return fail(msg=e.msg, code=e.code)
    except Exception as e:
        # 系统异常：记录堆栈
        logger.error(f"add enrollment error: {e}", exc_info=True)
        return fail(msg="fail to add enrollment", code=500, data=None)


@router.put("/update/{enrollment_id}")
# Path(..., gt=0) 让非法 id（如 -1、abc）由 FastAPI 自动返回 422
def update_enrollment(
    enrollment_id: int = Path(..., gt=0),
    enr: EnrollmentUpdate = ...,
):
    """update enrollment，不含成绩（成绩由 /score 接口单独录入）"""
    service = EnrollmentService()
    try:
        rowcount = service.update_enrollment(
            enrollment_id, enr.student_id, enr.course_id,
            enr.term, enr.status
        )
        return ok(data={"updated": rowcount}, msg="update enrollment success")
    except BizException as e:
        logger.warning(f"update enrollment failed: {e.msg}")
        return fail(msg=e.msg, code=e.code)
    except Exception as e:
        # 系统异常：记录堆栈
        logger.error(f"update enrollment error: {e}", exc_info=True)
        return fail(msg="fail to update enrollment", code=500, data=None)


@router.put("/score/{enrollment_id}")
# Path(..., gt=0) 让非法 id（如 -1、abc）由 FastAPI 自动返回 422
def update_score(
    enrollment_id: int = Path(..., gt=0),
    data: ScoreIn = ...,
):
    """录入/修改成绩与状态，score 为空表示未录入"""
    service = EnrollmentService()
    try:
        rowcount = service.update_score(
            enrollment_id, data.score, data.status
        )
        return ok(data={"updated": rowcount}, msg="update score success")
    except BizException as e:
        logger.warning(f"update score failed: {e.msg}")
        return fail(msg=e.msg, code=e.code)
    except Exception as e:
        # 系统异常：记录堆栈
        logger.error(f"update score error: {e}", exc_info=True)
        return fail(msg="fail to update score", code=500, data=None)


@router.delete("/delete/{enrollment_id}")
# Path(..., gt=0) 让非法 id（如 -1、abc）由 FastAPI 自动返回 422
def delete_enrollment(enrollment_id: int = Path(..., gt=0)):
    """delete enrollment"""
    service = EnrollmentService()
    try:
        rowcount = service.delete_enrollment(enrollment_id)
        return ok(data={"deleted": rowcount}, msg="delete enrollment success")
    except BizException as e:
        logger.warning(f"delete enrollment failed: {e.msg}")
        return fail(msg=e.msg, code=e.code)
    except Exception as e:
        # 系统异常：记录堆栈
        logger.error(f"delete enrollment error: {e}", exc_info=True)
        return fail(msg="fail to delete enrollment", code=500, data=None)
