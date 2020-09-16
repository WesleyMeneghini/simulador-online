from src.config import webBrowser
from src import acesso, login, simular

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


import time

if __name__ == '__main__':

    driver = webBrowser.browser()
    # driver.minimize_window()
    driver.get(acesso.getSite)

    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="ara_cliente"]/iframe'))
        )
    except:
        print("Nao achou o iframe")
    finally:

        try:
            login.login(driver)
        except:
            driver.get('https://app.simuladoronline.com/inicio')

        simular.simulador(driver)

        time.sleep(4)
        driver.close()
