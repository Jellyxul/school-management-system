"""
业务逻辑层
承载业务逻辑、连接校验、写日志
是 API 与 DAO 之间的桥梁
"""
import logging

from cn.jelly.student.dao import StudentDB
from cn.jelly.teacher.dao import TeacherDB
from cn.jelly.common.config import MAX_PAGE_SIZE
from cn.jelly.common.exceptions import BizException, NOT_EXIST

# 模块日志记录
logger = logging.getLogger(__name__)


# 所有方法中均采用 try/finally，保证异常时也能关闭连接
# service 层抛出异常，由 api 层 except ValueError 捕获
# 成功路径才 logger.info，失败路径由 API 层记，避免日志重复



class StudentService:
    def list_students(self):
        """show all students"""
        db = StudentDB()  # 此时实例化不再建立真实连接，没有性能损耗
        data = db.get_all()
        logger.info("successfully fetched all students, total %d", len(data))
        return data

    def get_student(self, student_id: int):
        """get one student"""
        db = StudentDB()
        stu = db.get_one(student_id)
        if not stu:
            # 业务异常：学生不存在
            raise BizException(msg=f"student not found, id={student_id}", code=NOT_EXIST)
        logger.info(f"successfully fetched, student id: {student_id}")
        return stu

    def get_by_page(self, page=1, size=10, keyword=""):
        """get student by page and size"""
        page = max(1, int(page))  # 页码至少为 1
        size = min(max(1, int(size)), MAX_PAGE_SIZE)  # size 限制在 1~100
        db = StudentDB()
        rows, total = db.get_by_page(page, size, keyword)
        logger.info(f"分页查：第{page}页 每页{size}条 关键字={keyword} 共{total}条")
        return {"total": total, "page": page, "size": size, "rows": rows}


    def add_student(self, name, gender, age, teacher_id, grade, enrollment_date):
        """add student to database"""
        # 【新增】：校验教师是否存在
        t_db = TeacherDB()
        if not t_db.get_one(teacher_id):
            logger.warning(f"business check failed: teacher not exists, teacher_id={teacher_id}")
            raise BizException(msg="任课老师不存在", code=NOT_EXIST)

        db = StudentDB()
        new_id = db.insert(name, gender, age, teacher_id, grade, enrollment_date)
        if not new_id:
            logger.warning(f"business check failed: insert no id, name={name}")
            raise BizException(msg="fail to add student", code=1)
        return new_id

    def update_student(self, student_id, name, gender, age, teacher_id, grade, enrollment_date):
        """update student"""
        db = StudentDB()
        if not db.get_one(student_id):
            logger.warning(f"business check failed: student not found, id={student_id}")
            raise BizException(msg=f"student not found, id={student_id}", code=NOT_EXIST)

        # 【新增】：校验要更新成的 teacher_id 是否有效
        t_db = TeacherDB()
        if not t_db.get_one(teacher_id):
            logger.warning(f"business check failed: teacher not exists, teacher_id={teacher_id}")
            raise BizException(msg="任课老师不存在", code=NOT_EXIST)

        rowcount = db.update(student_id, name, gender, age, teacher_id, grade, enrollment_date)
        logger.info(f"successfully updated, student id: {student_id}")
        return rowcount

    def delete_student(self, student_id: int):
        """delete student"""
        db = StudentDB()
        one = db.get_one(student_id)
        if not one:
            # service 层写日志，提示 business check failed
            logger.warning(f"business check failed: student not found, id={student_id}")
            # 业务异常：学生不存在
            raise BizException(msg=f"student not found, id={student_id}", code=NOT_EXIST)
        rowcount = db.delete(student_id)
        logger.info(f"successfully deleted, student id: {student_id}")
        return rowcount