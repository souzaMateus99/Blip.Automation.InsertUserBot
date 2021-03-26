from logging import error
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BlipCrawlerService:
    __BLIP_BASE_URL = 'https://{0}.blip.ai'
    __BLIP_DEFAULT_ORGANIZATION = 'portal'
    __MILLISECONDS_WAIT_ELEMENT_LOAD = 6000
    __ONE_MINUTE_IN_SECONDS_VALUE = 60
    
    def __init__(self, user_login, users_insert):
        self.user_login = user_login
        self.users_insert = users_insert
        self.__driver = self.__driver_factory()

    def do_portal_login(self):
        self.__driver.get(self.__BLIP_BASE_URL.format(self.__BLIP_DEFAULT_ORGANIZATION))

        self.__find_element((By.NAME, 'Username'), self.__MILLISECONDS_WAIT_ELEMENT_LOAD).send_keys(self.user_login['mail'])
        password_elem = self.__find_element((By.NAME, 'Password'), self.__MILLISECONDS_WAIT_ELEMENT_LOAD)

        password_elem.send_keys(self.user_login['password'])
        password_elem.send_keys(Keys.ENTER)

    def is_logged(self):
        return True if self.__driver.get_cookie('.AspNetCore.Antiforgery.w5W7x28NAIs') == None else False

    def has_access_in_bot(self, bot_identity):        
        organization_id = self.__get_organization_id(bot_identity)

        print(f'Search bot "{bot_identity}" in bot list ({organization_id})')
        
        self.__driver.get(f'{self.__BLIP_BASE_URL.format(organization_id)}/application')
        
        bots_elem = self.__find_elements((By.XPATH, '//div[@id="applications"] //contact-list //contact //div[@class="contact animated fadeIn"] //ng-include //a'), self.__MILLISECONDS_WAIT_ELEMENT_LOAD)

        for bot_elem in bots_elem:
            if bot_elem.get_attribute("href").find(bot_identity) >= 0:
                return True

        return False

    def do_register_team_member(self, bot_identity):
        organization_id = self.__get_organization_id(bot_identity)
        
        self.__driver.get(f'{self.__BLIP_BASE_URL.format(organization_id)}/application/detail/{bot_identity}/team')
        
        for user_insert in self.users_insert:
            user_insert_mail = user_insert['mail']
            user_insert_profile = user_insert['profile']

            print("------------------------------------------------------")

            print(f'Bot Identity: {bot_identity} | User: {user_insert_mail}')

            if self.__is_user_registered(user_insert_mail):
                print('User already registered in bot')
            else:
                self.__find_element((By.XPATH, '//div[@class="custom-header-content flex items-center justify-end ml5 tr w-100"] //custom-content //button'), self.__MILLISECONDS_WAIT_ELEMENT_LOAD).click()

                self.__find_element((By.NAME, 'email'), self.__MILLISECONDS_WAIT_ELEMENT_LOAD).send_keys(user_insert_mail)

                profile_elems = self.__find_elements((By.XPATH, '//ul[@class="rz-ticks"] //li'), self.__MILLISECONDS_WAIT_ELEMENT_LOAD)

                profile_name = self.__get_user_profile(user_insert_profile)

                if profile_name != 'Customizado' and profile_name != None:
                    print('User profile found')

                    user_profile_elem = self.__get_profile_elem(profile_elems, profile_name)

                    self.__move_to_element(user_profile_elem).click().perform()

                    save_button_element = self.__find_element((By.XPATH, '//div[@class="modal-footer mt4"] //button[@class="bp-btn bp-btn--bot bp-btn--small"]'), self.__MILLISECONDS_WAIT_ELEMENT_LOAD)

                    self.__move_to_element(save_button_element).click().perform()

                    time.sleep(self.__ONE_MINUTE_IN_SECONDS_VALUE)

                    self.__driver.refresh()
                    
                    time.sleep(self.__ONE_MINUTE_IN_SECONDS_VALUE)

                    if self.__is_user_registered(user_insert_mail):
                        print('user inserted with success')
                    else:
                        print('Ocurred error in insert')
                else:
                    if profile_name == 'Customizado':
                        print("Profile 'Customizado' wasn't implemented yet")
                    if profile_name == None:
                        print("Profile not found")

            print("------------------------------------------------------")

    def __driver_factory(self) -> webdriver.Chrome:
        driver_options = webdriver.ChromeOptions()

        driver_options.add_argument('--no-sandbox')
        driver_options.add_argument('--headless')
        driver_options.add_argument('--disable-gpu')
        driver_options.add_argument("--window-size=1920, 1200")

        return webdriver.Chrome(options=driver_options)
    
    def __find_element(self, locator, search_timeout = 30):    
        return WebDriverWait(self.__driver, search_timeout).until(
            EC.presence_of_element_located(locator)
        )

    def __find_elements(self, locator, search_timeout = 30):
        return WebDriverWait(self.__driver, search_timeout).until(
            EC.presence_of_all_elements_located(locator)
        )

    def __find_elements_with_condition(self, condition, search_timeout = 30):
        return WebDriverWait(self.__driver, search_timeout).until(condition)

    def __move_to_element(self, element):
        return ActionChains(self.__driver).move_to_element(element)

    def __get_profile_elem(self, profile_elems, profile):
        for elem in profile_elems:
            if profile == elem.text:
                return elem
        
        return None

    def __get_user_profile(self, user_profile):    
        profile_dic = {
            "Visualizar": lambda text: (re.match('^visualizar$|^1$', text, re.IGNORECASE) != None),
            "Customizado": lambda text: (re.match('^customizado$|^2$', text, re.IGNORECASE) != None),
            "Visualizar e editar": lambda text: (re.match('^visualizar[\s\w]+editar$|^3$', text, re.IGNORECASE) != None),
            "Admin": lambda text: (re.match('^admin$|^4$', text, re.IGNORECASE) != None)
        }
        
        for key, value in profile_dic.items():
            if value(user_profile):
                return key

        return None

    def __get_organization_id(self, bot) -> str:
        if len(bot.split(':')) > 1:
            return bot.split(':')[0]
            
        return self.__BLIP_DEFAULT_ORGANIZATION

    def __is_user_registered(self, user):
        users_registered_element = self.__find_elements_with_condition(
            EC.visibility_of_all_elements_located((By.XPATH, '//div[@class="container"] //div[@class="row team-cards"] //div //a //card[@class="card--mini-card"] //div //div //div //div //span')),
            self.__MILLISECONDS_WAIT_ELEMENT_LOAD
        )
        
        for user_registered in users_registered_element:
            if user_registered.text == user:
                return True

        return False