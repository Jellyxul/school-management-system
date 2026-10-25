"""
subject management module
对外 http 接口
负责接收请求、参数校验、调用 Service、返回统一响应、记日志
"""
import logging

from fastapi import APIRouter, Path
from pydantic import BaseModel, Field

from cn.jelly.subject.service import SubjectService
from cn.jelly.common.response import *
from cn.jelly.common.config import MAX_PAGE_SIZE
from cn.jelly.common.exceptions import BizException

# 模块日志记录
logger = logging.getLogger(__name__)

# 子路由
router = APIRouter(prefix="/subject", tags=["subject management"])

# 请求模型
class SubjectIn(BaseModel):
    # 全部加 Field 约束
    name: str = Field(..., min_length=1, max_length=50,
                      description="subject name，1~50 strings")
    credit: int = Field(0, ge=0, le=10, description="subject credit 0~10, default 0")
    teacher_id: int = Field(..., gt=0, description="teacher id, required and must > 0")


class SubjectUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    credit: int = Field(0, ge=0, le=10)
    teacher_id: int = Field(..., gt=0)


# 路由
@router.get("/list")
def list_subjects():
    """show all subjects"""
    service = SubjectService()
    try:
        data = service.list_subjects()
        return ok(data)
    except Exception as e:
        # 系统异常：记录堆栈，返回通用失败
        logger.error(f"list subjects error: {e}", exc_info=True)
        return fail(msg="fail to list subjects", code=500, data=None)


@router.get("/page")
def get_by_page(page: int = 1, size: int = 10, keyword: str = ""):
    """查：课程分页列表（keyword 按课程名模糊查询）"""
    if page <= 0:
        return fail("页码必须大于 0")
    if size <= 0 or size > MAX_PAGE_SIZE:
        return fail(f"每页条数必须在 1~{MAX_PAGE_SIZE} 之间")

    service = SubjectService()
    try:
        data = service.get_by_page(page, size, keyword)
        return ok(data)
    except Exception as e:
        logger.error(f"list subjects by page error: {e}", exc_info=True)
        return fail(msg="fail to list subjects by page", code=500, data=None)


@router.get("/{subject_id}")
# Path(..., gt=0) 让非法 id（如 -1、abc）由 FastAPI 自动返回 422
def get_subject(subject_id: int = Path(..., gt=0)):
    """get one subject"""
    service = SubjectService()
    try:
        return ok(service.get_subject(subject_id))
    except BizException as e:
        logger.warning(f"get subject failed: {e.msg}")
        return fail(msg=e.msg, code=e.code)
    except Exception as e:
        logger.error(f"get subject error: {e}", exc_info=True)
        return fail(msg="fail to get subject", code=500, data=None)


@router.get("/{subject_id}/detail")
def get_subject_detail(subject_id: int = Path(..., gt=0)):
     """get subject detail: subject + its teacher + that teacher's students"""
     service = SubjectService()
     try:
         return ok(service.get_subject_detail(subject_id))
     except BizException as e:
         logger.warning(f"get subject failed: {e.msg}")
         return fail(msg=e.msg, code=e.code)
     except Exception as e:
         logger.error(f"get subject error: {e}", exc_info=True)
         return fail(msg="fail to get subject", code=500, data=None)


@router.post("/add")
def add_subject(sub: SubjectIn):
    """add subject to database"""
    service = SubjectService()
    try:
        new_id = service.add_subject(
            sub.name,
            sub.credit,
            sub.teacher_id,
        )
        return ok(data={"id": new_id}, msg="add subject success")
    except BizException as e:
        logger.warning(f"add subject failed: {e.msg}")
        return fail(msg=e.msg, code=e.code)
    except Exception as e:
        logger.error(f"add subject error: {e}", exc_info=True)
        return fail(msg="fail to add subject", code=500, data=None)


@router.put("/update/{subject_id}")
# Path(..., gt=0) 让非法 id（如 -1、abc）由 FastAPI 自动返回 422
def update_subject(
    subject_id: int = Path(..., gt=0),
    sub: SubjectUpdate = ...,
):
    """update subject"""
    service = SubjectService()
    try:
        rowcount = service.update_subject(
            subject_id, sub.name, sub.credit, sub.teacher_id
        )
        return ok(data={"updated": rowcount}, msg="update subject success")
    except BizException as e:
        logger.warning(f"update subject failed: {e.msg}")
        return fail(msg=e.msg, code=e.code)
    except Exception as e:
        logger.error(f"update subject error: {e}", exc_info=True)
        return fail(msg="fail to update subject", code=500, data=None)


@router.delete("/delete/{subject_id}")
# Path(..., gt=0) 让非法 id（如 -1、abc）由 FastAPI 自动返回 422
def delete_subject(subject_id: int = Path(..., gt=0)):
    """delete subject"""
    service = SubjectService()
    try:
        rowcount = service.delete_subject(subject_id)
        return ok(data={"deleted": rowcount}, msg="delete subject success")
    except BizException as e:
        logger.warning(f"delete subject failed: {e.msg}")
        return fail(msg=e.msg, code=e.code)
    except Exception as e:
        logger.error(f"delete subject error: {e}", exc_info=True)
        return fail(msg="fail to delete subject", code=500, data=None)

