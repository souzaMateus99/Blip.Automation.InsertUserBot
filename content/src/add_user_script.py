import os
from services import ConfigService
from services import SeleniumService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def get_base_path():
    script_path = os.path.realpath(__file__)
    return script_path.replace(__file__[1:], '').replace('src', '')


def has_access_in_bot(bot_identity, driver):
    driver.get('https://portal.blip.ai/application')

    SeleniumService.find_element(driver, (By.ID, 'applications'), time_search_element)
    
    bots_elem = SeleniumService.find_elements(driver, (By.XPATH, '//div[2] //contact-list //contact //div //ng-include //a'), time_search_element)

    print(f"Search bot {bot} in user's bot list")

    for bot_elem in bots_elem:
        if SeleniumService.get_element_attribute(bot_elem, "href").find(bot_identity) >= 0:
            print('Bot find')
            return True

    return False


def ocurred_error_insert(element):
    return inserted_message_elem.text.find('problema') >= 0 or inserted_message_elem.text.find('erro') >= 0


time_search_element = 120
blip_login_url = 'https://account.blip.ai/login?ReturnUrl=%2Fconnect%2Fauthorize%2Fcallback%3Fclient_id%3Dblip-portal%26redirect_uri%3Dhttps%253A%252F%252Fportal.blip.ai%252Fauthorize%26response_type%3Did_token%2520token%26scope%3Doffline_access%2520openid%2520profile%2520email%2520api-msging-hub.full_access%26state%3Dfe3e8195269b4e84bb3e5e428fc48ab2%26nonce%3Da9a76f021a4c490fb43189d27a6a8e7b'

base_path = get_base_path()
driver_filepath = base_path + r'driver\chromedriver.exe'
cofig_filepath = base_path + r'configuration\config.json'

driver = SeleniumService.driver_factory(driver_filepath)
config_json = ConfigService.read_config_file(cofig_filepath)

user_mail = config_json['user_info']['mail']
user_password = config_json['user_info']['password']
users_insert_mail = config_json['users_insert']
bots = config_json['bots']

driver.get(blip_login_url)

SeleniumService.find_element(driver, (By.NAME, 'Username'), time_search_element).send_keys(user_mail)
password_elem = SeleniumService.find_element(driver, (By.NAME, 'Password'), time_search_element)

password_elem.send_keys(user_password)
password_elem.send_keys(Keys.ENTER)

is_success_logged = True if driver.get_cookie('.AspNetCore.Antiforgery.w5W7x28NAIs') == None else False

if is_success_logged:
    for bot in bots:
        if has_access_in_bot(bot, driver):
            driver.get(f'https://portal.blip.ai/application/detail/{bot}/team')

            for user_insert in users_insert_mail:            
                SeleniumService.find_element(driver, (By.XPATH, '//*[@id="main-content-area"] //div //page-header //div[1] //div[1] //div[1] //div[2] //custom-content //button'), time_search_element).click()
                
                SeleniumService.find_element(driver, (By.NAME, 'email'), time_search_element).send_keys(user_insert)

                admin_elem = SeleniumService.find_element(driver, (By.XPATH, '/html/body/div[7]/div[2]/div[2]/form/div[1]/div[3]/ul/li[4]'), time_search_element)

                SeleniumService.move_to_element(driver, admin_elem).click().perform()

                SeleniumService.find_element(driver, (By.XPATH, '/html/body/div[7]/div[2]/div[2]/form/div[2]/button[2]'), time_search_element).click()
                
                inserted_message_elem = SeleniumService.find_element(driver, (By.XPATH, '/html/body/div[3]/div[2]/ul/li/div/span/span'), time_search_element)

                if ocurred_error_insert(inserted_message_elem):
                    print('Ocurred error in insert')
                else:
                    print('Inserted user with success')

                print(f'Bot Identity: {bot} | User: {user_insert}')
        else:
            print(f"User haven't access to bot: {bot}")

        print('------------------------------------------------------')
else:
    print('User email or password is wrong')
    print('Please verify in "config.json" file!!')