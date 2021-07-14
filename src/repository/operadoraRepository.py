from src.db import conexao


def getOperadoraByName(nomeOperadora):
    conn = conexao.myConexao()
    cursor = conn.cursor()

    sqlOperadora = f"SELECT * FROM tbl_operadora WHERE titulo like '{nomeOperadora}%';"

    res = cursor.execute(sqlOperadora)

    if res == 0:
        print(f"Nenhum operadora encontrada para: \n{sqlOperadora}")
        return []
    elif res == 1:
        return cursor.fetchone()
    print(sqlOperadora)
    return False
