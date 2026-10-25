"""
数据访问层，只执行sql
只与数据库交互
"""

from cn.jelly.common.basedao import get_all, get_one, execute, insert

class ClazzDB:
    """clazz information management"""

    def get_all(self):
        """return all clazz information"""
        sql = "SELECT * FROM clazz"
        return get_all(sql)

    def get_by_page(self, page, size, keyword=""):
        """return clazz on name by page number"""
        where, args = "", []
        if keyword:
            where = "WHERE name LIKE %s"
            args.append(f"%{keyword}%")
        # 总数，条件必须与下面的列表查询一致
        total = get_one(f"SELECT count(*) AS total FROM clazz {where}", args or None)["total"]
        # 当前页：LIMIT size OFFSET (page-1)*size
        rows = get_all(
            f"SELECT * FROM clazz {where} ORDER BY id LIMIT %s OFFSET %s",
            [*args, size, (page-1)*size]
        )
        return rows, total


    def get_one(self, clazz_id):
        """return one clazz information"""
        sql = "SELECT * FROM clazz WHERE id=%s"
        return get_one(sql, (clazz_id,))

    def insert(self, name, code, teacher_id, address):
        """insert clazz，create_time 由数据库默认填充当前时间"""
        sql = '''
        INSERT INTO clazz (name,code,teacher_id,address) VALUES
                    (%s,%s,%s,%s)
                    '''
        return insert(sql, (name, code, teacher_id, address))

    def update(self, clazz_id, name, code, teacher_id, address):
        """update clazz"""
        sql = '''
        UPDATE clazz SET name=%s, code=%s, teacher_id=%s,
                           address=%s
        WHERE id=%s;
        '''
        return execute(sql, (name, code, teacher_id, address, clazz_id))

    def delete(self, clazz_id):
        """delete clazz"""
        sql = '''
        DELETE FROM clazz WHERE id=%s;
        '''
        return execute(sql, (clazz_id,))

if __name__ == '__main__':
    clazz = ClazzDB()
    print(clazz.get_all())
    print(clazz.get_one('1'))
