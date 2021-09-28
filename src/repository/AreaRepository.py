from src.db import conexao
from src.model.Area import Area

conn = conexao.myConexao()
cursor = conn.cursor()


def findAll():
    sql = f"SELECT * FROM tbl_area;"

    cursor.execute(sql)
    return cursor.fetchall()


def findByName(name):

    if name == 'SÃO PAULO':
        name = 'SP CAPITAL'
    sql = f"SELECT * FROM tbl_area WHERE area like '{name.upper()}';"
    print(sql)
    cursor.execute(sql)
    res = cursor.fetchone()

    return Area(res[0], res[1], res[2])


