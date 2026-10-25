
import pymysql
from dbutils.pooled_db import PooledDB

# pymysql 数据库连接参数
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '0611221',
    'database': 'school_db',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}

# 使用 PoolDB 建立数据库连接池,封装 pymysql 数据库连接参数
_pool = PooledDB(
    creator=pymysql,
    mincached=5,
    maxcached=5,
    maxconnections=10,
    maxusage=1000,
    # setsession=['set autocommit = 1'],
    ping=1,
    blocking=True,
    **DB_CONFIG
)

def get_conn():
    """一次从连接池中借一个连接，借完需要归还"""
    return _pool.connection()
