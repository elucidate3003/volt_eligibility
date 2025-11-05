from selenium import webdriver

def initialize_browser():
    driver = webdriver.Chrome()  
    driver.implicitly_wait(30) 
    driver.maximize_window()
    return driver
