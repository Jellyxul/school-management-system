"""
数据访问层，只执行sql
只与数据库交互
"""
from cn.jelly.common.basedao import get_all, get_one, execute, insert

class SubjectDB:
    """subject information management"""

    def get_all(self):
        """return all subject information"""
        sql = "SELECT * FROM subject"
        return get_all(sql)

    def get_by_page(self, page, size, keyword=""):
        """return subject on name by page number"""
        where, args = "", []
        if keyword:
            where = "WHERE name LIKE %s"
            args.append(f"%{keyword}%")
        # 总数
        total = get_one(f"SELECT count(*) AS total FROM subject {where}", args or None)["total"]
        # 当前页
        rows = get_all(
            f"SELECT * FROM subject {where} ORDER BY id LIMIT %s OFFSET %s",
            [*args, size, (page-1)*size]
        )
        return rows, total

    def get_one(self, subject_id):
        """return one subject information"""
        sql = "SELECT * FROM subject WHERE id=%s"
        return get_one(sql, (subject_id,))

    def insert(self, name, credit, teacher_id):
        """insert subject"""
        sql = '''
        INSERT INTO subject (name, credit, teacher_id) VALUES (%s, %s, %s)
        '''
        return insert(sql, (name, credit, teacher_id))

    def update(self, subject_id, name, credit, teacher_id):
        """update subject"""
        sql = '''
        UPDATE subject SET name=%s, credit=%s, teacher_id=%s WHERE id=%s;
        '''
        return execute(sql, (name, credit, teacher_id, subject_id))

    def delete(self, subject_id):
        """delete subject"""
        sql = '''
        DELETE FROM subject WHERE id=%s;
        '''
        return execute(sql, (subject_id,))