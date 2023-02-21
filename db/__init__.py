import os
from urllib.parse import urlparse
import MySQLdb

# データベースの接続情報
db_info = urlparse(os.environ["DATABASE_URL"])
db_conn = MySQLdb.connect(host=db_info.hostname,
                          user=db_info.username,
                          passwd=db_info.password,
                          db=db_info.path[1:],
                          ssl_mode="VERIFY_IDENTITY",
                          ssl={
                              "ca": "/etc/ssl/cert.pem"
                          })


# 指定したテーブルが存在するかどうか
def is_table_exists(table_name):
    with db_conn.cursor() as cursor:
        sql=f"SHOW TABLES LIKE '{table_name}';"
        cursor.execute(sql)
        hit_num=cursor.fetchone()[0]

        return hit_num > 0


def register_user(line_id):
    with db_conn.cursor() as cursor:
        # line_usersテーブルが存在していなかったら作成
        if not is_table_exists("line_users"):
            sql="""
                CREATE TABLE line_users (
                    id INT NOT NULL AUTO_INCREMENT,
                    user_id VARCHAR(255) NOT NULL,
                    PRIMARY KEY (id)
                );
            """
            cursor.execute(sql)
            db_conn.commit()

        # 既にそのユーザーが存在するか確認
        sql=f"SELECT COUNT(*) FROM line_users WHERE user_id = '{line_id}';"
        cursor.execute(sql)
        hit_num=cursor.fetchone()[0]

        if hit_num > 0:
            return

        # 存在しなければ初登録
        sql=f"INSERT INTO line_users (user_id) VALUES ('{line_id}');"
        cursor.execute(sql)
        db_conn.commit()
