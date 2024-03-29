from src.acesso import getNumberWhatsNotificationLog
from src.config import webBrowser
from src import acesso, login, simular, tabela, sompoProvisorio
from src.portoSeguroPrecos import obterPrecos
import src.omintPrecos as omintPrecos
import src.sompoPrecos as sompoPrecos
from datetime import datetime

from src.services import apiWhats

logs = open("logs.txt", "a+", encoding="utf-8")

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

            mensagem = f"Preços pela Simulaçao Tradicional (Finalizado): {datetime.now().strftime(formatHorario)}"
            apiWhats.sendMessageLog(message=mensagem, number=getNumberWhatsNotificationLog)
        except Exception as e:
            apiWhats.sendMessageLog(message="Erro interno - Simulação Tradicional: Consulte os logs no script", number=getNumberWhatsNotificationLog)

            logs.seek(0)
            data = datetime.now().strftime(formatHorario)

            logs.write(data + " - Simulação Tradicional: ")
            logs.write(str(e))
            logs.write("\n")

            pass
        finally:

            try:
                print("Iniciando os preços pela tabela!")
                tabela.navegacao(driver)
            except Exception as e:
                apiWhats.sendMessageLog(message="Erro interno - Tabela: Consulte os logs no script", number=getNumberWhatsNotificationLog)

                logs.seek(0)
                data = datetime.now().strftime(formatHorario)

                logs.write(data + " - Tabela: ")
                logs.write(str(e))
                logs.write("\n")

                pass
            finally:
                mensagem = f"Preços pela Tabela (Finalizado): {datetime.now().strftime(formatHorario)}"
                apiWhats.sendMessageLog(message=mensagem, number=getNumberWhatsNotificationLog)

                planos = open("planos.txt", "r", encoding="utf-8").read()
                mensagem = f"Planos que não foram encontrados no banco:\n\n{planos}"
                apiWhats.sendMessageLog(message=mensagem, number=getNumberWhatsNotificationLog)

    # Pegar os preços do site da affinity (OPERADORA: Porto Seguro)
    if affinityPortoSeguro:
        obterPrecos(driver)

    if affinityOmint:
        omintPrecos.obterPrecos(driver=driver)
        # driver.find_element_by_xpath(f'//*[@id="tabela_regiao"]/option[13]').is_selected()

    if affinitySompo:
        # sompoPrecos.obterPrecos(driver=driver)
        sompoProvisorio.obterPrecos(driver=driver)

    driver.close()

    mensagem = f"Final do processo - script de preços: {datetime.now().strftime(formatHorario)}"
    apiWhats.sendMessageLog(message=mensagem, number=getNumberWhatsNotificationLog)
