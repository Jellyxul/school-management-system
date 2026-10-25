"""
数据访问层，只执行sql
只与数据库交互
"""
from cn.jelly.common.basedao import get_all, get_one, execute, insert

class TeacherDB:
    """teacher information management"""

    def get_all(self):
        """return all teacher information"""
        sql = "SELECT * FROM teacher"
        return get_all(sql)

    def get_one(self, teacher_id):
        """return one teacher information"""
        sql = "SELECT * FROM teacher WHERE id=%s"
        return get_one(sql, (teacher_id,))

    def insert(self, name, gender, age, subject, phone):
        """insert teacher"""
        sql = '''
        INSERT INTO teacher (name, gender, age, subject, phone)
        VALUES (%s, %s, %s, %s, %s)
        '''
        return insert(sql, (name, gender, age, subject, phone))

    def update(self, teacher_id, name, gender, age, subject, phone):
        """update teacher"""
        sql = '''
        UPDATE teacher SET name=%s, gender=%s, age=%s, subject=%s, phone=%s WHERE id=%s
        '''
        return execute(sql, (name, gender, age, subject, phone, teacher_id))

    def delete(self, teacher_id):
        """delete teacher"""
        sql = "DELETE FROM teacher WHERE id=%s"
        return execute(sql, (teacher_id,))