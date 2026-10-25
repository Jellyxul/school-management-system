"""
数据访问层，只执行sql
只与数据库交互
"""

from cn.jelly.common.basedao import get_all, get_one, execute, insert

# 列表查询公共片段：带出学生姓名与课程名称
_SELECT_WITH_NAMES = '''
SELECT e.*, stu.name AS student_name, c.name AS course_name
FROM enrollment e
JOIN student stu ON e.student_id = stu.id
JOIN subject c ON e.course_id = c.id
'''

class EnrollmentDB:
    """enrollment information management"""

    def get_all(self):
        """return all enrollment information with student and course names"""
        sql = _SELECT_WITH_NAMES + " ORDER BY e.id"
        return get_all(sql)

    def get_by_page(self, page, size, keyword=""):
        """return enrollment on term/student/course by page number"""
        where, args = "", []
        if keyword:
            where = "WHERE e.term LIKE %s OR stu.name LIKE %s OR c.name LIKE %s"
            args = [f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"]
        # 总数，条件必须与下面的列表查询一致
        total = get_one(
            f"SELECT count(*) AS total FROM enrollment e "
            f"JOIN student stu ON e.student_id = stu.id "
            f"JOIN subject c ON e.course_id = c.id {where}",
            args or None
        )["total"]
        # 当前页：LIMIT size OFFSET (page-1)*size
        rows = get_all(
            _SELECT_WITH_NAMES + f" {where} ORDER BY e.id LIMIT %s OFFSET %s",
            [*args, size, (page-1)*size]
        )
        return rows, total

    def get_one(self, enrollment_id):
        """return one enrollment information with student and course names"""
        sql = _SELECT_WITH_NAMES + " WHERE e.id=%s"
        return get_one(sql, (enrollment_id,))

    def insert(self, student_id, course_id, term, score, status):
        """insert enrollment，create_time 由数据库默认填充当前时间"""
        sql = '''
        INSERT INTO enrollment (student_id,course_id,term,score,status) VALUES
                    (%s,%s,%s,%s,%s)
                    '''
        return insert(sql, (student_id, course_id, term, score, status))

    def update(self, enrollment_id, student_id, course_id, term, status):
        """update enrollment，不含成绩（成绩由 update_score 单独录入）"""
        sql = '''
        UPDATE enrollment SET student_id=%s, course_id=%s, term=%s,
                           status=%s
        WHERE id=%s;
        '''
        return execute(sql, (student_id, course_id, term, status, enrollment_id))

    def update_score(self, enrollment_id, score, status):
        """update score and status only"""
        sql = '''
        UPDATE enrollment SET score=%s, status=%s WHERE id=%s;
        '''
        return execute(sql, (score, status, enrollment_id))

    def delete(self, enrollment_id):
        """delete enrollment"""
        sql = '''
        DELETE FROM enrollment WHERE id=%s;
        '''
        return execute(sql, (enrollment_id,))

if __name__ == '__main__':
    enrollment = EnrollmentDB()
    print(enrollment.get_all())
    print(enrollment.get_one('1'))
