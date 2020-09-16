from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from src import acesso


count = 0
def login(driver):
    global count
    print("logando...")
    driver.switch_to.frame(driver.find_element_by_xpath('//*[@id="area_cliente"]/iframe'))
    # time.sleep(0.1)
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, 'login_usuario'))
        )
    except:
        count += 1
        if count > 2:
            driver.close()
            exit()
        print("Nao achou a input de Login")
        login(driver)
    finally:
        driver.find_element_by_id('login_usuario').send_keys(acesso.getUser)
        driver.find_element_by_id('login_senha').send_keys(acesso.getPassword)
        driver.find_element_by_id('btSubmit').click()
        driver.switch_to.default_content()