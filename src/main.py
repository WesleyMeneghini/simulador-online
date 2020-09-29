from src.config import webBrowser
from src import acesso, login, simular

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


import time

if __name__ == '__main__':

    driver = webBrowser.browser()
    # driver.minimize_window()
    try:
        driver.get(acesso.getSite)
    except:
        print("SEM INTERNET!")
        exec()
    finally:
        pass

    resLogin = login.login(driver)
    while not resLogin:
        resLogin = login.login(driver)

    simular.simulador(driver)


    driver.close()
