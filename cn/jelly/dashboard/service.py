"""
业务逻辑层
聚合各模块统计数据，供首页数据看板展示
"""
import logging

from cn.jelly.dashboard.dao import DashboardDB

# 模块日志记录
logger = logging.getLogger(__name__)


class DashboardService:
    def get_stats(self):
        """首页看板统计：学生/教师/课程/班级总数"""
        db = DashboardDB()
        # 各表单独容错：某表尚未建表（如未执行对应 SQL 脚本）时按 0 处理，
        # 避免单个模块缺失导致看板整体加载失败
        stats = {
            "student_count": self._safe_count(db.count_student, "student"),
            "teacher_count": self._safe_count(db.count_teacher, "teacher"),
            "subject_count": self._safe_count(db.count_subject, "subject"),
            "clazz_count": self._safe_count(db.count_clazz, "clazz"),
        }
        logger.info(f"dashboard stats: {stats}")
        return stats

    @staticmethod
    def _safe_count(fn, table):
        """执行单个计数，异常（如表不存在）时记日志并返回 0"""
        try:
            return fn()
        except Exception as e:
            logger.warning(f"count {table} failed, treat as 0: {e}")
            return 0
