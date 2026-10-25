"""
数据访问层，只执行sql
只与数据库交互
"""

from cn.jelly.common.basedao import get_all, get_one, execute, insert

# 列表查询公共片段：带出课程名称与教师名称
_SELECT_WITH_NAMES = '''
SELECT a.*, s.name AS course_name, t.name AS teacher_name
FROM arrangement a
JOIN subject s ON a.course_id = s.id
JOIN teacher t ON a.teacher_id = t.id
'''

class ArrangementDB:
    """arrangement information management"""

    def get_all(self):
        """return all arrangement information with course and teacher names"""
        sql = _SELECT_WITH_NAMES + " ORDER BY a.id"
        return get_all(sql)

    def get_by_page(self, page, size, keyword=""):
        """return arrangement on term/classroom by page number"""
        where, args = "", []
        if keyword:
            where = "WHERE a.term LIKE %s OR a.classroom LIKE %s"
            args = [f"%{keyword}%", f"%{keyword}%"]
        # 总数，条件必须与下面的列表查询一致
        total = get_one(f"SELECT count(*) AS total FROM arrangement a {where}", args or None)["total"]
        # 当前页：LIMIT size OFFSET (page-1)*size
        rows = get_all(
            _SELECT_WITH_NAMES + f" {where} ORDER BY a.id LIMIT %s OFFSET %s",
            [*args, size, (page-1)*size]
        )
        return rows, total

    def get_one(self, arrangement_id):
        """return one arrangement information"""
        sql = "SELECT * FROM arrangement WHERE id=%s"
        return get_one(sql, (arrangement_id,))

    def insert(self, course_id, teacher_id, term, classroom, class_time):
        """insert arrangement，create_time 由数据库默认填充当前时间"""
        sql = '''
        INSERT INTO arrangement (course_id,teacher_id,term,classroom,class_time) VALUES
                    (%s,%s,%s,%s,%s)
                    '''
        return insert(sql, (course_id, teacher_id, term, classroom, class_time))

    def update(self, arrangement_id, course_id, teacher_id, term, classroom, class_time):
        """update arrangement"""
        sql = '''
        UPDATE arrangement SET course_id=%s, teacher_id=%s, term=%s,
                           classroom=%s, class_time=%s
        WHERE id=%s;
        '''
        return execute(sql, (course_id, teacher_id, term, classroom, class_time, arrangement_id))

    def delete(self, arrangement_id):
        """delete arrangement"""
        sql = '''
        DELETE FROM arrangement WHERE id=%s;
        '''
        return execute(sql, (arrangement_id,))

if __name__ == '__main__':
    arrangement = ArrangementDB()
    print(arrangement.get_all())
    print(arrangement.get_one('1'))
