import os
import time
from services import ConfigService as config_service
from services import SeleniumService as selenium_service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def get_base_path():
    script_path = os.path.realpath(__file__)
    file_split = __file__.split('\\')
    
    return script_path.replace(r'\src', '').replace(file_split[-1], '')


def has_access_in_bot(bot_identity, driver, time_search_element):
    driver.get('https://portal.blip.ai/application')

    selenium_service.find_element(driver, (By.ID, 'applications'), time_search_element)
    
    bots_elem = selenium_service.find_elements(driver, (By.XPATH, '//div[2] //contact-list //contact //div //ng-include //a'), time_search_element)

    print(f"Search bot '{bot_identity}'' in user's bot list")

    for bot_elem in bots_elem:
        if selenium_service.get_element_attribute(bot_elem, "href").find(bot_identity) >= 0:
            print('Bot find')
            return True

    return False


def ocurred_error_insert(element):
    return element.text.find('problema') >= 0 or element.text.find('erro') >= 0


def main(driver_path, config_path, time_search_element):
    try:
        blip_login_url = 'https://account.blip.ai/login?ReturnUrl=%2Fconnect%2Fauthorize%2Fcallback%3Fclient_id%3Dblip-portal%26redirect_uri%3Dhttps%253A%252F%252Fportal.blip.ai%252Fauthorize%26response_type%3Did_token%2520token%26scope%3Doffline_access%2520openid%2520profile%2520email%2520api-msging-hub.full_access%26state%3Dfe3e8195269b4e84bb3e5e428fc48ab2%26nonce%3Da9a76f021a4c490fb43189d27a6a8e7b'

        base_path = get_base_path()
        driver_filepath = base_path + driver_path
        config_filepath = base_path + config_path

        config_json = config_service.read_config_file(config_filepath)

        user_mail = config_json['userInfo']['mail']
        user_password = config_json['userInfo']['password']
        users_insert_mail = config_json['usersInsert']
        bots = config_json['bots']
        headless_browser = config_json['headlessBrowser']

        driver = selenium_service.driver_factory(driver_filepath, headless_browser)

        driver.get(blip_login_url)

        selenium_service.find_element(driver, (By.NAME, 'Username'), time_search_element).send_keys(user_mail)
        password_elem = selenium_service.find_element(driver, (By.NAME, 'Password'), time_search_element)

        password_elem.send_keys(user_password)
        password_elem.send_keys(Keys.ENTER)

        is_success_logged = True if driver.get_cookie('.AspNetCore.Antiforgery.w5W7x28NAIs') == None else False

        if is_success_logged:
            for bot in bots:
                if has_access_in_bot(bot, driver, time_search_element):

                    driver.get(f'https://portal.blip.ai/application/detail/{bot}/team')

                    for user_insert in users_insert_mail:
                        print(f'Bot Identity: {bot} | User: {user_insert}')
                              
                        selenium_service.find_element(driver, (By.XPATH, '//*[@id="main-content-area"] //div //page-header //div[1] //div[1] //div[1] //div[2] //custom-content //button'), time_search_element).click()
                        
                        selenium_service.find_element(driver, (By.NAME, 'email'), time_search_element).send_keys(user_insert)

                        admin_elem = selenium_service.find_element(driver, (By.XPATH, '/html/body/div[7]/div[2]/div[2]/form/div[1]/div[3]/ul/li[4]'), time_search_element)

                        selenium_service.move_to_element(driver, admin_elem).click().perform()

                        selenium_service.find_element(driver, (By.XPATH, '/html/body/div[7]/div[2]/div[2]/form/div[2]/button[2]'), time_search_element).click()
                        
                        inserted_message_elem = selenium_service.find_element(driver, (By.XPATH, '/html/body/div[3]/div[2]/ul/li/div/span/span'), time_search_element)

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
        driver.close()
        print('Chromedriver closed')
        driver.stop_client()
        print('Proccess finish!!')


main(r'driver\chromedriver.exe', r'configuration\config.json', 120)