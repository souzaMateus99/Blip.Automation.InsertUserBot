import time
from services.BlipCrawlerService import BlipCrawlerService
from services.JsonFileService import JsonFileService

PARTIAL_CONFIG_FILEPATH = 'configuration/config.json'

config_json = JsonFileService(PARTIAL_CONFIG_FILEPATH).do_read_config_file()

user_login_info = config_json['userInfo']
users_insert_mail = config_json['usersInsert']
bots = config_json['bots']

blip_crawler = BlipCrawlerService(user_login_info, users_insert_mail, bots)

try:
    blip_crawler.do_portal_login()

    if blip_crawler.is_logged():
        for bot in blip_crawler.bots:
            if blip_crawler.has_access_in_bot(bot):
                blip_crawler.do_register_team_member(bot)

                if bot != bots[-1]:
                    time.sleep(10)
            else:
                print(f"User haven't access to bot: {bot}")
    else:
        print('User email or password is wrong')
        print('Please verify in "config.json" file!!')
except Exception as e:
    e.with_traceback()