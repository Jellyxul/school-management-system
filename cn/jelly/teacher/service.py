"""
业务逻辑层
承载业务逻辑、连接校验、写日志
是 API 与 DAO 之间的桥梁
"""
import logging

import requests

from cn.jelly.teacher.dao import TeacherDB
from cn.jelly.student.dao import StudentDB
from cn.jelly.common.config import PARTNER_BASE_URL, PARTNER_STU_BY_TEA_PATH, REQUEST_TIMEOUT
from cn.jelly.common.exceptions import BizException, NOT_EXIST, CODE_FAIL

logger = logging.getLogger(__name__)


# ==============伙伴服务（远程接口）配置===================== #
def get_stu_by_teaid(teacher_id, timeout=REQUEST_TIMEOUT):
    """远程调用伙伴接口：按老师ID查询学生列表，返回学生列表"""
    url = f"{PARTNER_BASE_URL}{PARTNER_STU_BY_TEA_PATH.format(teacher_id=teacher_id)}"
    try:
        # 远程调用伙伴接口，timeout 防止服务卡死时无限挂起
        resp = requests.get(url=url, timeout=timeout)
        # 请求接口成功，然后处理数据
        resp.raise_for_status()
    # 顺序不能写错, RequestException 是所有 request 异常的父类，必须放在最后
    except requests.exceptions.HTTPError as e:
        logger.error(f"call partner interface http error: {e}, url={url}")
        raise BizException(msg="伙伴接口返回错误", code=CODE_FAIL)
    except requests.exceptions.ConnectionError as e:
        logger.error(f"call partner interface connection error: {e}, url={url}")
        raise BizException(msg="伙伴服务未启动或无法连接", code=CODE_FAIL)
    except requests.exceptions.Timeout as e:
        logger.error(f"call partner interface timeout: {e}, url={url}")
        raise BizException(msg="调用伙伴接口超时", code=CODE_FAIL)
    except requests.exceptions.RequestException as e:
        logger.error(f"call partner interface error: {e}, url={url}")
        raise BizException(msg="调用伙伴接口失败", code=CODE_FAIL)

    # 伙伴统一响应：code=0 成功，data 为学生列表
    result = resp.json()
    if result.get("code") != 0:
        logger.warning(f"business check failed: partner code={result.get('code')}, msg={result.get('msg')}")
        raise BizException(msg=result.get("msg", "fail to get students by teacher id"),
                           code=result.get("code", CODE_FAIL))
    logger.info(f"successfully fetched students by remote interface, teacher id: {teacher_id}")
    return result.get("data") or []



class TeacherService:
    def list_teachers(self):
        """show all teachers"""
        db = TeacherDB()
        data = db.get_all()
        logger.info("successfully fetched all teachers, total %d", len(data))
        return data

    def get_teacher(self, teacher_id: int):
        """get one teacher"""
        db = TeacherDB()
        tea = db.get_one(teacher_id)
        if not tea:
            logger.warning(f"business check failed: teacher not found, id={teacher_id}")
            raise BizException(msg=f"teacher not found, id={teacher_id}", code=NOT_EXIST)
        # 组装业务：远程调用伙伴接口，按老师ID带出该老师名下的学生
        tea["stu_list"] = get_stu_by_teaid(tea["id"])
        logger.info(f"successfully fetched, teacher id: {teacher_id}, student count: {len(tea['stu_list'])}")
        return tea

    def get_teacher_detail(self, teacher_id):
        """获取教师详情，并组装其名下的学生信息 (组装查询业务)"""
        t_db = TeacherDB()
        s_db = StudentDB()
        # 查教师
        teacher = t_db.get_one(teacher_id)
        if not teacher:
            raise BizException(msg=f"teacher not found, id={teacher_id}", code=NOT_EXIST)
        # 查该教师名下的学生
        students = s_db.get_by_teacher_id(teacher_id)
        # 组装数据
        teacher["students"] = students
        teacher["student_count"] = len(students)

        logger.info(f"successfully fetched teacher detail with students, id={teacher_id}")
        return teacher

    def add_teacher(self, name, gender, age, subject, phone):
        """add teacher to database"""
        db = TeacherDB()
        new_id = db.insert(name, gender, age, subject, phone)
        if not new_id:
            logger.warning(f"business check failed: insert no id, name={name}")
            raise BizException(msg="fail to add teacher", code=1)
        logger.info(f"successfully inserted, new id: {new_id}")
        return new_id

    def update_teacher(self, teacher_id, name, gender, age, subject, phone):
        """update teacher"""
        db = TeacherDB()
        if not db.get_one(teacher_id):
            logger.warning(f"business check failed: teacher not found, id={teacher_id}")
            raise BizException(msg=f"teacher not found, id={teacher_id}", code=NOT_EXIST)

        rowcount = db.update(teacher_id, name, gender, age, subject, phone)
        logger.info(f"successfully updated, teacher id: {teacher_id}")
        return rowcount

    def delete_teacher(self, teacher_id: int):
        """delete teacher"""
        db = TeacherDB()
        if not db.get_one(teacher_id):
            logger.warning(f"business check failed: teacher not found, id={teacher_id}")
            raise BizException(msg=f"teacher not found, id={teacher_id}", code=NOT_EXIST)

        rowcount = db.delete(teacher_id)
        logger.info(f"successfully deleted, teacher id: {teacher_id}")
        return rowcount