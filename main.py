from src.config import webBrowser
from src import acesso, login, simular, tabela
from src.portoSeguroPrecos import obterPrecos
import src.omintPrecos as omintPrecos

if __name__ == '__main__':

    driver = webBrowser.browser()

    simuladorOnline = True
    affinityPortoSeguro = False
    affinityOmint = False

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

    driver.close()
