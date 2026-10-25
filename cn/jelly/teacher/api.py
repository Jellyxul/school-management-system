"""
teacher management module
对外http接口
负责接收请求、参数校验、调用 Service、返回统一响应、记日志
"""
import logging
from fastapi import APIRouter, Path
from pydantic import BaseModel, Field
from typing import Literal, Optional

from cn.jelly.teacher.service import TeacherService
from cn.jelly.common.response import *
from cn.jelly.common.exceptions import BizException

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/teacher", tags=["teacher management"])

class TeacherIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="teacher name，1~50 strings")
    gender: Literal["man", "woman"] = Field(..., description="gender in man/woman")
    age: int = Field(..., ge=18, le=100, description="age 18~100")
    subject: str = Field(..., min_length=1, max_length=50, description="subject")
    phone: Optional[str] = Field(None, pattern=r"^1[3-9]\d{9}$", description="phone number")

class TeacherUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    gender: Literal["man", "woman"] = Field(..., description="gender in man/woman")
    age: int = Field(..., ge=18, le=100)
    subject: str = Field(..., min_length=1, max_length=50)
    phone: Optional[str] = Field(None, pattern=r"^1[3-9]\d{9}$")

@router.get("/list")
def list_teachers():
    """show all teachers"""
    service = TeacherService()
    try:
        data = service.list_teachers()
        return ok(data)
    except Exception as e:
        logger.error(f"list teachers error: {e}", exc_info=True)
        return fail(msg="fail to list teachers", code=500, data=None)

@router.get("/{teacher_id}/detail")
def get_teacher_detail(teacher_id: int = Path(..., gt=0)):
    """get teacher detail and their students"""
    service = TeacherService()
    try:
        return ok(service.get_teacher_detail(teacher_id))
    except BizException as e:
        logger.warning(f"get teacher detail failed: {e.msg}")
        return fail(msg=e.msg, code=e.code)
    except Exception as e:
        logger.error(f"get teacher detail error: {e}", exc_info=True)
        return fail(msg="fail to get teacher detail", code=500, data=None)

@router.get("/{teacher_id}")
def get_teacher(teacher_id: int = Path(..., gt=0)):
    """get one teacher"""
    service = TeacherService()
    try:
        return ok(service.get_teacher(teacher_id))
    except BizException as e:
        logger.warning(f"get teacher failed: {e.msg}")
        return fail(msg=e.msg, code=e.code)
    except Exception as e:
        logger.error(f"get teacher error: {e}", exc_info=True)
        return fail(msg="fail to get teacher", code=500, data=None)

@router.post("/add")
def add_teacher(tea: TeacherIn):
    """add teacher to database"""
    service = TeacherService()
    try:
        new_id = service.add_teacher(tea.name, tea.gender, tea.age, tea.subject, tea.phone)
        return ok(data={"id": new_id}, msg="add teacher success")
    except BizException as e:
        logger.warning(f"add teacher failed: {e.msg}")
        return fail(msg=e.msg, code=e.code)
    except Exception as e:
        logger.error(f"add teacher error: {e}", exc_info=True)
        return fail(msg="fail to add teacher", code=500, data=None)

@router.put("/update/{teacher_id}")
def update_teacher(teacher_id: int = Path(..., gt=0), tea: TeacherUpdate = ...):
    """update teacher"""
    service = TeacherService()
    try:
        rowcount = service.update_teacher(teacher_id, tea.name, tea.gender, tea.age, tea.subject, tea.phone)
        return ok(data={"updated": rowcount}, msg="update teacher success")
    except BizException as e:
        logger.warning(f"update teacher failed: {e.msg}")
        return fail(msg=e.msg, code=e.code)
    except Exception as e:
        logger.error(f"update teacher error: {e}", exc_info=True)
        return fail(msg="fail to update teacher", code=500, data=None)

@router.delete("/delete/{teacher_id}")
def delete_teacher(teacher_id: int = Path(..., gt=0)):
    """delete teacher"""
    service = TeacherService()
    try:
        rowcount = service.delete_teacher(teacher_id)
        return ok(data={"deleted": rowcount}, msg="delete teacher success")
    except BizException as e:
        logger.warning(f"delete teacher failed: {e.msg}")
        return fail(msg=e.msg, code=e.code)
    except Exception as e:
        logger.error(f"delete teacher error: {e}", exc_info=True)
        return fail(msg="fail to delete teacher", code=500, data=None)