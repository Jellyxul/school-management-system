"""
业务逻辑层
承载业务逻辑、连接校验、写日志
是 API 与 DAO 之间的桥梁
"""
import logging

from cn.jelly.clazz.dao import ClazzDB
from cn.jelly.teacher.dao import TeacherDB
from cn.jelly.common.config import MAX_PAGE_SIZE
from cn.jelly.common.exceptions import BizException, NOT_EXIST

# 模块日志记录
logger = logging.getLogger(__name__)


class ClazzService:
    def list_clazzes(self):
        """show all clazzes"""
        db = ClazzDB()  # 此时实例化不再建立真实连接，没有性能损耗
        data = db.get_all()
        logger.info("successfully fetched all clazzes, total %d", len(data))
        return data

    def get_clazz(self, clazz_id: int):
        """get one clazz"""
        db = ClazzDB()
        clazz = db.get_one(clazz_id)
        if not clazz:
            # 业务异常：班级不存在
            raise BizException(msg=f"clazz not found, id={clazz_id}", code=NOT_EXIST)
        logger.info(f"successfully fetched, clazz id: {clazz_id}")
        return clazz

    def get_by_page(self, page=1, size=10, keyword=""):
        """get clazz by page and size"""
        page = max(1, int(page))  # 页码至少为 1
        size = min(max(1, int(size)), MAX_PAGE_SIZE)  # size 限制在 1~100
        db = ClazzDB()
        rows, total = db.get_by_page(page, size, keyword)
        logger.info(f"分页查：第{page}页 每页{size}条 关键字={keyword} 共{total}条")
        return {"total": total, "page": page, "size": size, "rows": rows}


    def add_clazz(self, name, code, teacher_id, address):
        """add clazz to database"""
        # 校验班主任是否存在
        t_db = TeacherDB()
        if not t_db.get_one(teacher_id):
            logger.warning(f"business check failed: teacher not exists, teacher_id={teacher_id}")
            raise BizException(msg="班主任不存在", code=NOT_EXIST)

        db = ClazzDB()
        new_id = db.insert(name, code, teacher_id, address)
        if not new_id:
            logger.warning(f"business check failed: insert no id, name={name}")
            raise BizException(msg="fail to add clazz", code=1)
        return new_id

    def update_clazz(self, clazz_id, name, code, teacher_id, address):
        """update clazz"""
        db = ClazzDB()
        if not db.get_one(clazz_id):
            logger.warning(f"business check failed: clazz not found, id={clazz_id}")
            raise BizException(msg=f"clazz not found, id={clazz_id}", code=NOT_EXIST)

        # 校验要更新成的 teacher_id 是否有效
        t_db = TeacherDB()
        if not t_db.get_one(teacher_id):
            logger.warning(f"business check failed: teacher not exists, teacher_id={teacher_id}")
            raise BizException(msg="班主任不存在", code=NOT_EXIST)

        rowcount = db.update(clazz_id, name, code, teacher_id, address)
        logger.info(f"successfully updated, clazz id: {clazz_id}")
        return rowcount

    def delete_clazz(self, clazz_id: int):
        """delete clazz"""
        db = ClazzDB()
        one = db.get_one(clazz_id)
        if not one:
            # service 层写日志，提示 business check failed
            logger.warning(f"business check failed: clazz not found, id={clazz_id}")
            # 业务异常：班级不存在
            raise BizException(msg=f"clazz not found, id={clazz_id}", code=NOT_EXIST)
        rowcount = db.delete(clazz_id)
        logger.info(f"successfully deleted, clazz id: {clazz_id}")
        return rowcount
