# from selenium import webdriver
#
# teste = webdriver.Chrome()

from bs4 import BeautifulSoup
from datetime import datetime

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import time
import re

from src.acesso import getNumberWhatsNotificationPrice
from src.db import conexao
from src.services import apiWhats

conn = conexao.myConexao()
cursor = conn.cursor()

salvar = conexao.inserirRegistro()
atualizarDataReajuste = conexao.atualizaDataReajuste()
updatePrecoPlano = conexao.updatePrecoPlano()

idArea = 0


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


def obterPrecos(table):
    trs = table.find_elements_by_tag_name('tr')

    dados = []
    id_modalidade = 0
    for i, tr in enumerate(trs):
        tds = tr.find_elements_by_tag_name('td')
        del (tds[0])

        if i == 0:
            if re.search("Enfermaria", str(tr.text).strip()):
                id_modalidade = 1
            elif re.search("Apartamento", str(tr.text).strip()):
                id_modalidade = 2
            # else:
            #     id_modalidade = 2
            print(f"Modalidade--: {id_modalidade}")
        if i == 1:
            for td in tds:
                aux = [td.text]
                dados.append(aux)

        if 1 < i < 12:
            for j, td in enumerate(tds):
                dados[j].append(td.text)
    print([dados, id_modalidade])
    return [dados, id_modalidade]


def dadosPlano(driver, title):
    global idArea
    print("Pagina com os Preços")

    idCoparticipacao = 0
    idArea = 0

    if re.search('COM REMISSÃO', title):
        driver.execute_script("history.back()")
        return

    # Tipo empresa
    if re.search('- MEI ', title):
        id_tipo_empresa = 1
    else:
        id_tipo_empresa = 2

    # Achar operadora
    if re.search('SULAMÉRICA', title):
        idOperadora = 4
    elif re.search('QSAÚDE', title):
        idOperadora = 16
        id_tipo_empresa = None
        idCoparticipacao = 1
    elif re.search('CENTRAL NACIONAL UNIMED ', title):
        idOperadora = 6

    # Tipo de contratacao
    if re.search('FLEX', title):
        idTipoContratacao = 1
    else:
        idTipoContratacao = 2

    if idArea == 0:
        # Area
        if re.search('Tarifa 1', title):
            idArea = 1
        elif re.search('Tarifa 2', title):
            idArea = 2
        elif re.search('Tarifa 3', title):
            idArea = 3
        elif re.search('CAMPINAS', title) and idOperadora == 4:
            idArea = 20
        else:
            idArea = 1

    textBoxSubtitle = driver.find_element_by_xpath('//*[@id="geral-content"]/section/div[2]/div[1]/div[1]/div[4]').text

    hospitalar = 1

    if re.search('COM COPART', title):
        if re.search('30%', title):
            idCoparticipacao = 5
        elif re.search('20%', title):
            idCoparticipacao = 3
        else:
            idCoparticipacao = 1
    elif re.search('SEM COPART', title):
        idCoparticipacao = 2
    elif re.search('HOSPITALAR', title):
        idCoparticipacao = 2
        hospitalar = 2
    elif not re.search('QSAÚDE', title):
        idCoparticipacao = 2

    elemestsClassTaC = driver.find_elements_by_class_name('ta-c')

    # print(len(elemestsClassTaC))

    refPrecos = False
    countPrecosTabela = 0
    planos_atualizados = []
    inseridos = 0

    minVidas = 0
    maxVidas = 0
    teste = 0
    testeQsaude = 0

    for i, ele in enumerate(elemestsClassTaC):
        # print(ele.get_attribute("class"))
        # exit()

        if refPrecos:
            print(f"CONFIGURACOES: \nidOperadora: {idOperadora} "
                  f"\nidTipoContratacao: {idTipoContratacao} \nidCoparticipacao: {idCoparticipacao} \n"
                  f"minVidas: {minVidas} \nmaxVidas: {maxVidas} \nidTipoEmpresa: {id_tipo_empresa}")

            if idOperadora == 4:
                refPrecos = False
            elif idOperadora == 16:
                if testeQsaude == 1:
                    refPrecos = False
                testeQsaude += 1
            elif idOperadora == 6:
                refPrecos = False

            countPrecosTabela += 1
            # print(driver.find_elements_by_class_name('fz-8')[countPrecosTabela].text)
            ultimaAlteracao = driver.find_elements_by_class_name('fz-8')[countPrecosTabela].text.split(": ")[1].split(
                "/")
            ultimaAlteracao = f"{ultimaAlteracao[2]}-{ultimaAlteracao[1]}-{ultimaAlteracao[0]}"
            ultimaAlteracao = datetime.strptime(str(ultimaAlteracao), '%Y-%m-%d').date()

            dados = obterPrecos(ele)
            id_modalidade = dados[1]

            for dado in dados[0]:
                dado[0] = str(dado[0]).replace("(R1)", "R1")
                dado[0] = str(dado[0]).replace("(R2)", "R2")
                dado[0] = str(dado[0]).replace("(R3)", "R3")

                plano = dado[0]

                plano = plano.replace(" ", "")
                plano = plano.replace("-", "")

                if idOperadora == 6:
                    plano = f"{plano}NACIONAL"

                sql = f"select * from tbl_tipo_plano where id_operadora = {idOperadora} and replace(titulo, ' ', '') like '{plano.upper()}';"
                # print(sql)
                res = cursor.execute(sql)
                valores = []

                if res > 0:
                    result_select = cursor.fetchall()[0]
                    id_plano = result_select[0]
                    id_categoria_plano = result_select[3]
                    if id_plano > 0:
                        for u, valor in enumerate(dado):
                            if u > 0 and not valor == "-":
                                valores.append(float(str(valor).split(" ")[1].replace(".", "").replace(",", ".")))
                            elif u > 0 and valor == "-":
                                valores.append(0)

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

                        # variaveis
                        id_administradora = 0

                        if idOperadora == 16:
                            id_tipo_empresa = None

                        values = (
                            idArea,  # id_area
                            id_categoria_plano,  # id_categoria_plano
                            idCoparticipacao,  # id_coparticipacao
                            id_modalidade,  # id_modalidade,
                            idOperadora,  # id_operadora
                            idTipoContratacao,  # id_tipo_contratacao
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
                            '1',  # qtd_titulares
                            None,  # id_sindicato
                            hospitalar,  # hospitalar
                            minVidas,  # min_vidas
                            maxVidas,  # max_vidas
                            id_tipo_empresa,  # id_tipo_empresa
                            id_administradora,  # id_administradora
                            ultimaAlteracao,  # ultimo_reajuste
                            0,  # id_tipo_contratacao_lead
                            None  # id_tipo_tabela
                        )

                        if idOperadora == 16:
                            id_tipo_empresa_txt = 'is null'
                        else:
                            id_tipo_empresa_txt = f"= {id_tipo_empresa}"

                        teste = "select * from tbl_preco_faixa_etaria " \
                                f"where id_area = {idArea} and id_operadora = {idOperadora} and id_tipo_plano = {id_plano} and id_modalidade = {id_modalidade} " \
                                f"and id_tipo_contratacao = {idTipoContratacao} and id_coparticipacao = {idCoparticipacao} and qtd_titulares = 1 " \
                                f"and min_vidas = {minVidas} and max_vidas = {maxVidas} and id_sindicato is null and id_tipo_empresa {id_tipo_empresa_txt} and hospitalar = {hospitalar};"
                        print(teste)
                        res = cursor.execute(teste)

                        print(values, " -- extraidos do simulador")
                        # print(res)
                        if res == 1 and valores[0] > 0:
                            select = cursor.fetchall()[0]

                            idSelect = select[0]
                            preco0_18 = select[8]
                            preco59 = select[17]
                            ultimo_reajuste = select[25]

                            print(select[1:28], f"ID: {idSelect} -- banco de dados")

                            # print(ultimaAlteracao)
                            # print(ultimo_reajuste)

                            # Condicao para alterar a data do reajuste caso os precos estejam iguais mais sem data
                            if (ultimo_reajuste is None or not (ultimo_reajuste == ultimaAlteracao)) and preco0_18 == \
                                    valores[0]:
                                print('Atualizar Data')
                                update = f"UPDATE `tbl_preco_faixa_etaria` SET `ultimo_reajuste`='{ultimaAlteracao}', status = '1' WHERE `id`='{idSelect}';"
                                # print(update)
                                if atualizarDataReajuste:
                                    cursor.execute(update)

                            # print(type(preco0_18), type(valores[0]))
                            # print(preco0_18, valores[0])
                            if not preco0_18 == valores[0] or not preco59 == valores[
                                9]:  # and not ultimo_reajuste == data_reajuste
                                print("Atualizar Precos! -----")
                                planos_atualizados.append(plano)

                                if ultimo_reajuste == None or ultimo_reajuste == "":
                                    ultimo_reajuste = "null"
                                    textUltimoReajuste = " "
                                else:
                                    ultimo_reajuste = datetime.strptime(str(ultimo_reajuste), '%Y-%m-%d').date()
                                    textUltimoReajuste = f", `ultimo_reajuste`='{ultimaAlteracao}' "
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
                                         f"`preco_m59`='{valores[9]}'," \
                                         f"`min_vidas`='{minVidas}', " \
                                         f"`max_vidas`='{maxVidas}', " \
                                         f"ultimo_reajuste = '{ultimaAlteracao}', " \
                                         f"status = '1' " \
                                         f"WHERE `id`='{idSelect}';"
                                print(update)

                                if updatePrecoPlano:
                                    res = cursor.execute(update)
                                    mensagem = f"Plano: {plano} \nIdOperadora: {idOperadora}\n SQL:{sql}"
                                    res2 = apiWhats.sendMessageAlert(
                                        message=mensagem,
                                        number=getNumberWhatsNotificationPrice
                                    )
                                    print(res2)
                                else:
                                    res = 1

                                # print(res)
                                if res == 1 and updatePrecoPlano:

                                    if ultimo_reajuste == None or ultimo_reajuste == "null":
                                        insert = "insert into tbl_historico_precos_planos " \
                                                 "(id_preco_faixa_etaria, preco0_18, preco19_23, preco24_28, preco29_33, preco34_38, preco39_43, preco44_48, preco49_53, preco54_58, preco_m59 ) " \
                                                 "values " \
                                                 f"({idSelect}, {select[8]}, {select[9]}, {select[10]}, {select[11]}, {select[12]}, {select[13]}, {select[14]}, {select[15]}, {select[16]}, {select[17]}); "
                                    else:
                                        insert = "insert into tbl_historico_precos_planos " \
                                                 "(id_preco_faixa_etaria, preco0_18, preco19_23, preco24_28, preco29_33, preco34_38, preco39_43, preco44_48, preco49_53, preco54_58, preco_m59, data_validade) " \
                                                 "values " \
                                                 f"({idSelect}, {select[8]}, {select[9]}, {select[10]}, {select[11]}, {select[12]}, {select[13]}, {select[14]}, {select[15]}, {select[16]}, {select[17]}, '{ultimo_reajuste}'); "

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
                        elif res == 0 and valores[0] > 0:
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
                else:
                    print("nothing")

        if re.search('vidas/beneficiários', ele.text):
            textVidas = ele.text

            if re.search('2 à 2 vidas', textVidas):
                minVidas = 0
                maxVidas = 2
            elif re.search('2 à 29 vidas', textVidas):
                minVidas = 2
                maxVidas = 29
            elif re.search('3 à 29 vidas', textVidas):
                minVidas = 3
                maxVidas = 29
            elif re.search('30 à 99 vidas', textVidas):
                minVidas = 30
                if idOperadora == 6:
                    maxVidas = 99
                else:
                    maxVidas = 0
            elif re.search('100 à 199 vidas', textVidas):
                minVidas = 100
                maxVidas = 199
            elif re.search('2 à 29', textVidas):
                minVidas = 0
                maxVidas = 29

            refPrecos = True

        if teste == 1 and idOperadora == 16:
            teste = 0
            refPrecos = True

        if idOperadora == 16 and (re.search('2021', ele.text)):
            teste += 1
            elemQsaude = driver.find_elements_by_class_name('static small ta-c')

            tipoContrato = driver.find_element_by_xpath(
                '//*[@id="geral-content"]/section/div[2]/div[1]/div[1]/div[3]').text
            if tipoContrato == "Individual":
                minVidas = 0
                maxVidas = 1
            elif tipoContrato == "Familiar":
                minVidas = 2
                maxVidas = 0

            # if len(elemQsaude) < 2:
            #     refPrecos = True

            refPrecos = True

            # print(f"CONFIGURACOES: \nidOperadora: {idOperadora} "
            #       f"\nidTipoContratacao: {idTipoContratacao} \nidCoparticipacao: {idCoparticipacao} \n"
            #       f"minVidas: {minVidas} \nmaxVidas: {maxVidas} \nidTipoEmpresa: {id_tipo_empresa}")

    conn.commit()

    driver.execute_script("history.back()")


def navegacao(driver):
    global idArea
    driver.find_element_by_xpath('//*[@id="geral-content"]/nav/ul/li[1]/a').click()

    # driver.find_element_by_id('tabela_tiposTabela_1').click()
    # driver.find_element_by_id('tabela_tiposTabela_2').click()
    driver.find_element_by_id('tabela_tiposTabela_3').click()
    driver.find_element_by_id('tabela_tiposPlano_1').click()

    driver.find_element_by_xpath(f'//*[@id="tabela_regiao"]/option[25]').click()
    idArea = 1

    time.sleep(1)
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.ID, 'btn-get-opes'))
        )
    finally:
        pass

    # driver.find_element_by_id('btn-get-opes').click()
    driver.execute_script('document.getElementById("btn-get-opes").click()')

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'bgGray'))
        )
    finally:
        pass

    qttResults = int(str(driver.find_element_by_class_name('bgGray').text).split("(")[1].split(")")[0])

    voltar = False
    for i in range(0, qttResults - 1):
        # for i in range(235, 242):

        if voltar:
            driver.find_element_by_id('btn-get-opes').click()
            time.sleep(2)
            voltar = False

        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.ID, 'div-opes-loaded'))
            )
        finally:
            pass
        try:
            textBox = driver.find_element_by_xpath(
                f'//*[@id="div-opes-loaded"]/div/label[{i + 1}]').find_element_by_class_name("text").text
        except:
            time.sleep(3)
            textBox = driver.find_element_by_xpath(
                f'//*[@id="div-opes-loaded"]/div/label[{i + 1}]').find_element_by_class_name("text").text
        finally:
            pass
        refOperadora = False

        # textAlteracao = driver.find_element_by_xpath(f'//*[@id="div-opes-loaded"]/div/label[{i + 1}]/div/b[2]').text
        #
        # if re.search('Essa Tabela está sendo atualizada neste momento', textAlteracao):
        #     # enviar pensagem pelo whats com o title do plano de saude
        #     print("Enviar mensagem pelo whats")

        refCheckBoxDesabilited = driver.find_element_by_xpath(
            f'//*[@id="div-opes-loaded"]/div/label[{i + 1}]').get_attribute('class')
        if re.search("beautyCheck fullwidth opcy-7", refCheckBoxDesabilited):
            refCheckBoxDesabilited = True
        else:
            refCheckBoxDesabilited = False
        # print(refCheckBoxDesabilited)

        if re.search('SULAMÉRICA', textBox) and (not re.search('COM REMISSÃO', textBox)
                                                 and not re.search('SEM REMISSÃO',
                                                                   textBox)) and not refCheckBoxDesabilited:
            refOperadora = True

        elif re.search('QSAÚDE', textBox):
            refOperadora = False
        elif re.search('CENTRAL NACIONAL UNIMED', textBox):
            refOperadora = False

        if refOperadora:
            driver.find_element_by_xpath(f'//*[@id="div-opes-loaded"]/div/label[{i + 1}]/input').click()
            # driver.execute_script(f"document.getElementsByName('tabela[tabelas][]')[{i}].click()")
            time.sleep(2)
            driver.execute_script("document.getElementById('btSubmit').click()")

            print(f"\n------------------------------------------------------------------------"
                  f"------------------------------------------\nLendo {i}: {textBox}")
            dadosPlano(driver, textBox)

            voltar = True

    cursor.close()
    conn.commit()
    conn.close()
