from functions import *

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# 하드 코딩된 위치
options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
service = Service(executable_path="./chromedriver.exe")
driver = webdriver.Chrome(chrome_options=options, service=service)

# Maximize the screen
# driver.maximize_window()

# main_url = [
#     "https://charancha.com/bu/sell/list",
#     "https://www.kbchachacha.com/public/search/main.kbc#!?_menu=buy&page=1&sort=-orderDate",
#     "https://www.bobaedream.co.kr/cyber/CyberCar.php?sel_m_gubun=ALL"
# ]

# driver.find_elements(By.ID, value="yDmH0d")[0].click()
urls = get_images_from_bakcha(driver, 2, 0, './img_crawled/')

start_page = ["https://charancha.com/bu/sell/list",
              "https://www.kbchachacha.com/public/search/main.kbc#!?_menu=buy&page=1&sort=-orderDate",
              "https://www.bobaedream.co.kr/cyber/CyberCar.php?sel_m_gubun=ALL",
              "https://biz.bakcha.com/pages#/product",
              ]
