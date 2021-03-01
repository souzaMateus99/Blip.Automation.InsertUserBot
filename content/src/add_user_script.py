import os
import time
import re
from services import ConfigService as config_service
from services import SeleniumService as selenium_service
from selenium.webchrome_driver.common.by import By
from selenium.webchrome_driver.common.keys import Keys


def get_base_path():
    script_path = os.path.realpath(__file__)
    file_split = __file__.split('\\')
    
    return script_path.replace(r'\src', '').replace(file_split[-1], '')


def has_access_in_bot(bot_identity, chrome_driver, time_search_element):
    chrome_driver.get('https://portal.blip.ai/application')

    selenium_service.find_element(chrome_driver, (By.ID, 'applications'), time_search_element)
    
    bots_elem = selenium_service.find_elements(chrome_driver, (By.XPATH, '//div[2] //contact-list //contact //div //ng-include //a'), time_search_element)

    print(f"Search bot '{bot_identity}'' in user's bot list")

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
    try:
        blip_login_url = 'https://account.blip.ai/login?ReturnUrl=%2Fconnect%2Fauthorize%2Fcallback%3Fclient_id%3Dblip-portal%26redirect_uri%3Dhttps%253A%252F%252Fportal.blip.ai%252Fauthorize%26response_type%3Did_token%2520token%26scope%3Doffline_access%2520openid%2520profile%2520email%2520api-msging-hub.full_access%26state%3Dfe3e8195269b4e84bb3e5e428fc48ab2%26nonce%3Da9a76f021a4c490fb43189d27a6a8e7b'

        config_filepath = config_path

        config_json = config_service.read_config_file(config_filepath)

        user_mail = config_json['userInfo']['mail']
        user_password = config_json['userInfo']['password']
        users_insert_mail = config_json['usersInsert']
        bots = config_json['bots']
        headless_browser = config_json['headlessBrowser']

        chrome_driver = selenium_service.chrome_driver_factory(headless_browser)

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

                        selenium_service.find_element(chrome_driver, (By.XPATH, '/html/body/div[7]/div[2]/div[2]/form/div[2]/button[2]'), time_search_element).click()
                        
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
    finally:
        chrome_driver.close()
        print('Chromechrome_driver closed')
        chrome_driver.stop_client()
        print('Proccess finish!!')


main('config.json', 120)