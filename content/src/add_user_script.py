from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains

user_mail = input('Digite seu e-mail')
user_password = input('Digite sua senha')

driver_path = r'.\content\driver\chromedriver.exe'
bot_identity = 'friday'
insert_user_mail = 'mateusmp@take.net'

driver = webdriver.Chrome(executable_path=driver_path)

driver.get('https://account.blip.ai/login?ReturnUrl=%2Fconnect%2Fauthorize%2Fcallback%3Fclient_id%3Dblip-portal%26redirect_uri%3Dhttps%253A%252F%252Fportal.blip.ai%252Fauthorize%26response_type%3Did_token%2520token%26scope%3Doffline_access%2520openid%2520profile%2520email%2520api-msging-hub.full_access%26state%3Dfe3e8195269b4e84bb3e5e428fc48ab2%26nonce%3Da9a76f021a4c490fb43189d27a6a8e7b')

username_elem = driver.find_element_by_name('Username')
username_elem.clear()
username_elem.send_keys(user_mail)

password_elem = driver.find_element_by_name('Password')
password_elem.clear()
password_elem.send_keys(user_password)
password_elem.send_keys(Keys.ENTER)

driver.get('https://portal.blip.ai/application')

bot_cards_elem = WebDriverWait(driver, 120).until(
    EC.presence_of_element_located((By.ID, 'applications'))
)

bots_elem = bot_cards_elem.find_elements_by_xpath('//div[2] //contact-list //contact //div //ng-include //a')

for bot_elem in bots_elem:
    if bot_elem.get_attribute("href").find(bot_identity) >= 0:
        driver.get(f'https://portal.blip.ai/application/detail/{bot_identity}/team')

        WebDriverWait(driver, 120).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="main-content-area"] //div //page-header //div[1] //div[1] //div[1] //div[2] //custom-content //button'))
        ).click()

        WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.NAME, 'email'))
        ).send_keys(insert_user_mail)

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

        if inserted_message_elem.text.find('problema') >= 0:
            print('Ocurred error in insert')
        else:
            print('Inserted user with success')

        print(f'Bot Identity: {bot_identity} | User: {insert_user_mail}')