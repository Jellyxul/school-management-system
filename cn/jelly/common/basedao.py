"""
通用操作文件
"""
from cn.jelly.common.pool import get_conn

def get_all(sql, args=None):
    """search all"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql,args)
            return cur.fetchall()

def get_one(sql, args=None):
    """search one"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql,args)
            return cur.fetchone()\

def execute(sql, args=None):
    """写入操作，覆盖增删改操作，返回影响行数"""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql,args)
            rowcount = cur.rowcount
        conn.commit()
        return rowcount
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()

def insert(sql, args=None):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            new_id = cur.lastrowid
        conn.commit()
        return new_id
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()



if __name__ == '__main__':
    sql = "SELECT * FROM student"
    print(get_all(sql))
    sql_one = "SELECT * FROM student WHERE id=%s"
    print(get_one(sql_one,(1,)))
    # 增
    sql_add =  '''
        INSERT INTO student (name,gender,age,teacher_id,grade,enrollment_date) 
        VALUES (%s,%s,%s,%s,%s,%s)
                    '''
    print(execute(sql_add,('aaa','male',18,1,'高三','2026-10-19 00:00:00')))
    print(insert(sql_add,('aaa','male',18,1,'高三','2026-10-19 00:00:00')))
    # # 删
    # sql_del = """DELETE FROM student WHERE id=%(student_id)s;"""
    # # print(execcute(sql_del,()))
    # 改
    sql_update =  '''
        UPDATE student SET name=%s, gender=%s, age=%s, teacher_id=%s,
                           grade=%s, enrollment_date=%s
        WHERE id=%s;
        '''
    print(execute(sql_update,('aaa','male',18,1,'高三','2026-10-19 00:00:00',1)))
