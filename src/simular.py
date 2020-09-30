from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import time
from src.db import conexao
from src import selecaoPlanos, selecaoAdesao

count = 0
def simulador(driver):

    global count
    count += 1
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="geral-content"]/nav/ul/li[2]/ul/li[1]/a'))
        )
    except:
        print("Nao achou a aba do simulador")
        if count == 3:
            driver.close()
            exit()
        simulador(driver)
    finally:
        # acessar area de simulacao
        driver.execute_script("document.getElementsByTagName('a')[5].click()")

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, 'simulacao__token'))
            )
        except:
            print("Nao abriu a pagina de simulacao")
            driver.close
            exit()
            # simulador(driver)
        finally:

            # SIMULAÇAO

            # TIPO DE PLANO -> saude
            driver.find_element_by_xpath('//*[@id="simulacao_tipoPlano"]/option[2]').click()

            pesquisa = False
            if pesquisa:

                # Selecionar o tipo de tabela
                print("Seleciona o tipo de tabela!")
                while driver.find_element_by_xpath('//*[@id="simulacao_tipoTabela"]/option[1]').is_selected():
                    time.sleep(0.5)

                for i, item in enumerate(
                        driver.find_element_by_id('simulacao_tipoTabela').find_elements_by_tag_name('option')):
                    # print(i, item.get_attribute("selected"))
                    if item.get_attribute("selected"):
                        tipo_tabela_option = i + 1

                if tipo_tabela_option == 5:  # ADESAO

                    # Selecionando a Administradora
                    print("Seleciona a administradora!")
                    while driver.find_element_by_xpath(
                            '//*[@id="simulacao_adesao_administradora"]/option[1]').is_selected():
                        time.sleep(0.5)

                    for i, item in enumerate(
                            driver.find_element_by_id('simulacao_adesao_administradora').find_elements_by_tag_name(
                                'option')):
                        if item.get_attribute("selected"):
                            nome_administradora = item.text
                            administradora_option = i + 1

                    sql = f"select * from tbl_administradora where titulo like '%{nome_administradora}%';"
                    conn = conexao.myConexao()
                    cursor = conn.cursor()
                    res = cursor.execute(sql)
                    if res > 0:
                        # print(cursor.fetchall()[0][0])
                        id_administradora = cursor.fetchall()[0][0]
                        print(id_administradora)

                    # Selecionando a Operadora
                    print("Seleciona a Operadora!")
                    while driver.find_element_by_xpath('//*[@id="simulacao_adesao_opes"]/option[1]').is_selected():
                        time.sleep(0.5)

                    for i, item in enumerate(
                            driver.find_element_by_id('simulacao_adesao_opes').find_elements_by_tag_name('option')):
                        if item.get_attribute("selected"):
                            operadora_option = i + 1

                    # Selecionando a Entidade
                    print("Seleciona a Entidade!")

                    while driver.find_element_by_xpath('//*[@id="simulacao_adesao_entidade"]/option[1]').is_selected():
                        time.sleep(0.5)

                    driver.implicitly_wait(15)
                    for i, item in enumerate(
                            driver.find_element_by_id('simulacao_adesao_entidade').find_elements_by_tag_name('option')):
                        if item.get_attribute("selected"):
                            entidade_option = i + 1

                    print(tipo_tabela_option, administradora_option, operadora_option, entidade_option)
                    selecaoAdesao.obterDados(driver, tipo_tabela_option, administradora_option, operadora_option, entidade_option)

                elif tipo_tabela_option == 4:
                    selecaoPlanos.obterDados(driver, tipo_tabela_option)

            else:

                tipo_tabela_option = 4

            # selecaoPlanos.obterDados(driver, tipo_tabela_option)


            # TESTES PARA ADESAO
            tipo_tabela_option = 5
            administradora_option = 16
            operadora_option = 2
            entidade_option = 1

            selecaoAdesao.obterDados(driver, tipo_tabela_option, administradora_option, operadora_option, entidade_option)



