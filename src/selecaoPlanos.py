from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from src.db import conexao
import time
import re
from datetime import datetime


id_area = 0
id_operadora = 0
nome_operadora = ""
coparticipacao = 2
hospitalar = 0
tipo_contratacao = 0
id_tipo_empresa = 2

min_vidas = 0
max_vidas = 29
data_reajuste = None
id_administradora = 0
id_tipo_contratacao_lead = 1
id_tipo_tabela = None
regional = False
planos_sem_cadastros = []

def insertDados(sql, values):
    conn = conexao.myConexao()
    cursor = conn.cursor()
    res = cursor.execute(sql, values)

    cursor.close()
    conn.commit()
    conn.close()
    if res == 1:
        return True
    else:
        return False

def rasparDados(driver):

    # Ativar ou dasativar a persistencia de dados
    salvar = False

    global id_operadora
    global nome_operadora
    global coparticipacao
    global hospitalar
    global min_vidas
    global max_vidas
    global data_reajuste
    global id_administradora
    global id_tipo_contratacao_lead
    global tipo_contratacao
    global regional
    global id_tipo_empresa
    qtd_titulares = '0'
    planos_atualizados = []



    conn = conexao.myConexao()
    cursor = conn.cursor()

    print("Obtendo dados")
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    tables = soup.find_all('table', attrs={"static small ta-c"})

    for num_tables in range(1):

        titulo = driver.find_element_by_xpath('//*[@id="geral-content"]/section/div[2]/div[2]/div[1]/p').text

        if nome_operadora == 'BRADESCO':
            if re.search('3 Vidas', titulo):
                min_vidas = 0
                max_vidas = 29

            if re.search('02 Titulares', titulo):
                qtd_titulares = '2'
            elif re.search('01 Titular', titulo):
                qtd_titulares = '1'

        elif re.search('AMIL', nome_operadora) or nome_operadora == 'ONE HEALTH':
            if min_vidas == 0:
                min_vidas = 0
                max_vidas = 29
                qtd_titulares = '1'
            elif min_vidas > 29:
                min_vidas = 30
                max_vidas = 99
                qtd_titulares = '1'

        elif re.search('SULAMÉRICA', nome_operadora):
            if min_vidas == 0:
                min_vidas = 0
                max_vidas = 29
                qtd_titulares = '1'
            elif min_vidas > 29:
                min_vidas = 30
                max_vidas = 0
                qtd_titulares = '1'

            if re.search(' MEI', titulo):
                id_tipo_empresa = 1

        elif re.search('SOMPO', nome_operadora):
            if min_vidas == 0:
                min_vidas = 0
                max_vidas = 29
                qtd_titulares = '1'
            elif min_vidas > 29:
                min_vidas = 30
                max_vidas = 99
                qtd_titulares = '1'



        trs = tables[num_tables + 1].find_all('tr')

        dados = []
        for i, tr in enumerate(trs):
            soup = BeautifulSoup(str(tr), 'html.parser')
            tds = soup.find_all('td')

            # del (tds[0])
            if i == 0:
                for td in tds:
                    aux = [td.text]
                    dados.append(aux)

            if 0 < i < 11:
                for j, td in enumerate(tds):
                    dados[j].append(td.text)

        # print(dados)
        inseridos = 0
        del (dados[0])
        for dado in dados:

            print(dado)
            dado[0] = str(dado[0]).replace("(R1)", "R1")
            dado[0] = str(dado[0]).replace("(R2)", "R2")
            dado[0] = str(dado[0]).replace("(R3)", "R3")


            plano_modalidade = str(dado[0]).split("(")

            id_modalidade = plano_modalidade[1].strip().replace(")", "")
            if id_modalidade == "A":
                id_modalidade = 2
            if id_modalidade == "E":
                id_modalidade = 1


            plano = plano_modalidade[0].strip()

            # Variacao de nome de planos AMIL
            if plano == 'AMIL FÁCIL 50 ABC / BX':
                plano = 'AMIL FÁCIL 50 ABC'

            if regional:
                plano = f"{plano} REGIONAL"

            if (re.search('CLASSICO', plano) or re.search('CLÁSSICO', plano)) and (id_operadora == 2 or id_operadora == 5 or id_operadora == 8) :
                if id_modalidade == 1:
                    plano = "CLÁSSICO ENF"
                elif id_modalidade == 2:
                    plano = "CLÁSSICO APT"

            # Variacao de nome de planos SULAMERICA
            if re.search('SULAMÉRICA', nome_operadora):
                plano = plano.replace("- ", "")

                # variaçoes dos nomes dos planos (FORMATACAO)
                plano = plano.split('PREMIUM')[0].strip()
                plano = plano.split('SUPREMO')[0].strip()

            nome_plano = plano
            plano = plano.replace(" ", "")

            sql = f"select * from tbl_tipo_plano where id_operadora = {id_operadora} and replace(titulo, ' ', '') like '{plano}';"
            print(sql)
            res = cursor.execute(sql)
            valores = []
            print(res)

            if res > 0:
                result_select = cursor.fetchall()[0]
                print(result_select)
                id_plano = result_select[0]
                id_categoria_plano = result_select[3]
                if id_plano > 0:
                    for i, valor in enumerate(dado):
                        if i > 0:
                            valores.append(float(str(valor).split(" ")[1].replace(".", "").replace(",", ".")))

                    sql = "insert into tbl_preco_faixa_etaria (" \
                          "id_area, " \
                          "id_categoria_plano, " \
                          "id_coparticipacao, " \
                          "id_modalidade, " \
                          "id_operadora, " \
                          "id_tipo_contratacao, " \
                          "id_tipo_plano, " \
                          "preco0_18, " \
                          "preco19_23, " \
                          "preco24_28, " \
                          "preco29_33, " \
                          "preco34_38, " \
                          "preco39_43, " \
                          "preco44_48, " \
                          "preco49_53, " \
                          "preco54_58, " \
                          "preco_m59, " \
                          "qtd_titulares, " \
                          "id_sindicato, " \
                          "hospitalar, " \
                          "min_vidas, " \
                          "max_vidas, " \
                          "id_tipo_empresa, " \
                          "id_administradora, " \
                          "ultimo_reajuste, " \
                          "id_tipo_contratacao_lead, " \
                          "id_tipo_tabela ) " \
                          "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"

                    values = (
                        id_area,  # id_area
                        id_categoria_plano,  # id_categoria_plano
                        coparticipacao,  # id_coparticipacao
                        id_modalidade,  # id_modalidade,
                        id_operadora,  # id_operadora
                        tipo_contratacao,  # id_tipo_contratacao
                        id_plano,  # id_tipo_plano
                        valores[0],  # preco0_18
                        valores[1],  #
                        valores[2],
                        valores[3],
                        valores[4],
                        valores[5],
                        valores[6],
                        valores[7],
                        valores[8],
                        valores[9],  # preco_m59
                        qtd_titulares,  # qtd_titulares
                        None,  # id_sindicato
                        hospitalar,  # hospitalar
                        min_vidas,  # min_vidas
                        max_vidas,  # max_vidas
                        id_tipo_empresa,  # id_tipo_empresa
                        id_administradora,  # id_administradora
                        data_reajuste,  # ultimo_reajuste
                        id_tipo_contratacao_lead,  # id_tipo_contratacao_lead
                        id_tipo_tabela  # id_tipo_tabela
                    )

                    teste = "select * from tbl_preco_faixa_etaria " \
                            f"where id_area = {id_area} and id_operadora = {id_operadora} and id_tipo_plano = {id_plano} and id_modalidade = {id_modalidade} " \
                            f"and id_tipo_contratacao = {tipo_contratacao} and id_coparticipacao = {coparticipacao} and qtd_titulares = {qtd_titulares} " \
                            f"and min_vidas = {min_vidas} and id_sindicato is null and id_tipo_empresa = {id_tipo_empresa} and hospitalar = {hospitalar};"
                    print(teste)
                    res = cursor.execute(teste)
                    print(res)


                    print(values, " -- extraidos do simulador")

                    if res == 1:
                        select = cursor.fetchall()[0]

                        id = select[0]
                        preco0_18 = select[8]
                        ultimo_reajuste = select[25]

                        print(select[1:28], f"ID: {id} -- banco de dados")

                        # Condicao para alterar a data do reajuste caso os precos estejam iguais mais sem data
                        # if ultimo_reajuste is None:
                        #     update = f"UPDATE `tbl_preco_faixa_etaria` SET `ultimo_reajuste`='{data_reajuste}' WHERE `id`='{id}';"
                        #     print(update)
                        #     cursor.execute(update)

                        # print(type(preco0_18), type(valores[0]))
                        # print(preco0_18, valores[0])
                        if not preco0_18 == valores[0] : #and not ultimo_reajuste == data_reajuste
                            print("Atualizar Precos! -----")
                            planos_atualizados.append(plano)

                            if ultimo_reajuste == None:
                                ultimo_reajuste = "null"
                            else:
                                ultimo_reajuste = datetime.strptime(str(ultimo_reajuste), '%Y-%m-%d').date()
                            print(ultimo_reajuste)

                            update = "UPDATE `tbl_preco_faixa_etaria` SET " \
                                     f"`preco0_18`='{valores[0]}', " \
                                     f"`preco19_23`='{valores[1]}', " \
                                     f"`preco24_28`='{valores[2]}', " \
                                     f"`preco29_33`='{valores[3]}', " \
                                     f"`preco34_38`='{valores[4]}', " \
                                     f"`preco39_43`='{valores[5]}', " \
                                     f"`preco44_48`='{valores[6]}', " \
                                     f"`preco49_53`='{valores[7]}', " \
                                     f"`preco54_58`='{valores[8]}', " \
                                     f"`preco_m59`='{valores[9]}', " \
                                     f"`ultimo_reajuste`='{data_reajuste}' " \
                                     f"WHERE `id`='{id}';"
                            print(update)

                            if salvar:
                                res = cursor.execute(update)
                            else:
                                res = 1

                            # res = 1
                            print(res)
                            if res == 1:


                                insert = "insert into tbl_historico_precos_planos " \
                                         "(id_preco_faixa_etaria, preco0_18, preco19_23, preco24_28, preco29_33, preco34_38, preco39_43, preco44_48, preco49_53, preco54_58, preco_m59, data_validade ) " \
                                         "values " \
                                         f"({id}, {select[8]}, {select[9]}, {select[10]}, {select[11]}, {select[12]}, {select[13]}, {select[14]}, {select[15]}, {select[16]}, {select[17]}, '{ultimo_reajuste}'); "
                                print(insert)
                                if salvar:
                                    res = cursor.execute(insert)
                                    print(res, "sucesso")



                            # if not insertDados(sql, values):
                            #     print("ERROR: erro ao inserir precos no banco de dados!")
                            # else:
                            #     print("Deletando registro desatualizado")
                            #     delete = f"delete from tbl_preco_faixa_etaria where id = {id}"
                            #     cursor.execute(delete)
                    elif res == 0:
                        print("------------------------------- Cadastrar Novo")
                        print(f'{sql} {values}')

                        if salvar:
                        # if False:

                            if not insertDados(sql, values):
                                print("ERROR: erro ao inserir precos no banco de dados!")
                            else:
                                inseridos += 1
                    elif res > 1:
                        print("Mais de um plano cadastrado")



                # print(values ,",")

            # Colocar em uma lista os planos nao encontrados
            elif res == 0:
                ref_plano = True
                for plan in planos_sem_cadastros:
                    if plan == nome_plano:
                        ref_plano = False

                if ref_plano:
                    planos_sem_cadastros.append(f"{nome_plano}")

        print(f"Total de preços de planos atulizados: {inseridos}")
    cursor.close()
    conn.commit()
    conn.close()

    print(f"Planos que nao foram encontrados: \n {planos_sem_cadastros}")
    print(f"Planos que sofreram alteracoes: \n {planos_atualizados}")

def verificarAtualizacao(driver, num):

    global data_reajuste
    global id_operadora
    global id_area
    global nome_operadora
    global tipo_contratacao
    global coparticipacao
    global hospitalar
    global regional


    conn = conexao.myConexao()
    cursor = conn.cursor()

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f'//*[@id="div-planos-loaded"]/table/tbody/tr[{num + 1}]/td[1]/p'))
        )
    except:
        print('Nao achou o elemento da pagina! Tendando novamente')
        verificarAtualizacao(driver, num)

    finally:
        nome_operadora = driver.find_element_by_xpath(
            f'//*[@id="div-planos-loaded"]/table/tbody/tr[{num + 1}]/td[1]/p').text

        if re.search('HOSPITALAR', nome_operadora):
            tipo_contratacao = 2
        # else:
        #     tipo_contratacao = str(driver.find_element_by_xpath(
        #         f'//*[@id="div-planos-loaded"]/table/tbody/tr[{num + 1}]/td[1]/b').text)
        # pass

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, f'//*[@id="div-planos-loaded"]/table/tbody/tr[{num + 1}]/td[1]/b'))
            )
        except:
            tipo_contratacao = None
        finally:
            if not tipo_contratacao == None:
                tipo_contratacao = str(driver.find_element_by_xpath(
                    f'//*[@id="div-planos-loaded"]/table/tbody/tr[{num + 1}]/td[1]/b').text)
            pass

    print(nome_operadora)
    print(tipo_contratacao, "\n")


    if re.search('BRADESCO', nome_operadora):
        tag_operadora = nome_operadora
        nome_operadora = str(nome_operadora).split(" ")[0]

        # Verificar de a area e de sao paulo
        if driver.find_element_by_xpath('//*[@id="simulacao_regiao"]/option[25]').is_selected():

            # Pegar a area do plano
            if re.search('INTERIOR 1', tag_operadora):
                area = 'INTERIOR 1'
            elif re.search('INTERIOR 2', tag_operadora):
                area = 'INTERIOR 2'
            else:
                area = 'SP CAPITAL'

            # Verificar se e hospitalar
            if re.search('HOSPITALAR', tag_operadora):
                hospitalar = 2
            else:
                hospitalar = 1

            tipo_contratacao = str(tipo_contratacao).split("-")
            print(tipo_contratacao)
            if len(tipo_contratacao) > 1:
                coparticipacao = tipo_contratacao[1]

                if re.search('10', coparticipacao):
                    coparticipacao = 1
                elif re.search('20', coparticipacao):
                    coparticipacao = 3
                elif re.search('30', coparticipacao):
                    coparticipacao = 5

            tipo_contratacao = tipo_contratacao[0].strip()

            tipo_contratacao = list(tipo_contratacao.lower())
            tipo_contratacao = f"{tipo_contratacao[0]+tipo_contratacao[1]+tipo_contratacao[2]}"

    # Verificando apenas AMIL e Amil Facil
    if re.search('AMIL -', str(nome_operadora).upper()) \
            or re.search('AMIL FÁCIL -', str(nome_operadora).upper()) \
            or re.search('AMIL ONE -', str(nome_operadora).upper()):

        tag_operadora = nome_operadora

        if re.search('AMIL FÁCIL -', str(nome_operadora).upper()):
            nome_operadora = str(nome_operadora).split(" -")[0]
        elif re.search('AMIL ONE -', str(nome_operadora).upper()):
            nome_operadora = 'ONE HEALTH'
        else:
            nome_operadora = str(nome_operadora).split(" ")[0]

        # Verificar de a area e de sao paulo
        if driver.find_element_by_xpath('//*[@id="simulacao_regiao"]/option[25]').is_selected():

            if re.search('SEM COPART', str(tag_operadora).upper()):
                coparticipacao = 2
            elif re.search('COM COPART', str(tag_operadora).upper()):
                coparticipacao = 1

            # Verificar se e hospitalar
            if re.search('HOSPITALAR', tag_operadora):
                hospitalar = 2
            else:
                hospitalar = 1

            if re.search('INTERIOR', str(tipo_contratacao).upper()) or re.search('INTERIOR', str(tag_operadora).upper()):
                area = 'INTERIOR 1'
            else:
                area = 'SP CAPITAL'

            if re.search('LIVRE ADESÃO', str(tipo_contratacao).upper()):
                tipo_contratacao = 'OPCI'
            elif re.search('COMPULSÓRIA', str(tipo_contratacao).upper()):
                tipo_contratacao = 'COMP'

    if re.search('SULAMÉRICA', str(nome_operadora).upper()):

        tag_operadora = nome_operadora
        nome_operadora = nome_operadora.split(" ")[0]

        # if re.search('AMIL FÁCIL -', str(nome_operadora).upper()):
        #     nome_operadora = str(nome_operadora).split(" -")[0]
        # elif re.search('AMIL ONE -', str(nome_operadora).upper()):
        #     nome_operadora = 'ONE HEALTH'
        # else:
        #     nome_operadora = str(nome_operadora).split(" ")[0]

        # Verificar de a area e de sao paulo
        if driver.find_element_by_xpath('//*[@id="simulacao_regiao"]/option[25]').is_selected():

            if re.search('SEM COPART', str(tag_operadora).upper()):
                coparticipacao = 2
            elif re.search('COM COPART', str(tag_operadora).upper()):

                if re.search('10', tipo_contratacao):
                    coparticipacao = 1
                elif re.search('20', tipo_contratacao):
                    coparticipacao = 3
                elif re.search('30', tipo_contratacao):
                    coparticipacao = 5


            # Verificar se e hospitalar
            if re.search('HOSPITALAR', tag_operadora):
                hospitalar = 2
            else:
                hospitalar = 1

            if re.search('TARIFA 1', str(tag_operadora).upper()):
                area = 'SP CAPITAL'
            elif re.search('TARIFA 2', str(tag_operadora).upper()):
                area = 'INTERIOR 1'
            elif re.search('TARIFA 3', str(tag_operadora).upper()):
                area = 'INTERIOR 2'
            else:
                area = 'SP CAPITAL'

            if re.search('COMPULSÓRIO', str(tag_operadora).upper()):
                tipo_contratacao = 'COMP'
            else:
                tipo_contratacao = 'OPCI'


    if re.search('SOMPO', str(nome_operadora).upper()):

        tag_operadora = nome_operadora
        nome_operadora = "SOMPO SAÚDE"

        # Verificar de a area e de sao paulo
        if driver.find_element_by_xpath('//*[@id="simulacao_regiao"]/option[25]').is_selected():

            if re.search('SEM COPART', str(tag_operadora).upper()):
                coparticipacao = 2
            elif re.search('COM COPART', str(tag_operadora).upper()):

                if re.search('10', tipo_contratacao):
                    coparticipacao = 1
                elif re.search('20', tipo_contratacao):
                    coparticipacao = 3
                elif re.search('30', tipo_contratacao):
                    coparticipacao = 5


            # Verificar se e hospitalar
            if re.search('HOSPITALAR', tag_operadora):
                hospitalar = 2
            else:
                hospitalar = 1

            if re.search('INTERIOR', str(tag_operadora).upper()):
                area = 'INTERIOR 1'
            else:
                area = 'SP CAPITAL'

            if re.search('REGIONAL', str(tipo_contratacao).upper()):
                regional = True
            else:
                regional = False

            if re.search('OPCIONAL', str(tipo_contratacao).upper()):
                tipo_contratacao = 'OPCI'
            else:
                tipo_contratacao = 'COMP'



    sql = f"select * from tbl_operadora, tbl_area, tbl_tipo_contratacao where tbl_operadora.titulo like '{nome_operadora}' and tbl_area.area like '%{area}%' and  tbl_tipo_contratacao.titulo like '%{tipo_contratacao}%';"
    print(sql)
    res = cursor.execute(sql)

    data_reajuste = driver.find_element_by_xpath(
        f'//*[@id="div-planos-loaded"]/table/tbody/tr[{num + 1}]/td[2]/ul/li[1]').get_attribute(
        'title')
    data_reajuste = str(data_reajuste).split("/")
    data_reajuste = f'{data_reajuste[2]}-{data_reajuste[1]}-{data_reajuste[0]}'

    # Converter a string em objeto tipo Date
    data_reajuste = datetime.strptime(str(data_reajuste), '%Y-%m-%d').date()
    print(data_reajuste)

    # print(res)
    if res > 0:
        select = cursor.fetchall()[0]
        id_operadora = select[0]
        id_area = select[3]
        tipo_contratacao = select[5]

        # print(id_operadora, id_area, tipo_contratacao)

    sql = f"select * from tbl_preco_faixa_etaria " \
          f"where id_operadora = {id_operadora} " \
          f"and id_area = {id_area} " \
          f"and hospitalar = {hospitalar} " \
          f"and id_tipo_contratacao = {tipo_contratacao} " \
          f"and id_coparticipacao = {coparticipacao} " \
          f"and ultimo_reajuste = '{data_reajuste}';"

    print(f"\n{sql}")

    res = cursor.execute(sql)
    print(res)
    cursor.close()
    conn.close()
    return True
    # if res == 0:
    #     # Precisa pegar os dados
    #     return True
    #
    # # Os dados ja estao atualizados
    # return False


def selecionarPlano(driver, num):
    driver.execute_script(f"document.getElementsByClassName('select-all')[{num}].click()")
    time.sleep(2)
    driver.execute_script("document.getElementById('btSubmit').click()")

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'fz-12'))
        )
    finally:
        rasparDados(driver)
        print("Voltando para simulacao")
        driver.execute_script("history.back()")


def obterDados(driver, tipo_tabela_option):
    # TIPO DE PLANO -> saude
    driver.find_element_by_xpath('//*[@id="simulacao_tipoPlano"]/option[2]').click()

    # Tipo de Tabela
    driver.find_element_by_xpath(f'//*[@id="simulacao_tipoTabela"]/option[{tipo_tabela_option}]').click()

    # desmarcar as informaçoes opcionais
    for i in range(5):
        driver.find_element_by_id(f"simulacao_info_{str(i)}").click()

    # colocar no minimo uma vida por faixa_etaria
    for i in range(10):
        # driver.find_element_by_xpath(f'//*[@id="simulacao_faixas_{str(i)}_vidas"]').send_keys(Keys.DELETE)
        driver.find_element_by_xpath(f'//*[@id="simulacao_faixas_{str(i)}_vidas"]').clear()
        if min_vidas >= 29 and i == 5:
            driver.find_element_by_xpath(f'//*[@id="simulacao_faixas_{str(i)}_vidas"]').send_keys(30)
        else:
            driver.find_element_by_xpath(f'//*[@id="simulacao_faixas_{str(i)}_vidas"]').send_keys(1)

    # pesquisar
    time.sleep(1)
    driver.find_element_by_id('btn-get-planos').click()
    time.sleep(3)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'sim-op-planos'))
        )
    except:
        print("Erro ao listar os planos")
        driver.close()
    finally:
        time.sleep(1)
        quantidade_results = len(driver.find_elements_by_class_name('sim-op-planos'))
        print(f"Achou {quantidade_results} na pesquisa!")

        if quantidade_results == 0:
            obterDados(driver, tipo_tabela_option)

        for i in range(quantidade_results):

            if i >= 0 and i < 1000:
                print("\n")
                print(f"Lendo resultado: {i+1}")

                if driver.find_element_by_id('btn-get-planos').is_displayed():
                    # time.sleep(1)
                    driver.find_element_by_id('btn-get-planos').click()
                    time.sleep(1)
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, f'//*[@id="div-planos-loaded"]/table/tbody/tr[{i + 1}]'))
                    )
                finally:
                    # time.sleep(1)
                    nome_operadora = driver.find_element_by_xpath(
                        f'//*[@id="div-planos-loaded"]/table/tbody/tr[{i + 1}]/td[1]/p').text

                    # FUNCIONANDO - BRADESCO SEM O 4 VIDAS
                    # if re.search('BRADESCO', nome_operadora) and not re.search('4 vidas', nome_operadora):
                    #
                    #     try:
                    #         WebDriverWait(driver, 10).until(
                    #             EC.presence_of_element_located(
                    #                 (By.XPATH, f'//*[@id="div-planos-loaded"]/table/tbody/tr[{i + 1}]'))
                    #         )
                    #     except:
                    #         print("Erro ao listar os planos")
                    #     finally:
                    #         pass
                    #
                    #     if verificarAtualizacao(driver, i):
                    #         # print(True)
                    #         selecionarPlano(driver, i)
                    #     else:
                    #         print(False)

                    # Funcionando o AMIL (id_operadora = 2)
                    # if re.search('AMIL -', str(nome_operadora).upper()) and not str(nome_operadora).upper() == 'AMIL - Linha Coordenada':
                    #
                    #     try:
                    #         WebDriverWait(driver, 10).until(
                    #             EC.presence_of_element_located(
                    #                 (By.XPATH, f'//*[@id="div-planos-loaded"]/table/tbody/tr[{i + 1}]'))
                    #         )
                    #     except:
                    #         print("Erro ao listar os planos")
                    #     finally:
                    #         pass
                    #
                    #     print(nome_operadora)
                    #     if verificarAtualizacao(driver, i):
                    #         print(True)
                    #         selecionarPlano(driver, i)
                    #     else:
                    #         print(False)


                    # Funcionando
                    # if re.search('AMIL FÁCIL -', str(nome_operadora).upper()):
                    #
                    #     try:
                    #         WebDriverWait(driver, 10).until(
                    #             EC.presence_of_element_located(
                    #                 (By.XPATH, f'//*[@id="div-planos-loaded"]/table/tbody/tr[{i + 1}]'))
                    #         )
                    #     except:
                    #         print("Erro ao listar os planos")
                    #         driver.close()
                    #     finally:
                    #         pass
                    #
                    #     # print(nome_operadora)
                    #     # print(driver.find_element_by_xpath(f'//*[@id="div-planos-loaded"]/table/tbody/tr[{i+1}]/td[1]/b').text, "\n")
                    #     if verificarAtualizacao(driver, i):
                    #         print(True)
                    #         selecionarPlano(driver, i)
                    #     else:
                    #         print(False)

                    # Amil ONE (funcionando)
                    # if re.search('AMIL ONE -', str(nome_operadora).upper()):
                    #
                    #     try:
                    #         WebDriverWait(driver, 10).until(
                    #             EC.presence_of_element_located(
                    #                 (By.XPATH, f'//*[@id="div-planos-loaded"]/table/tbody/tr[{i + 1}]'))
                    #         )
                    #     except:
                    #         print("Erro ao listar os planos")
                    #     finally:
                    #         pass
                    #
                    #     print(nome_operadora)
                    #     print(driver.find_element_by_xpath(f'//*[@id="div-planos-loaded"]/table/tbody/tr[{i+1}]/td[1]/b').text, "\n")
                    #     if verificarAtualizacao(driver, i):
                    #         print(True)
                    #         selecionarPlano(driver, i)
                    #     else:
                    #         print(False)

                    # if re.search('SULAMÉRICA', str(nome_operadora).upper()):
                    #
                    #     try:
                    #         WebDriverWait(driver, 10).until(
                    #             EC.presence_of_element_located(
                    #                 (By.XPATH, f'//*[@id="div-planos-loaded"]/table/tbody/tr[{i + 1}]'))
                    #         )
                    #     except:
                    #         print("Erro ao listar os planos")
                    #     finally:
                    #         pass
                    #
                    #         # print(nome_operadora)
                    #         # print(driver.find_element_by_xpath(f'//*[@id="div-planos-loaded"]/table/tbody/tr[{i+1}]/td[1]/b').text, "\n")
                    #         if verificarAtualizacao(driver, i):
                    #             print(True)
                    #             selecionarPlano(driver, i)
                    #         else:
                    #             print(False)

                    # if re.search('SOMPO', str(nome_operadora).upper()):
                    #
                    #     try:
                    #         WebDriverWait(driver, 10).until(
                    #             EC.presence_of_element_located(
                    #                 (By.XPATH, f'//*[@id="div-planos-loaded"]/table/tbody/tr[{i + 1}]'))
                    #         )
                    #     except:
                    #         print("Erro ao listar os planos")
                    #     finally:
                    #         pass
                    #
                    #     # print(nome_operadora)
                    #     # print(driver.find_element_by_xpath(f'//*[@id="div-planos-loaded"]/table/tbody/tr[{i+1}]/td[1]/b').text, "\n")
                    #     if verificarAtualizacao(driver, i):
                    #         print(True)
                    #         selecionarPlano(driver, i)
                    #     else:
                    #         print(False)

                    if re.search('SULAMÉRICA', str(nome_operadora).upper()) and re.search(' MEI', str(nome_operadora).upper()):

                        try:
                            WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located(
                                    (By.XPATH, f'//*[@id="div-planos-loaded"]/table/tbody/tr[{i + 1}]'))
                            )
                        except:
                            print("Erro ao listar os planos")
                        finally:
                            pass

                            # print(nome_operadora)
                            # print(driver.find_element_by_xpath(f'//*[@id="div-planos-loaded"]/table/tbody/tr[{i+1}]/td[1]/b').text, "\n")
                            if verificarAtualizacao(driver, i):
                                print(True)
                                selecionarPlano(driver, i)
                            else:
                                print(False)


                    # try:
                    #     WebDriverWait(driver, 10).until(
                    #         EC.presence_of_element_located(
                    #             (By.XPATH, f'//*[@id="div-planos-loaded"]/table/tbody/tr[{i + 1}]'))
                    #     )
                    # except:
                    #     print("Erro ao listar os planos")
                    # finally:
                    #     pass
                    #
                    # # print(nome_operadora)
                    # # print(driver.find_element_by_xpath(f'//*[@id="div-planos-loaded"]/table/tbody/tr[{i+1}]/td[1]/b').text, "\n")
                    # if verificarAtualizacao(driver, i):
                    #     print(True)
                    #     selecionarPlano(driver, i)
                    # else:
                    #     print(False)