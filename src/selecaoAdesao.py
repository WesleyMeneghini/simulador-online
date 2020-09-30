import time
from bs4 import BeautifulSoup
import re
from src.db import conexao
from datetime import datetime

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

navegador_aberto = False

adm = 1
ope = 1
ent = 1
hospitalar = 1
id_operadora = 0
nome_administradora = ""

tipo_tabela_option = 0
administradora_option = 1
operadora_option = 1
entidade_option = 1

id_coparticipacao = 0
id_administradora = 0

count_result = 0

nome_administradora_option = ''
nome_operadora_option = ''
nome_entidade_option = ''

planos_sem_cadastros = []

min_vidas = 0
max_vidas = 0
ultimo = False

def aguardandoCarregamento(string, element):
    if string == element:
        return False
    else:
        return True

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


def pegarDados(driver, cursor, id_sindicato, data_reajuste):
    # Ativar ou dasativar a persistencia de dados


    salvar = conexao.inserirRegistro()
    deletar_duplicados = conexao.deletarRegistroDuplicado()

    global nome_administradora
    global planos_sem_cadastros
    global hospitalar
    global id_coparticipacao
    global id_operadora
    global min_vidas
    global max_vidas
    global ultimo
    id_area = 0
    planos_atualizados = []

    time.sleep(4)

    print("Obtendo dados:")
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'bgGray'))
        )
    finally:
        pass

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    tables = soup.find_all('table', attrs={"static small ta-c"})

    tipo_contratacao_lead = driver.find_elements_by_class_name('titulo')[0].text

    if re.search('Adesão', tipo_contratacao_lead):
        id_tipo_contratacao_lead = 0

    operadora_tipocoparticipacao = str(
        driver.find_element_by_xpath('//*[@id="geral-content"]/section/div[2]/div[2]/div[1]/p').text)

    if re.search('COM COPART', operadora_tipocoparticipacao.upper()):
        id_coparticipacao = 1
    elif re.search('SEM COPART', operadora_tipocoparticipacao.upper()):
        id_coparticipacao = 2
    elif re.search('HOSPITALAR', operadora_tipocoparticipacao.upper()):
        id_coparticipacao = 2
        hospitalar = 2

    print("Pegando precos!")
    if ultimo :
        quant = 1
    else:
        quant = 2
    for num_tables in range(quant):
        info_sindicato = ""
        sindicato_name = ""
        if num_tables == 0:
            titulo = str(driver.find_element_by_xpath('//*[@id="geral-content"]/section/div[2]/div[2]/div[2]/b').text)

            info_sindicato = driver.find_element_by_xpath('//*[@id="geral-content"]/section/div[2]/div[2]/div[3]').text
            sindicato_name = driver.find_element_by_xpath('//*[@id="geral-content"]/section/div[2]/div[2]/div[3]/b').text

        if num_tables == 1:
            titulo = str(driver.find_element_by_xpath('//*[@id="geral-content"]/section/div[2]/div[2]/div[5]/b').text)
            info_sindicato = driver.find_element_by_xpath('//*[@id="geral-content"]/section/div[2]/div[2]/div[6]').text
            sindicato_name = driver.find_element_by_xpath(
                '//*[@id="geral-content"]/section/div[2]/div[2]/div[6]/b').text

        print(f"{operadora_tipocoparticipacao}\n \n{titulo}\n{info_sindicato}\n")

        titulo = titulo.split("-")
        if len(titulo) > 1:
            area = titulo[1].strip()
            numero_vidas = titulo[2].strip()
        else:
            area = 'SP CAPITAL'
            numero_vidas = 'APENAS TITULAR'

        tipo_tabela = titulo[0].strip()

        sql = f"select * from tbl_tipo_tabela, tbl_sindicato where nome like '%{tipo_tabela}%' and titulo like '%{str(sindicato_name).strip()}%';"
        res = cursor.execute(sql)

        if res > 0:
            select = cursor.fetchall()[0]
            print(f"Sindicato do banco de dados: {select[1:-1]}")
            id_tipo_tabela = select[0]
            id_sindicato = select[2]

            if numero_vidas == 'APENAS TITULAR':
                min_vidas = 0
                # Se a Operadora for AMIL, alterar o numero maximo de vidas
                if id_operadora == 2:
                    max_vidas = 0
                else:
                    max_vidas = 1
            elif numero_vidas == 'TITULAR + DEPENDENTES':
                min_vidas = 2
                max_vidas = 0

            sql = f"select * from tbl_area, tbl_administradora where area like '%{area}%' and  titulo like 'QUALICORP';"
            # print(sql)
            res = cursor.execute(sql)
            if res > 0:
                select = cursor.fetchall()[0]
                id_area = select[0]
                id_administradora = select[2]

                trs = tables[num_tables + 1].find_all('tr')

                dados = []
                # dados =      "plano", "preco 0 a 18", ""
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
                    # print(dado)
                    plano_modalidade = str(dado[0]).split("(")

                    id_modalidade = plano_modalidade[1].strip().replace(")", "")
                    if id_modalidade == "A":
                        id_modalidade = 2
                    if id_modalidade == "E":
                        id_modalidade = 1

                    plano = plano_modalidade[0].strip()

                    # variaçoes dos nomes dos planos (FORMATACAO)
                    plano = plano.split('PREMIUM')[0].strip()
                    plano = plano.split('SUPREMO')[0].strip()

                    # variaçoes dos nomes de planos da BRADESCO
                    if id_operadora == 3:
                        if plano == 'SAÚDE EFETIVO IV':
                            plano = "Efetivo III"
                        elif plano == "NACIONAL FLEX E CA":
                            plano = "FLEX"
                        elif plano == "NACIONAL FLEX Q CA":
                            plano = "FLEX"
                        elif plano == "TOP NACIONAL E CA":
                            plano = "Top Nacional E"
                        elif plano == "TOP NACIONAL Q CA":
                            plano = "Top Nacional Q"
                        elif plano == "TOP NPLUS3 Q CA":
                            plano = "NP03"
                        elif plano == "TOP NPLUS4 Q CA":
                            plano = "NP04"
                        elif plano == "TOP NPLUS6 Q CA":
                            plano = "NP06"

                        min_vidas = 0
                        max_vidas = 0

                    sql = f"select * from tbl_planos_sindicato where titulo like '%{plano}%';"
                    # print(sql)
                    res = cursor.execute(sql)
                    valores = []
                    # print(res)

                    if res == 1:
                        result_select = cursor.fetchall()[0]
                        print(result_select)
                        id_plano = result_select[0]
                        id_categoria_plano = result_select[4]
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
                                id_coparticipacao,  # id_coparticipacao
                                id_modalidade,  # id_modalidade,
                                id_operadora,  # id_operadora
                                2,  # id_tipo_contratacao
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
                                str(1),  # qtd_titulares
                                id_sindicato,  # id_sindicato
                                hospitalar,  # hospitalar
                                min_vidas,  # min_vidas
                                max_vidas,  # max_vidas
                                2,  # id_tipo_empresa
                                id_administradora,  # id_administradora
                                data_reajuste,  # ultimo_reajuste
                                id_tipo_contratacao_lead,  # id_tipo_contratacao_lead
                                id_tipo_tabela  # id_tipo_tabela
                            )

                            teste = "select * from tbl_preco_faixa_etaria " \
                                    f"where id_area = {id_area} and id_operadora = {id_operadora} and id_tipo_plano = {id_plano} and id_modalidade = {id_modalidade} " \
                                    f"and id_coparticipacao = {id_coparticipacao} and qtd_titulares = 1 " \
                                    f"and min_vidas = {min_vidas} and max_vidas = {max_vidas} and id_sindicato = {id_sindicato} and hospitalar = {hospitalar};"
                            print(teste)
                            res = cursor.execute(teste)

                            print(values, " -- extraidos do simulador")

                            if res == 1:
                                select = cursor.fetchall()[0]

                                id = select[0]
                                preco0_18 = select[8]
                                ultimo_reajuste = select[25]

                                print(select[1:28], f"ID: {id} -- banco de dados")

                                # if ultimo_reajuste is None:
                                #     update = f"UPDATE `tbl_preco_faixa_etaria` SET `ultimo_reajuste`='{data_reajuste}' WHERE `id`='{id}';"
                                #     print(update)
                                #     cursor.execute(update)

                                # print(type(preco0_18), type(valores[0]))
                                # print(preco0_18, valores[0])
                                if not preco0_18 == valores[0]:  # and not ultimo_reajuste == data_reajuste
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
                                if deletar_duplicados:
                                    id_item_duplicado = cursor.fetchall()[0][0]
                                    sql = f"delete from tbl_preco_faixa_etaria where id = {id_item_duplicado};"
                                    print(sql)
                                    res = cursor.execute(sql)
                                    if res > 0:
                                        print("Item deletado com sucesso")

                        # print(values ,",")

                    elif res > 1:
                        print(f"Mais de um plano encontrado: {cursor.fetchall()}")

                    # Colocar em uma lista os planos nao encontrados
                    elif res == 0:
                        ref_plano = True
                        for plan in planos_sem_cadastros:
                            if plan == plano:
                                ref_plano = False

                        if ref_plano:
                            planos_sem_cadastros.append(plano)

                print(f"Total de preços de planos atulizados: {inseridos}")

        elif res == 0:
            print("Nao achou o sindicato")

    print(planos_sem_cadastros)


def simulacaoAdesao(driver, administradora_option, operadora_option, entidade_option):
    global nome_administradora_option
    global nome_operadora_option
    global nome_entidade_option
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, f'//*[@id="simulacao_adesao_administradora"]/option[{administradora_option}]'))
        )
    finally:
        while aguardandoCarregamento("display: block; position: static; zoom: 1;",
                                     driver.find_element_by_id('div-adesao').get_attribute('style')):
            pass
        if not str(nome_administradora_option) == str(driver.find_element_by_xpath(
                   f'//*[@id="simulacao_adesao_administradora"]/option[{administradora_option}]').text):
            simulacaoAdesao(driver, administradora_option, operadora_option, entidade_option)
    # Selecionar a Adimistradora
    administradora = driver.find_element_by_xpath(
        f'//*[@id="simulacao_adesao_administradora"]/option[{administradora_option}]')
    administradora.click()



    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, f'//*[@id="simulacao_adesao_opes"]/option[{operadora_option}]'))
        )
    except:
        print("Nao achou a Operadora!")
        driver.close()
        exec()
    finally:
        while aguardandoCarregamento("display: block; position: static; zoom: 1;",
                                     driver.find_element_by_id('div-adesao').get_attribute('style')):
            pass
        if not str(nome_operadora_option) == str(
                driver.find_element_by_xpath(f'//*[@id="simulacao_adesao_opes"]/option[{operadora_option}]').text):
            simulacaoAdesao(driver, administradora_option, operadora_option, entidade_option)

    # Selecionando a operadora
    operadora = driver.find_element_by_xpath(f'//*[@id="simulacao_adesao_opes"]/option[{operadora_option}]').click()
    while aguardandoCarregamento("display: block; position: static; zoom: 1;", driver.find_element_by_id('div-adesao').get_attribute('style')):
        pass

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, f'//*[@id="simulacao_adesao_entidade"]/option[{entidade_option}]'))
        )
    except:
        print("Nao achou a Entidade!")
        driver.close()
        exec()
    finally:
        while aguardandoCarregamento("display: block; position: static; zoom: 1;",
                                     driver.find_element_by_id('div-adesao').get_attribute('style')):
            pass
        if not str(nome_entidade_option) == str(
                driver.find_element_by_xpath(f'//*[@id="simulacao_adesao_entidade"]/option[{entidade_option}]').text):
            simulacaoAdesao(driver, administradora_option, operadora_option, entidade_option)

    driver.find_element_by_xpath(f'//*[@id="simulacao_adesao_entidade"]/option[{entidade_option}]').click()
    while aguardandoCarregamento("display: block; position: static; zoom: 1;", driver.find_element_by_id('div-adesao').get_attribute('style')):
        pass

    # pesquisar
    time.sleep(0.5)
    driver.execute_script("document.getElementById('btn-get-planos').click()")
    time.sleep(0.5)
    # driver.find_element_by_id('btn-get-planos').click()
    # while aguardandoCarregamento("position: static; zoom: 1; margin-top: 0px;", driver.find_element_by_id('div-planos').get_attribute('style')):
    #     pass


def obterDados(driver, tipo_tabela_option, administradora_option, operadora_option, entidade_option):
    global hospitalar
    global id_coparticipacao
    global id_operadora
    global min_vidas

    global nome_administradora_option
    global nome_operadora_option
    global nome_entidade_option
    global ultimo

    conn = conexao.myConexao()
    cursor = conn.cursor()

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

    # TIPO DE PLANO -> saude
    driver.find_element_by_xpath('//*[@id="simulacao_tipoPlano"]/option[2]').click()

    # Tipo de Tabela
    driver.find_element_by_xpath(f'//*[@id="simulacao_tipoTabela"]/option[{tipo_tabela_option}]').click()
    while aguardandoCarregamento("display: block; position: static; zoom: 1;", driver.find_element_by_id('div-adesao').get_attribute('style')):
        pass

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, f'//*[@id="simulacao_adesao_administradora"]/option[{administradora_option}]'))
        )
    except:
        print("Nao achou a administradora!")
        driver.close()
        exec()
    finally:
        pass

    # Selecionar a Adimistradora
    administradora = driver.find_element_by_xpath(
        f'//*[@id="simulacao_adesao_administradora"]/option[{administradora_option}]')
    nome_administradora_option = administradora.text
    if nome_administradora_option != '':
        administradora.click()
        while aguardandoCarregamento("display: block; position: static; zoom: 1;", driver.find_element_by_id('div-adesao').get_attribute('style')):
            pass
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, f'//*[@id="simulacao_adesao_opes"]/option[{operadora_option}]'))
            )
        except:
            print("Nao achou a Operadora!")
            driver.close()
            exec()
        finally:
            pass

        # Selecionando a operadora
        operadora = driver.find_element_by_xpath(f'//*[@id="simulacao_adesao_opes"]/option[{operadora_option}]')
        nome_operadora_option = operadora.text
        # print("selecionando operadora")
        if nome_operadora_option != '':

            # variaçoes dos nomes AMIL
            if re.search('AMIL', operadora.text):
                nome_operadora = str(operadora.text).split('-')[0].strip()
            else:
                nome_operadora = str(operadora.text).split(' ')[0]

            sql = f"select * from tbl_operadora where titulo like '{nome_operadora}';"
            # print(sql)
            res = cursor.execute(sql)
            if res > 0:
                # print("Achou a operadora!")
                id_operadora = cursor.fetchall()[0][0]

                if re.search('COM COPART', operadora.text):
                    id_coparticipacao = 1
                elif re.search('SEM COPART', operadora.text):
                    id_coparticipacao = 2
                elif re.search('HOSPITALAR', operadora.text):
                    id_coparticipacao = 2
                    hospitalar = 2

                operadora.click()
                while aguardandoCarregamento("display: block; position: static; zoom: 1;", driver.find_element_by_id('div-adesao').get_attribute('style')):
                    pass
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, f'//*[@id="simulacao_adesao_entidade"]/option[{entidade_option}]'))
                    )
                except:
                    print("Nao achou a Entidade!")
                    driver.close()
                    exec()
                finally:
                    pass
                # print("selecionando entidade")
                entidades_selecionada = driver.find_element_by_xpath(
                    f'//*[@id="simulacao_adesao_entidade"]/option[{entidade_option}]')
                nome_entidade_option = entidades_selecionada.text
                entidades_selecionada.click()
                while aguardandoCarregamento("display: block; position: static; zoom: 1;", driver.find_element_by_id('div-adesao').get_attribute('style')):
                    pass

                # quantidade de entidades
                quantidade_operadoras = len(
                    driver.find_element_by_id('simulacao_adesao_entidade').find_elements_by_tag_name('option')) - 1
                # print('Quantidade de Entidades:', quantidade_operadoras)

                # pesquisar
                driver.find_element_by_id('btn-get-planos').click()
                # while aguardandoCarregamento("position: static; zoom: 1; margin-top: 0px;", driver.find_element_by_id('div-planos').get_attribute('style')):
                #     pass
                try:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located(
                            (By.CLASS_NAME, 'sim-op-planos'))
                    )
                finally:
                    time.sleep(1)
                    quantidade_results = len(driver.find_elements_by_class_name('sim-op-planos'))
                    print(f"Achou {quantidade_results} na pesquisa!")

                    count = 0
                    for i in range(0, quantidade_results, 2):

                        # print(f"\nLendo resultados {i} e {i + 1} ...")


                        if i >= 0 and i <= 1000:
                            print(f"\nLendo resultados {i+1} e {i + 2} ...")
                            if count > 0:
                                simulacaoAdesao(driver, administradora_option, operadora_option, entidade_option)

                            count = 1

                            try:
                                WebDriverWait(driver, 15).until(
                                    EC.presence_of_element_located(
                                        (By.CLASS_NAME, 'sim-op-planos'))
                                )
                            finally:

                                entidade_nome = driver.find_element_by_xpath(
                                    f'//*[@id="div-planos-loaded"]/table/tbody/tr[{i + 1}]/td[1]/span/strong').text
                                sql = f"select * from tbl_sindicato where titulo like '%{entidade_nome}%';"
                                res = cursor.execute(sql)
                                if res > 0:
                                    id_sindicato = cursor.fetchall()[0][0]

                                    data_reajuste = driver.find_element_by_xpath(
                                        f'//*[@id="div-planos-loaded"]/table/tbody/tr[{i + 1}]/td[2]/ul/li[1]').get_attribute(
                                        'title')
                                    data_reajuste = str(data_reajuste).split("/")
                                    data_reajuste = f'{data_reajuste[2]}-{data_reajuste[1]}-{data_reajuste[0]}'

                                    tipo_area = str(driver.find_element_by_xpath(
                                        f'//*[@id="div-planos-loaded"]/table/tbody/tr[{i + 1}]/td[1]/b').text).split(
                                        "-")

                                    if len(tipo_area) > 1:

                                        area_nome = str(driver.find_element_by_xpath(
                                            f'//*[@id="div-planos-loaded"]/table/tbody/tr[{i + 1}]/td[1]/b').text).split(
                                            "-")[1].strip()

                                        sql = f"select * from tbl_area where area like '%{area_nome}%';"
                                        res = cursor.execute(sql)
                                        if res > 0:
                                            id_area = cursor.fetchall()[0][0]
                                        else:
                                            print("Nao achou a area Selecionada")
                                    else:
                                        if str(driver.find_element_by_xpath(
                                                '//*[@id="simulacao_regiao"]/option[25]').text) == "São Paulo":
                                            id_area = 1

                                    sql = f"select * from tbl_preco_faixa_etaria where id_operadora = {id_operadora} and id_sindicato = {id_sindicato} and ultimo_reajuste = '{data_reajuste}' and id_area = {id_area} and hospitalar = {hospitalar};"
                                    res = cursor.execute(sql)
                                    if res >= 0:
                                        # if res > 0:
                                        # print(f"Nome do sindicato '{entidade_nome}'")

                                        if i+1 >= quantidade_results:
                                            driver.execute_script(
                                                f"document.getElementsByClassName('select-all')[{i}].click();")
                                            ultimo = True
                                        else:
                                            driver.execute_script(
                                                f"document.getElementsByClassName('select-all')[{i}].click();"
                                                f"document.getElementsByClassName('select-all')[{i + 1}].click();")
                                        time.sleep(0.5)

                                        driver.execute_script("document.getElementById('btSubmit').click()")
                                        time.sleep(0.5)

                                        pegarDados(driver, cursor, id_sindicato, data_reajuste)

                                        driver.execute_script("history.back()")
                                        time.sleep(0.5)

    cursor.close()
    conn.commit()
    conn.close()

    # time.sleep(10)
    # driver.close()
