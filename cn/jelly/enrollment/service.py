"""
业务逻辑层
承载业务逻辑、连接校验、写日志
是 API 与 DAO 之间的桥梁
"""
import logging

from cn.jelly.enrollment.dao import EnrollmentDB
from cn.jelly.student.dao import StudentDB
from cn.jelly.subject.dao import SubjectDB
from cn.jelly.arrangement.service import get_current_term
from cn.jelly.common.config import MAX_PAGE_SIZE
from cn.jelly.common.exceptions import BizException, NOT_EXIST

# 模块日志记录
logger = logging.getLogger(__name__)


class EnrollmentService:
    def list_enrollments(self):
        """show all enrollments"""
        db = EnrollmentDB()  # 此时实例化不再建立真实连接，没有性能损耗
        data = db.get_all()
        logger.info("successfully fetched all enrollments, total %d", len(data))
        return data

    def get_enrollment(self, enrollment_id: int):
        """get one enrollment"""
        db = EnrollmentDB()
        enrollment = db.get_one(enrollment_id)
        if not enrollment:
            # 业务异常：选课记录不存在
            raise BizException(msg=f"enrollment not found, id={enrollment_id}", code=NOT_EXIST)
        logger.info(f"successfully fetched, enrollment id: {enrollment_id}")
        return enrollment

    def get_by_page(self, page=1, size=10, keyword=""):
        """get enrollment by page and size"""
        page = max(1, int(page))  # 页码至少为 1
        size = min(max(1, int(size)), MAX_PAGE_SIZE)  # size 限制在 1~100
        db = EnrollmentDB()
        rows, total = db.get_by_page(page, size, keyword)
        logger.info(f"分页查：第{page}页 每页{size}条 关键字={keyword} 共{total}条")
        return {"total": total, "page": page, "size": size, "rows": rows}


    def add_enrollment(self, student_id, course_id, term, score, status):
        """add enrollment to database"""
        # 校验学生是否存在
        stu_db = StudentDB()
        if not stu_db.get_one(student_id):
            logger.warning(f"business check failed: student not exists, student_id={student_id}")
            raise BizException(msg="学生不存在", code=NOT_EXIST)

        # 校验课程是否存在
        c_db = SubjectDB()
        if not c_db.get_one(course_id):
            logger.warning(f"business check failed: course not exists, course_id={course_id}")
            raise BizException(msg="课程不存在", code=NOT_EXIST)

        # 学期不传时默认当前学期
        if not term:
            term = get_current_term()
            logger.info(f"term not given, use current term: {term}")

        db = EnrollmentDB()
        new_id = db.insert(student_id, course_id, term, score, status)
        if not new_id:
            logger.warning(f"business check failed: insert no id, student_id={student_id}")
            raise BizException(msg="fail to add enrollment", code=1)
        return new_id

    def update_enrollment(self, enrollment_id, student_id, course_id, term, status):
        """update enrollment，不含成绩（成绩由 update_score 单独录入）"""
        db = EnrollmentDB()
        if not db.get_one(enrollment_id):
            logger.warning(f"business check failed: enrollment not found, id={enrollment_id}")
            raise BizException(msg=f"enrollment not found, id={enrollment_id}", code=NOT_EXIST)

        # 校验要更新成的 student_id 是否有效
        stu_db = StudentDB()
        if not stu_db.get_one(student_id):
            logger.warning(f"business check failed: student not exists, student_id={student_id}")
            raise BizException(msg="学生不存在", code=NOT_EXIST)

        # 校验要更新成的 course_id 是否有效
        c_db = SubjectDB()
        if not c_db.get_one(course_id):
            logger.warning(f"business check failed: course not exists, course_id={course_id}")
            raise BizException(msg="课程不存在", code=NOT_EXIST)

        rowcount = db.update(enrollment_id, student_id, course_id, term, status)
        logger.info(f"successfully updated, enrollment id: {enrollment_id}")
        return rowcount

    def update_score(self, enrollment_id, score, status):
        """录入/修改成绩与状态，score 为 None 表示未录入（清空成绩）"""
        db = EnrollmentDB()
        if not db.get_one(enrollment_id):
            logger.warning(f"business check failed: enrollment not found, id={enrollment_id}")
            raise BizException(msg=f"enrollment not found, id={enrollment_id}", code=NOT_EXIST)

        rowcount = db.update_score(enrollment_id, score, status)
        logger.info(f"successfully updated score, enrollment id: {enrollment_id}, score: {score}")
        return rowcount

    def delete_enrollment(self, enrollment_id: int):
        """delete enrollment"""
        db = EnrollmentDB()
        one = db.get_one(enrollment_id)
        if not one:
            # service 层写日志，提示 business check failed
            logger.warning(f"business check failed: enrollment not found, id={enrollment_id}")
            # 业务异常：选课记录不存在
            raise BizException(msg=f"enrollment not found, id={enrollment_id}", code=NOT_EXIST)
        rowcount = db.delete(enrollment_id)
        logger.info(f"successfully deleted, enrollment id: {enrollment_id}")
        return rowcount
