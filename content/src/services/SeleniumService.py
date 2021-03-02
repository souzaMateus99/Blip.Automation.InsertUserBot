from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def driver_factory():
    driver_options = webdriver.ChromeOptions()

    driver_options.add_argument('--no-sandbox')
    driver_options.add_argument('--headless')
    driver_options.add_argument('--disable-gpu')
    driver_options.add_argument("--window-size=1920, 1200")

    return webdriver.Chrome(options=driver_options)


def find_element(driver, locator, search_timeout = 30):    
    return WebDriverWait(driver, search_timeout).until(
        EC.presence_of_element_located(locator)
    )

def find_element_with_condition(driver, condition, search_timeout = 30):
    return WebDriverWait(driver, search_timeout).until(
        condition
    )

def find_elements(driver, locator, search_timeout = 30):   
    return WebDriverWait(driver, search_timeout).until(
        EC.presence_of_all_elements_located(locator)
    )

def move_to_element(driver, element):    
    return ActionChains(driver).move_to_element(element)

def get_element_attribute(element, attribute):
    return element.get_attribute(attribute)    