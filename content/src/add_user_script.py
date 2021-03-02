import os
import re
import time
import json
from services import SeleniumService as selenium_service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC


def read_config_file(filepath):
    f = open(file=filepath, mode='r')
    return json.load(f)

def get_base_path():
    script_path = os.path.realpath(__file__)
    
    file_split = __file__.split('/')

    if len(file_split) == 1:
        file_split = __file__.split('\\')

    return script_path.replace(r'/src', '').replace(r'\src', '').replace(file_split[-1], '')


def has_access_in_bot(bot_identity, chrome_driver, time_search_element):
    chrome_driver.get('https://portal.blip.ai/application')

    selenium_service.find_element(chrome_driver, (By.ID, 'applications'), time_search_element)
    
    bots_elem = selenium_service.find_elements(chrome_driver, (By.XPATH, '//div[2] //contact-list //contact //div //ng-include //a'), time_search_element)

    print(f"Search bot '{bot_identity}' in user's bot list")

    for bot_elem in bots_elem:
        if selenium_service.get_element_attribute(bot_elem, "href").find(bot_identity) >= 0:
            print('Bot find')
            return True

    return False


def ocurred_error_insert(element):
    return element.text.find('problema') >= 0 or element.text.find('erro') >= 0


def get_user_profile(user_profile):    
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


def get_profile_elem(profile_elems, user_profile):
    elem_value = get_user_profile(user_profile)
    
    if elem_value == None:
        print('User profile not found')
    elif elem_value != 'Customizado':
        print('User profile found')

        for elem in profile_elems:
            if elem_value == elem.text:
                return elem
    else:
        print("Profile 'Customizado' wasn't implemented yet")
    
    return None


def main(config_path, time_search_element):
    blip_login_url = 'http://portal.blip.ai/'

    config_filepath = get_base_path() + config_path
    config_json = read_config_file(config_filepath)

    user_mail = config_json['userInfo']['mail']
    user_password = config_json['userInfo']['password']
    users_insert_mail = config_json['usersInsert']
    bots = config_json['bots']

    try:
        chrome_driver = selenium_service.driver_factory()

        chrome_driver.get(blip_login_url)

        selenium_service.find_element(chrome_driver, (By.NAME, 'Username'), time_search_element).send_keys(user_mail)
        password_elem = selenium_service.find_element(chrome_driver, (By.NAME, 'Password'), time_search_element)

        password_elem.send_keys(user_password)
        password_elem.send_keys(Keys.ENTER)

        is_success_logged = True if chrome_driver.get_cookie('.AspNetCore.Antiforgery.w5W7x28NAIs') == None else False

        if is_success_logged:
            for bot in bots:
                if has_access_in_bot(bot, chrome_driver, time_search_element):
                    chrome_driver.get(f'https://portal.blip.ai/application/detail/{bot}/team')

                    for user_insert in users_insert_mail:
                        user_insert_mail = user_insert['mail']
                        user_insert_profile = user_insert['profile']
                        
                        print(f'Bot Identity: {bot} | User: {user_insert_mail}')

                        selenium_service.find_element(chrome_driver, (By.XPATH, '//*[@id="main-content-area"] //div //page-header //div[1] //div[1] //div[1] //div[2] //custom-content //button'), time_search_element).click()

                        selenium_service.find_element(chrome_driver, (By.NAME, 'email'), time_search_element).send_keys(user_insert_mail)

                        profile_elems = selenium_service.find_elements(chrome_driver, (By.XPATH, '/html/body/div[7]/div[2]/div[2]/form/div[1]/div[3]/ul/li'), time_search_element)

                        user_profile_elem = get_profile_elem(profile_elems, user_insert_profile)

                        selenium_service.move_to_element(chrome_driver, user_profile_elem).click().perform()

                        save_button_element = selenium_service.find_element(chrome_driver, (By.XPATH, '/html/body/div[7]/div[2]/div[2]/form/div[2]/button[2]'), time_search_element)

                        selenium_service.move_to_element(chrome_driver, save_button_element).click().perform()

                        inserted_message_elem = selenium_service.find_element(chrome_driver, (By.XPATH, '/html/body/div[3]/div[2]/ul/li/div/span/span'), time_search_element)

                        if ocurred_error_insert(inserted_message_elem):
                            print('Ocurred error in insert')
                        else:
                            print('Inserted user with success')

                        print('------------------------------------------------------')

                        if bot != bots[-1]:
                            time.sleep(10)
                else:
                    print(f"User haven't access to bot: {bot}")

                print('------------------------------------------------------')
        else:
            print('User email or password is wrong')
            print('Please verify in "config.json" file!!')
    except Exception as e:
        e.with_traceback()


main('configuration/config.development.json', 120)