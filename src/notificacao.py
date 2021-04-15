import re

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from src.db import conexao
from src.services import apiWhats
from src import login
from src import acesso


def notificacao(driver):

    conn = conexao.myConexao()

    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, 'twitter-widget-0'))
        )
    except:
        driver.find_elements_by_class_name("icone exit extend")[0].click()
        login.login(driver)

    finally:
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, 'twitter-widget-0'))
            )
        finally:
            pass
        driver.switch_to.frame(driver.find_element_by_id('twitter-widget-0'))

        timeLine = driver.find_elements_by_class_name("timeline-Tweet-text")

        cursor = conn.cursor()
        sql = "SELECT * FROM tbl_operadora;"
        cursor.execute(sql)
        operadoras = cursor.fetchall()

        for operadora in operadoras:
            nomeOperadora = operadora[1]

            for line in timeLine:
                if re.search(nomeOperadora.upper(), str(line.text).upper()):

                    # Enviar notificaçao pelo whats
                    message = "*Notificaçao do simulador online*\n\n" \
                              f"{line.text}"
                    number = acesso.getNumberWhatsNotificationPrice

                    select = f"select count(id) as qtt from tbl_log_whatsapp_msg " \
                             f"where numero like '%{number}%' and mensagem like '%{message}%';"
                    cursor.execute(select)
                    resSelect = cursor.fetchone()
                    qtt = resSelect[0]

                    if qtt == 0:
                        res = apiWhats.sendMessage(message=message, number=number)

                        if int(res.status_code) == 200:
                            print("Mensagem Enviada com Sucesso!")
                            insert = f"INSERT INTO tbl_log_whatsapp_msg(numero, mensagem, retorno) " \
                                     f"values ('{number}', '{message}', '{res.text}');"
                            cursor.execute(insert)
                            conn.commit()
                        else:
                            print(f"Erro ao enviar a mensagem! STATUS CODE -> {res}")
                    else:
                        print("Mensagem ja consta como enviada no sistema!")

    cursor.close()
    conn.commit()
    conn.close()
