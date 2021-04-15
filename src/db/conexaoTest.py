import pymysql


def myConexao():
    return pymysql.connect(host="localhost", user="user", passwd="password", database="database")

# Inserir novos e atualizar os preços dos que ja existem
def inserirRegistro():
    return True

def updatePrecoPlano():
    return True

def atualizaDataReajuste():
    return True

def deletarRegistroDuplicado():
    return False