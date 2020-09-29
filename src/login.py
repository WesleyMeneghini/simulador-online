from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from src import acesso


count = 0
def login(driver):
    global count
    print("logando...")
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, 'login_usuario'))
        )
    except:
        print("Nao achou a input de Login")
        return False
    finally:
        driver.find_element_by_id('login_usuario').send_keys(acesso.getUser)
        driver.find_element_by_id('login_senha').send_keys(acesso.getPassword)
        driver.find_element_by_id('btSubmit').click()
        # driver.switch_to.default_content()

        return True