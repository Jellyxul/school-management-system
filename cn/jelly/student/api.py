"""
student management module
对外 http 接口
负责接收请求、参数校验、调用 Service、返回统一响应、记日志
"""
import logging
from datetime import datetime
from typing import Literal, Optional

from fastapi import APIRouter, Path, Query
from pydantic import BaseModel, Field

from cn.jelly.student.service import StudentService
from cn.jelly.common.response import *
from cn.jelly.common.config import MAX_PAGE_SIZE
from cn.jelly.common.exceptions import BizException


# api 层与 service 层交互
# 异常日志只在 API 层记一次，避免与 service 重复
# 使用 try/except ValueError/Exception 记录业务异常 4xx 和系统异常 5xx


# 模块日志记录
logger = logging.getLogger(__name__)

# 子路由
router = APIRouter(prefix="/student", tags=["student management"])


# 请求模型
class StudentIn(BaseModel):
    # 全部加 Field 约束
    name: str = Field(..., min_length=1, max_length=50,
                      description="student name，1~50 strings")
    gender: Literal["man", "woman"] = Field(..., description="gender in man/woman")
    age: int = Field(..., ge=1, le=100, description="age 1~100")
    teacher_id: int = Field(..., gt=0, description="teacher id, required and must > 0")
    grade: Literal["高一", "高二", "高三"] = Field(..., description="grade")
    enrollment_date: Optional[datetime] = Field(None, description="enrollment date, optional")


class StudentUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    gender: Literal["man", "woman"] = Field(..., description="gender in man/woman")
    age: int = Field(..., ge=1, le=100)
    teacher_id: int = Field(..., gt=0)
    grade: Literal["高一", "高二", "高三"] = Field(...)
    enrollment_date: Optional[datetime] = Field(None)


# 路由
@router.get("/list")
def list_students():
    """show all students"""
    service = StudentService()
    try:
        data = service.list_students()
        return ok(data)
    except Exception as e:
        # 系统异常：记录堆栈，返回通用失败
        logger.error(f"list students error: {e}", exc_info=True)
        return fail(msg="fail to list students", code=500, data=None)

@router.get("/page")
def get_by_page(page: int = 1, size: int = 10, keyword: str = ""):
    """查：学生分页列表（keyword 按姓名模糊查询）"""
    if page <= 0:
        return fail("页码必须大于 0")
    if size <= 0 or size > MAX_PAGE_SIZE:
        return fail(f"每页条数必须在 1~{MAX_PAGE_SIZE} 之间")

    service = StudentService()
    try:
        data = service.get_by_page(page, size, keyword)
        return ok(data)
    except Exception as e:
        logger.error(f"list students by page error: {e}", exc_info=True)
        return fail(msg="fail to list students by page", code=500, data=None)


@router.get("/{student_id}")
# Path(..., gt=0) 让非法 id（如 -1、abc）由 FastAPI 自动返回 422
def get_student(student_id: int = Path(..., gt=0)):
    """get one student"""
    service = StudentService()
    try:
        return ok(service.get_student(student_id))
    except BizException as e:  # 捕获 BizException
        logger.warning(f"get student failed: {e.msg}")
        return fail(msg=e.msg, code=e.code)  # 动态获取自定义 code
    except Exception as e:
        logger.error(f"get student error: {e}", exc_info=True)
        return fail(msg="fail to get student", code=500, data=None)


@router.post("/add")
def add_student(stu: StudentIn):
    """add student to database"""
    service = StudentService()
    try:
        new_id = service.add_student(
            stu.name,
            stu.gender,
            stu.age,
            stu.teacher_id,
            stu.grade,
            stu.enrollment_date,
        )
        return ok(data={"id": new_id}, msg="add student success")
    except BizException as e:  # 修改
        logger.warning(f"add student failed: {e.msg}")
        return fail(msg=e.msg, code=e.code)
    except Exception as e:
        # 系统异常：记录堆栈
        logger.error(f"add student error: {e}", exc_info=True)
        return fail(msg="fail to add student", code=500, data=None)


@router.put("/update/{student_id}")
# Path(..., gt=0) 让非法 id（如 -1、abc）由 FastAPI 自动返回 422
def update_student(
    student_id: int = Path(..., gt=0),
    stu: StudentUpdate = ...,
):
    """update student"""
    service = StudentService()
    try:
        rowcount = service.update_student(
            student_id, stu.name, stu.gender, stu.age,
            stu.teacher_id, stu.grade, stu.enrollment_date
        )
        return ok(data={"updated": rowcount}, msg="update student success")
    except BizException as e:  # 修改
        logger.warning(f"update student failed: {e.msg}")
        return fail(msg=e.msg, code=e.code)
    except Exception as e:
        # 系统异常：记录堆栈
        logger.error(f"update student error: {e}", exc_info=True)
        return fail(msg="fail to update student", code=500, data=None)


@router.delete("/delete/{student_id}")
# Path(..., gt=0) 让非法 id（如 -1、abc）由 FastAPI 自动返回 422
def delete_student(student_id: int = Path(..., gt=0)):
    """delete student"""
    service = StudentService()
    try:
        rowcount = service.delete_student(student_id)
        return ok(data={"deleted": rowcount}, msg="delete student success")
    except BizException as e:  # 修改
        logger.warning(f"delete student failed: {e.msg}")
        return fail(msg=e.msg, code=e.code)
    except Exception as e:
        # 系统异常：记录堆栈
        logger.error(f"delete student error: {e}", exc_info=True)
        return fail(msg="fail to delete student", code=500, data=None)