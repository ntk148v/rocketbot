import os
import sys

from dotenv import load_dotenv
import requests
import urllib3

from loguru import logger
from rocketbot import RocketBot

# Disable warning
urllib3.disable_warnings()

load_dotenv()
username = os.environ.get('ROCKET_USERNAME')
password = os.environ.get('ROCKET_PASSWORD')
server_url = os.environ.get('ROCKET_SERVER_URL')

rocket = RocketBot(user=username, password=password,
                   server_url=server_url, ssl_verify=False,
                   session=requests.sessions.Session(),
                   logger_config={
                       "handlers": [
                           {"sink": sys.stdout, "format": "{time} - {message}"},
                           {"sink": "/tmp/rocketbot.log", "serialize": True},
                       ],
                   },
                   threading_updates=True)


@rocket.add_command(r'/start', usage='Start working with bot')
def start(message, *args):
    rocket.send_message(message['rid'],
                        f"hi @{message['u']['username']}, let's start")


logger.info("Bot started")
rocket.run(sleep=20)
