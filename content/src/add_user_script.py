import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


blip_login_url = 'https://account.blip.ai/login?ReturnUrl=%2Fconnect%2Fauthorize%2Fcallback%3Fclient_id%3Dblip-portal%26redirect_uri%3Dhttps%253A%252F%252Fportal.blip.ai%252Fauthorize%26response_type%3Did_token%2520token%26scope%3Doffline_access%2520openid%2520profile%2520email%2520api-msging-hub.full_access%26state%3Dfe3e8195269b4e84bb3e5e428fc48ab2%26nonce%3Da9a76f021a4c490fb43189d27a6a8e7b'

def chrome_driver_factory(driver_path = '', is_headless = False):
    driver_options = Options()
    
    if is_headless:
        driver_options.add_argument("--headless")

    return webdriver.Chrome(executable_path=driver_path, chrome_options=driver_options)


def read_config_file():
    f = open(file=r'.\content\configuration\config.json', mode='r')
    return json.load(f)

def has_access_in_bot(bot_identity, driver):
    driver.get('https://portal.blip.ai/application')

    bot_cards_elem = WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.ID, 'applications'))
    )

    bots_elem = bot_cards_elem.find_elements_by_xpath('//div[2] //contact-list //contact //div //ng-include //a')

    print(f"Search bot {bot} in user's bot list")

    for bot_elem in bots_elem:
        if bot_elem.get_attribute("href").find(bot_identity) >= 0:
            print('Bot find')
            return True

    return False


driver = chrome_driver_factory(r'.\content\driver\chromedriver.exe', True)
config_json = read_config_file()

user_mail = config_json['user_info']['mail']
user_password = config_json['user_info']['password']
users_insert_mail = config_json['users_insert']
bots = config_json['bots']

driver.get(blip_login_url)

WebDriverWait(driver, 120).until(
    EC.visibility_of_element_located((By.NAME, 'Username'))
).send_keys(user_mail)

password_elem = WebDriverWait(driver, 120).until(
    EC.visibility_of_element_located((By.NAME, 'Password'))
)
password_elem.send_keys(user_password)
password_elem.send_keys(Keys.ENTER)

for bot in bots:
    if has_access_in_bot(bot, driver):
        driver.get(f'https://portal.blip.ai/application/detail/{bot}/team')

        for user_insert in users_insert_mail:            
            WebDriverWait(driver, 120).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="main-content-area"] //div //page-header //div[1] //div[1] //div[1] //div[2] //custom-content //button'))
            ).click()

            WebDriverWait(driver, 120).until(
                EC.presence_of_element_located((By.NAME, 'email'))
            ).send_keys(user_insert)

            admin_elem = WebDriverWait(driver, 120).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[7]/div[2]/div[2]/form/div[1]/div[3]/ul/li[4]'))
            )

            ActionChains(driver).move_to_element(admin_elem).click().perform()

            WebDriverWait(driver, 120).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[7]/div[2]/div[2]/form/div[2]/button[2]'))
            ).click()

            inserted_message_elem = WebDriverWait(driver, 120).until(
                EC.visibility_of_element_located((By.XPATH, '/html/body/div[3]/div[2]/ul/li/div/span/span'))
            )

            if inserted_message_elem.text.find('problema') >= 0 or inserted_message_elem.text.find('erro') >= 0:
                print('Ocurred error in insert')
            else:
                print('Inserted user with success')

            print(f'Bot Identity: {bot} | User: {user_insert}')
    else:
        print(f"User haven't access to bot: {bot}")

    print('------------------------------------------------------')