"""
数据访问层，只执行sql
只与数据库交互
"""

from cn.jelly.common.basedao import get_one


class DashboardDB:
    """dashboard statistics"""

    def count_student(self):
        """学生总数"""
        sql = "SELECT COUNT(*) AS cnt FROM student"
        return get_one(sql)["cnt"]

    def count_teacher(self):
        """教师总数"""
        sql = "SELECT COUNT(*) AS cnt FROM teacher"
        return get_one(sql)["cnt"]

    def count_subject(self):
        """课程总数"""
        sql = "SELECT COUNT(*) AS cnt FROM subject"
        return get_one(sql)["cnt"]

    def count_clazz(self):
        """班级总数"""
        sql = "SELECT COUNT(*) AS cnt FROM clazz"
        return get_one(sql)["cnt"]


if __name__ == '__main__':
    dashboard = DashboardDB()
    print(dashboard.count_student())
    print(dashboard.count_teacher())
    print(dashboard.count_subject())
    print(dashboard.count_clazz())
