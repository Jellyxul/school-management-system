"""
数据访问层，只执行sql
只与数据库交互
"""

from cn.jelly.common.basedao import get_all, get_one, execute, insert

class StudentDB:
    """student information management"""

    def get_all(self):
        """return all student information"""
        sql = "SELECT * FROM student"
        return get_all(sql)

    def get_by_page(self, page, size, keyword=""):
        """return student on name by page number"""
        where, args = "", []
        if keyword:
            where = "WHERE name LIKE %s"
            args.append(f"%{keyword}%")
        # 总数，条件必须与下面的列表查询一致
        total = get_one(f"SELECT count(*) AS total FROM student {where}", args or None)["total"]
        # 当前页：LIMIT size OFFSET (page-1)*size
        rows = get_all(
            f"SELECT * FROM student {where} ORDER BY id LIMIT %s OFFSET %s",
            [*args, size, (page-1)*size]
        )
        return rows, total


    def get_one(self, student_id):
        """return one student information"""
        sql = "SELECT * FROM student WHERE id=%s"
        return get_one(sql, (student_id,))

    def insert(self, name, gender, age, teacher_id, grade, enrollment_date):
        """insert student"""
        sql = '''
        INSERT INTO student (name,gender,age,teacher_id,grade,enrollment_date) VALUES
                    (%s,%s,%s,%s,%s,%s)
                    '''
        return insert(sql, (name, gender, age, teacher_id, grade, enrollment_date))

    def update(self, student_id, name, gender, age, teacher_id, grade, enrollment_date):
        """update student"""
        sql = '''
        UPDATE student SET name=%s, gender=%s, age=%s, teacher_id=%s,
                           grade=%s, enrollment_date=%s
        WHERE id=%s;
        '''
        return execute(sql, (name, gender, age, teacher_id, grade, enrollment_date, student_id))

    def delete(self,student_id):
        """delete student"""
        sql = '''
        DELETE FROM student WHERE id=%s;
        '''
        return execute(sql, (student_id,))

    def get_by_teacher_id(self, teacher_id):
        """return students by teacher id"""
        sql = "SELECT * FROM student WHERE teacher_id = %s"
        return get_all(sql, (teacher_id,))

if __name__ == '__main__':
    stu = StudentDB()
    print(stu.get_all())
    print(stu.get_one('1'))




