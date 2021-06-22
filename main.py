from src.acesso import getNumberWhatsNotificationLog
from src.config import webBrowser
from src import acesso, login, simular, tabela
from src.portoSeguroPrecos import obterPrecos
import src.omintPrecos as omintPrecos
import src.sompoPrecos as sompoPrecos
from datetime import datetime

from src.services import apiWhats

if __name__ == '__main__':

    formatHorario = "%d/%m/%Y, %H:%M:%S"

    mensagem = f"Inicio do script de preços: {datetime.now().strftime(formatHorario)}"
    apiWhats.sendMessageLog(message=mensagem, number=getNumberWhatsNotificationLog)

    driver = webBrowser.browser()
    driver.maximize_window()

    simuladorOnline = True
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

        try:

            simular.simulador(driver)

            mensagem = f"Preços pela Simulçao (Finalizado): {datetime.now().strftime(formatHorario)}"
            apiWhats.sendMessageLog(message=mensagem, number=getNumberWhatsNotificationLog)
        except Exception as e:
            apiWhats.sendMessageLog(message=e, number=getNumberWhatsNotificationLog)
            print(e)
            pass
        finally:

            try:
                tabela.navegacao(driver)
            except Exception as e:
                apiWhats.sendMessageLog(message=e, number=getNumberWhatsNotificationLog)
                print(e)
                pass
            finally:
                mensagem = f"Preços pela Tabela (Finalizado): {datetime.now().strftime(formatHorario)}"
                apiWhats.sendMessageLog(message=mensagem, number=getNumberWhatsNotificationLog)

    # Pegar os preços do site da affinity (OPERADORA: Porto Seguro)
    if affinityPortoSeguro:
        obterPrecos(driver)

    if affinityOmint:
        omintPrecos.obterPrecos(driver=driver)

    if affinitySompo:
        sompoPrecos.obterPrecos(driver=driver)

    driver.close()

    mensagem = f"Final do processo - script de preços: {datetime.now().strftime(formatHorario)}"
    apiWhats.sendMessageLog(message=mensagem, number=getNumberWhatsNotificationLog)
