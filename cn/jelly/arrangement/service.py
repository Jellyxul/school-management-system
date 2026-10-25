"""
业务逻辑层
承载业务逻辑、连接校验、写日志
是 API 与 DAO 之间的桥梁
"""
import logging
from datetime import datetime

from cn.jelly.arrangement.dao import ArrangementDB
from cn.jelly.subject.dao import SubjectDB
from cn.jelly.teacher.dao import TeacherDB
from cn.jelly.common.config import MAX_PAGE_SIZE
from cn.jelly.common.exceptions import BizException, NOT_EXIST

# 模块日志记录
logger = logging.getLogger(__name__)


def get_current_term():
    """计算当前学期，如 2026-2027-1"""
    today = datetime.now()
    y, m = today.year, today.month
    if m >= 8:
        # 8~12月：学年第 y~y+1 第 1 学期
        start, no = y, 1
    elif m == 1:
        # 1月：仍属学年第 y-1~y 第 1 学期
        start, no = y - 1, 1
    else:
        # 2~7月：学年第 y-1~y 第 2 学期
        start, no = y - 1, 2
    return f"{start}-{start + 1}-{no}"


class ArrangementService:
    def list_arrangements(self):
        """show all arrangements"""
        db = ArrangementDB()  # 此时实例化不再建立真实连接，没有性能损耗
        data = db.get_all()
        logger.info("successfully fetched all arrangements, total %d", len(data))
        return data

    def get_arrangement(self, arrangement_id: int):
        """get one arrangement"""
        db = ArrangementDB()
        arrangement = db.get_one(arrangement_id)
        if not arrangement:
            # 业务异常：排课不存在
            raise BizException(msg=f"arrangement not found, id={arrangement_id}", code=NOT_EXIST)
        logger.info(f"successfully fetched, arrangement id: {arrangement_id}")
        return arrangement

    def get_by_page(self, page=1, size=10, keyword=""):
        """get arrangement by page and size"""
        page = max(1, int(page))  # 页码至少为 1
        size = min(max(1, int(size)), MAX_PAGE_SIZE)  # size 限制在 1~100
        db = ArrangementDB()
        rows, total = db.get_by_page(page, size, keyword)
        logger.info(f"分页查：第{page}页 每页{size}条 关键字={keyword} 共{total}条")
        return {"total": total, "page": page, "size": size, "rows": rows}


    def add_arrangement(self, course_id, teacher_id, term, classroom, class_time):
        """add arrangement to database"""
        # 校验课程是否存在
        s_db = SubjectDB()
        if not s_db.get_one(course_id):
            logger.warning(f"business check failed: course not exists, course_id={course_id}")
            raise BizException(msg="课程不存在", code=NOT_EXIST)

        # 校验教师是否存在
        t_db = TeacherDB()
        if not t_db.get_one(teacher_id):
            logger.warning(f"business check failed: teacher not exists, teacher_id={teacher_id}")
            raise BizException(msg="教师不存在", code=NOT_EXIST)

        # 学期不传时默认当前学期
        if not term:
            term = get_current_term()
            logger.info(f"term not given, use current term: {term}")

        db = ArrangementDB()
        new_id = db.insert(course_id, teacher_id, term, classroom, class_time)
        if not new_id:
            logger.warning(f"business check failed: insert no id, course_id={course_id}")
            raise BizException(msg="fail to add arrangement", code=1)
        return new_id

    def update_arrangement(self, arrangement_id, course_id, teacher_id, term, classroom, class_time):
        """update arrangement"""
        db = ArrangementDB()
        if not db.get_one(arrangement_id):
            logger.warning(f"business check failed: arrangement not found, id={arrangement_id}")
            raise BizException(msg=f"arrangement not found, id={arrangement_id}", code=NOT_EXIST)

        # 校验要更新成的 course_id 是否有效
        s_db = SubjectDB()
        if not s_db.get_one(course_id):
            logger.warning(f"business check failed: course not exists, course_id={course_id}")
            raise BizException(msg="课程不存在", code=NOT_EXIST)

        # 校验要更新成的 teacher_id 是否有效
        t_db = TeacherDB()
        if not t_db.get_one(teacher_id):
            logger.warning(f"business check failed: teacher not exists, teacher_id={teacher_id}")
            raise BizException(msg="教师不存在", code=NOT_EXIST)

        rowcount = db.update(arrangement_id, course_id, teacher_id, term, classroom, class_time)
        logger.info(f"successfully updated, arrangement id: {arrangement_id}")
        return rowcount

    def delete_arrangement(self, arrangement_id: int):
        """delete arrangement"""
        db = ArrangementDB()
        one = db.get_one(arrangement_id)
        if not one:
            # service 层写日志，提示 business check failed
            logger.warning(f"business check failed: arrangement not found, id={arrangement_id}")
            # 业务异常：排课不存在
            raise BizException(msg=f"arrangement not found, id={arrangement_id}", code=NOT_EXIST)
        rowcount = db.delete(arrangement_id)
        logger.info(f"successfully deleted, arrangement id: {arrangement_id}")
        return rowcount
