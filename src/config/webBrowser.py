from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

def browser():
    chromedriver = r"./src/config/chromedriver"
    # chromedriver = f'{os.getcwd()}/src/config/chromedriver'
    # print(chromedriver)
    # options = webdriver.ChromeOptions()
    options = webdriver.ChromeOptions()
    options.headless = True
    # return webdriver.Chrome(executable_path=chromedriver, options=options)
    # return webdriver.Firefox(options=options)
    return webdriver.Chrome(ChromeDriverManager().install(), options=options)
