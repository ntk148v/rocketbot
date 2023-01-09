import os

from dotenv import load_dotenv
import requests

from loguru import logger
from rocketbot import RocketBot

# Disable warning
requests.packages.urllib3.disable_warnings()

load_dotenv()
username = os.environ.get('ROCKET_USERNAME')
password = os.environ.get('ROCKET_PASSWORD')
server_url = os.environ.get('ROCKET_SERVER_URL')
gatepro3_username = os.environ.get('GATEPRO3_USERNAME')
gatepro3_password = os.environ.get('GATEPRO3_PASSWORD')

rocket = RocketBot(user=username, password=password,
                   server_url=server_url, ssl_verify=False,
                   session=requests.sessions.Session(),
                   threading_updates=True)


@rocket.add_command(r'/start', usage='Start working with bot')
def start(bot, message):
    bot.send_message(
        message['rid'], f"hi @{message['u']['username']}, let's start")



logger.info("Bot started")
rocket.run(sleep=20)
