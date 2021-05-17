from src.acesso import getNumberWhatsNotificationPrice
from src.config import webBrowser
from src import acesso, login, simular, tabela
from src.portoSeguroPrecos import obterPrecos
import src.omintPrecos as omintPrecos
import src.sompoPrecos as sompoPrecos
from datetime import datetime

from src.services import apiWhats

if __name__ == '__main__':

    try:

        formatHorario = "%d/%m/%Y, %H:%M:%S"

        mensagem = f"Inicio do script de preços: {datetime.now().strftime(formatHorario)}"
        apiWhats.sendMessage(message=mensagem, number=getNumberWhatsNotificationPrice)

        driver = webBrowser.browser()
        driver.maximize_window()

        simuladorOnline = False
        affinityPortoSeguro = False
        affinityOmint = False
        affinitySompo = False

        try:
            if simuladorOnline:
                driver.get(acesso.getSite)
        except:
            print("SEM INTERNET!")
            exec()
        finally:
            pass

        # fazer login no simulador Online
        if simuladorOnline:
            resLogin = login.login(driver)
            while not resLogin:
                resLogin = login.login(driver)

            simular.simulador(driver)

            tabela.navegacao(driver)

        # Pegar os preços do site da affinity (OPERADORA: Porto Seguro)
        if affinityPortoSeguro:
            obterPrecos(driver)

        if affinityOmint:
            omintPrecos.obterPrecos(driver=driver)

        if affinitySompo:
            sompoPrecos.obterPrecos(driver=driver)

        driver.close()

        mensagem = f"Final do processo - script de preços: {datetime.now().strftime(formatHorario)}"
        apiWhats.sendMessage(message=mensagem, number=getNumberWhatsNotificationPrice)

    except Exception as e:
        mensagem = f"Erro no script de preços: {datetime.now().strftime(formatHorario)} \n{e}"
        apiWhats.sendMessage(message=mensagem, number=getNumberWhatsNotificationPrice)


