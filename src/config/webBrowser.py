from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

def browser():
    options = webdriver.ChromeOptions()
    options.headless = False
    return webdriver.Chrome(ChromeDriverManager().install(), options=options)
