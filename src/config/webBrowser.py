from selenium import webdriver
import os

def browser():
    chromedriver = r"src/config/chromedriver"
    # chromedriver = f'{os.getcwd()}/src/config/chromedriver'
    options = webdriver.ChromeOptions()
    options.headless = True

    return webdriver.Chrome(executable_path=chromedriver, options=options)
