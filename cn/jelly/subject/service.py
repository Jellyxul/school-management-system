"""
业务逻辑层
承载业务逻辑、连接校验、写日志
是 API 与 DAO 之间的桥梁
"""
import logging

from cn.jelly.subject.dao import SubjectDB
from cn.jelly.teacher.dao import TeacherDB
from cn.jelly.common.config import MAX_PAGE_SIZE
from cn.jelly.common.exceptions import BizException, NOT_EXIST

from cn.jelly.teacher.service import TeacherService

# 模块日志记录
logger = logging.getLogger(__name__)


class SubjectService:
    def list_subjects(self):
        """show all subjects"""
        db = SubjectDB()
        data = db.get_all()
        logger.info("successfully fetched all subjects, total %d", len(data))
        return data

    def get_by_page(self, page=1, size=10, keyword=""):
        """get subject by page and size"""
        page = max(1, int(page))
        size = min(max(1, int(size)), MAX_PAGE_SIZE)
        db = SubjectDB()
        rows, total = db.get_by_page(page, size, keyword)
        logger.info(f"分页查：第{page}页 每页{size}条 关键字={keyword} 共{total}条")
        return {"total": total, "page": page, "size": size, "rows": rows}

    def get_subject(self, subject_id: int):
        """get one subject"""
        db = SubjectDB()
        sub = db.get_one(subject_id)
        if not sub:
            # 业务异常：课程不存在
            raise BizException(msg=f"subject not found, id={subject_id}", code=NOT_EXIST)
        logger.info(f"successfully fetched, subject id: {subject_id}")
        return sub

    def add_subject(self, name, credit, teacher_id):
        """add subject to database"""
        # 校验授课教师是否存在
        t_db = TeacherDB()
        if not t_db.get_one(teacher_id):
            logger.warning(f"business check failed: teacher not exists, teacher_id={teacher_id}")
            raise BizException(msg="授课教师不存在", code=NOT_EXIST)

        db = SubjectDB()
        new_id = db.insert(name, credit, teacher_id)
        if not new_id:
            logger.warning(f"business check failed: insert no id, name={name}")
            raise BizException(msg="fail to add subject", code=1)
        logger.info(f"successfully inserted, new id: {new_id}")
        return new_id

    def update_subject(self, subject_id, name, credit, teacher_id):
        """update subject"""
        db = SubjectDB()
        if not db.get_one(subject_id):
            logger.warning(f"business check failed: subject not found, id={subject_id}")
            raise BizException(msg=f"subject not found, id={subject_id}", code=NOT_EXIST)

        # 校验要更新成的 teacher_id 是否有效
        t_db = TeacherDB()
        if not t_db.get_one(teacher_id):
            logger.warning(f"business check failed: teacher not exists, teacher_id={teacher_id}")
            raise BizException(msg="授课教师不存在", code=NOT_EXIST)

        rowcount = db.update(subject_id, name, credit, teacher_id)
        logger.info(f"successfully updated, subject id: {subject_id}")
        return rowcount

    def delete_subject(self, subject_id: int):
        """delete subject"""
        db = SubjectDB()
        if not db.get_one(subject_id):
            logger.warning(f"business check failed: subject not found, id={subject_id}")
            raise BizException(msg=f"subject not found, id={subject_id}", code=NOT_EXIST)

        rowcount = db.delete(subject_id)
        logger.info(f"successfully deleted, subject id: {subject_id}")
        return rowcount

    def get_subject_detail(self, subject_id: int):
        """get subjects detail"""
        s_db = SubjectDB()
        t_db = TeacherService()
        # 查找课程信息
        subject = s_db.get_one(subject_id)
        if not subject:
            raise BizException(msg=f"subject not found, id={subject_id}", code=NOT_EXIST)
        # 获取任课教师id
        teacher_id = subject.get("teacher_id")
        if not teacher_id:
            raise BizException(msg="subject has no teacher", code=NOT_EXIST)
        #  复用教师详情（教师 + 其学生 + 人数）
        teacher_detail = t_db.get_teacher_detail(teacher_id)
        subject["teacher"] = teacher_detail
        logger.info(f"successfully fetched subject detail, id={subject_id}, teacher id: {teacher_id}")
        return subject


