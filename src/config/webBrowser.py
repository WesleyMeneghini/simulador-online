from selenium import webdriver


def browser():
    chromedriver = r"/home/wesley/dev/drivers/chromedriver"
    options = webdriver.ChromeOptions()
    options.headless = False

    return webdriver.Chrome(executable_path=chromedriver, options=options)
