from src.config import webBrowser
from src import acesso, login, simular, tabela
from src.portoSeguroPrecos import obterPrecos
import src.omintPrecos as omintPrecos
import src.sompoPrecos as sompoPrecos

if __name__ == '__main__':

    driver = webBrowser.browser()
    driver.maximize_window()

    simuladorOnline = True
    affinityPortoSeguro = True
    affinityOmint = True
    affinitySompo = True

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
