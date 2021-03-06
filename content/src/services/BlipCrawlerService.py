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
    BLIP_LOGIN_URL = 'http://portal.blip.ai/'
    MILLISECONDS_WAIT_ELEMENT_LOAD = 120
    
    def __init__(self, user_login, users_insert, bots):
        self.user_login = user_login
        self.users_insert = users_insert
        self.bots = bots
        self.driver = self.__driver_factory()

    def do_portal_login(self):
        self.driver.get(self.BLIP_LOGIN_URL)

        self.__find_element((By.NAME, 'Username'), self.MILLISECONDS_WAIT_ELEMENT_LOAD).send_keys(self.user_login['mail'])
        password_elem = self.__find_element((By.NAME, 'Password'), self.MILLISECONDS_WAIT_ELEMENT_LOAD)

        password_elem.send_keys(self.user_login['password'])
        password_elem.send_keys(Keys.ENTER)

    def is_logged(self):
        return True if self.driver.get_cookie('.AspNetCore.Antiforgery.w5W7x28NAIs') == None else False

    def has_access_in_bot(self, bot_identity):        
        self.driver.get('https://portal.blip.ai/application')

        self.__find_element((By.ID, 'applications'), self.MILLISECONDS_WAIT_ELEMENT_LOAD)
        
        bots_elem = self.__find_elements((By.XPATH, '//div[2] //contact-list //contact //div //ng-include //a'), self.MILLISECONDS_WAIT_ELEMENT_LOAD)

        print(f"Search bot '{bot_identity}' in user's bot list")

        for bot_elem in bots_elem:
            if bot_elem.get_attribute("href").find(bot_identity) >= 0:
                print('Bot find')
                return True

        return False

    def do_register_team_member(self, bot_identity):
        print("------------------------------------------------------")
        
        self.driver.get(f'https://portal.blip.ai/application/detail/{bot_identity}/team')
        
        for user_insert in self.users_insert:
            user_insert_mail = user_insert['mail']
            user_insert_profile = user_insert['profile']

            print(f'Bot Identity: {bot_identity} | User: {user_insert_mail}')

            self.__find_element((By.XPATH, '//*[@id="main-content-area"] //div //page-header //div[1] //div[1] //div[1] //div[2] //custom-content //button'), self.MILLISECONDS_WAIT_ELEMENT_LOAD).click()

            self.__find_element((By.NAME, 'email'), self.MILLISECONDS_WAIT_ELEMENT_LOAD).send_keys(user_insert_mail)

            profile_elems = self.__find_elements((By.XPATH, '/html/body/div[7]/div[2]/div[2]/form/div[1]/div[3]/ul/li'), self.MILLISECONDS_WAIT_ELEMENT_LOAD)

            profile_name = self.__get_user_profile(user_insert_profile)

            if profile_name != 'Customizado' and profile_name != None:
                print('User profile found')

                user_profile_elem = self.__get_profile_elem(profile_elems, profile_name)

                self.__move_to_element(user_profile_elem).click().perform()

                save_button_element = self.__find_element((By.XPATH, '/html/body/div[7]/div[2]/div[2]/form/div[2]/button[2]'), self.MILLISECONDS_WAIT_ELEMENT_LOAD)

                self.__move_to_element(save_button_element).click().perform()

                inserted_message_elem = self.__find_element((By.XPATH, '/html/body/div[3]/div[2]/ul/li/div/span/span'), self.MILLISECONDS_WAIT_ELEMENT_LOAD)

                if self.__ocurred_error_insert(inserted_message_elem):
                    print('Ocurred error in insert')
                else:
                    print('Inserted user with success')

                print("------------------------------------------------------")
            else:
                if profile_name == 'Customizado':
                    print("Profile 'Customizado' wasn't implemented yet")
                if profile_name == None:
                    print("Profile not found")

    def __driver_factory(self):
        driver_options = webdriver.ChromeOptions()

        driver_options.add_argument('--no-sandbox')
        driver_options.add_argument('--headless')
        driver_options.add_argument('--disable-gpu')
        driver_options.add_argument("--window-size=1920, 1200")

        return webdriver.Chrome(options=driver_options)
    
    def __find_element(self, locator, search_timeout = 30):    
        return WebDriverWait(self.driver, search_timeout).until(
            EC.presence_of_element_located(locator)
        )

    def __find_elements(self, locator, search_timeout = 30):
        return WebDriverWait(self.driver, search_timeout).until(
            EC.presence_of_all_elements_located(locator)
        )

    def __move_to_element(self, element):
        return ActionChains(self.driver).move_to_element(element)

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

    def __ocurred_error_insert(self, element):
        return element.text.find('problema') >= 0 or element.text.find('erro') >= 0