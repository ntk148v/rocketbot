import importlib
import pkgutil
import re
import sys
import time
import threading
from typing import Any

from loguru import logger
from rocketchat_API.rocketchat import RocketChat

import rocketbot.plugins


class RocketBot(RocketChat):
    def __init__(self, user: str, password: Any | None = None,
                 logger_config: dict | None = None,
                 auth_token: Any | None = None, user_id: Any | None = None,
                 server_url: str = 'http://127.0.0.1:3000',
                 ssl_verify: bool = True,
                 proxies: Any | None = None,
                 timeout: int = 30, session: Any | None = None,
                 client_certs: Any | None = None,
                 threading_updates=False):
        """RocketBot is a plugginable RocketChat API wrapper."""
        super().__init__(user, password, auth_token, user_id, server_url,
                         ssl_verify, proxies, timeout, session, client_certs)
        self.bot_name = user
        self.commands = {}
        self.threading = threading_updates
        self.last_ts = {}  # Last timestamp

        # load logger
        if not logger_config:
            logger_config = {
                "handlers": [
                    {"sink": sys.stderr, "level": "INFO"}
                ],
            }
        logger.configure(**logger_config)

        # Load built-in plugins
        self._load_plugins()

    def get_commands(self):
        """Return a list of supported commands"""
        return self.commands

    def add_command(self, regex: str, usage: str | None = None):
        """Add command with matching regex

        :params regex: If message matches regex, bot does the defined action
        :params usage: Bot usage

        Use it as decorator. For example:

        # Init a bot
        rocketbot = rocketbot(...)
        @rocketbot.command(r'/echo (.*)')
        def echo(bot, message, match_list):
            bot.send_message(message['rid'], match_list[0])
        """

        def decorator(handler):
            self.commands[regex] = {
                'usage': usage or 'Unknown usage',
                'built-in': False,
                'handler': handler
            }
            logger.debug(f'Loaded command {regex}')

        return decorator

    def send_message(self, chat_id, text):
        """Send message"""
        return self.chat_post_message(text, chat_id)

    def subscribe(self):
        """Get all subscriptions"""
        return self.subscriptions_get().json().get('update', list())

    def get_status(self):
        """Get user's status"""
        return self.users_get_presence(username=self.bot_name)

    def set_status(self, message: str | None = None, status: str | None = None):
        """Set user's status message

        :params message: The user's status message.
        :params status: The user's status like online, away, busy, offline.
        """
        if not message:
            message = "Hi, I'm bot. I can do some shitty thing"
        if not status:
            status = "online"
        return self.users_set_status(message=message,
                                     status=status)

    def run(self, sleep: int = 1):
        """Run bot

        :params sleep: Time in second to wait between loop.
                       This argument is used if you hit rate limit issue.
        """
        while True:
            updates = self.subscribe()
            room = None

            for result in updates:
                room_id = result['rid']
                room_unread = result['unread']
                if not room_unread:
                    logger.debug(f'The room with id {room_id}'
                                 ' has been read, skip...')
                    continue

                room = self._get_room(room_id, result['t'])
                if not room:
                    logger.info("Something went wrong, unable to get room")
                    continue

                # Handle messages
                messages = room.get('messages')
                if not messages and not room.get('success'):
                    logger.error(f"Something went wrong, receive"
                                 f" error: {room.get('error')}")
                    continue

                # Set last timestamp
                if len(messages) > 0:
                    self.last_ts[room_id] = messages[0]['ts']

                # Get only unread messages
                messages = messages[:room_unread]
                # Start processing the oldest message
                messages.reverse()

                self._handle_messages(messages)

            # Wait for a bit to work around with RocketChat ratelimit
            time.sleep(sleep)

    def _load_plugins(self):
        """Dynamically load plugins"""
        for _, name, _ in pkgutil.iter_modules(rocketbot.plugins.__path__):
            try:
                module = importlib.import_module('rocketbot.plugins.' + name)
                module_name = module.__name__.split('.')[-1]
                command = f'/{module_name}'
                usage = 'Unknown usage'
                if module.__doc__:
                    command = module.__doc__.split('\n')[0]
                    usage = ''.join(module.__doc__.split('\n')[1:])

                # Construct a plugin
                self.commands[command] = {
                    'usage': usage,
                    'built-in': True,
                    'handler': getattr(module, 'handle')
                }
                logger.debug(f'Loaded command {command}')
            except Exception as e:
                logger.warning(f'Import failed on module {name} due to: {e}')

    def _get_room(self, room_id: str, room_type: str):
        """Get room information with a given room id

        :params room_id: Room's id
        :params room_type: Room's type. The valid value:
                           'd': direct
                           'p': private group
                           'c': public channel
        """
        logger.info(f'Process room with id {room_id}')
        room = None
        if room_type == 'd':  # Direct
            room = self.im_history(room_id,
                                   oldest=self.last_ts.get(room_id)).json()
        elif room_type == 'c':  # Public Channel
            room = self.channels_history(room_id,
                                         oldest=self.last_ts.get(room_id)).json()
        elif room_type == 'p':  # Private Group
            room = self.groups_history(room_id,
                                       oldest=self.last_ts.get(room_id)).json()
        return room

    def _handle_messages(self, messages: dict):
        """Handle messages get from each room

        :params messages: Messages get from room history APIs.
        """
        for message in messages:
            if message['u']['username'] == self.bot_name or \
                    message['u']['username'] == 'rocket.cat':
                continue

            @logger.catch
            def response_update():
                for k, v in self.commands.items():
                    msg = message['msg']
                    if msg.startswith('@' + self.bot_name):
                        msg = msg.lstrip('@' + self.bot_name).strip()

                    regex = re.compile(
                        k, flags=re.MULTILINE | re.DOTALL)
                    m = regex.match(msg)

                    if m:
                        if v.get('built-in'):
                            args = [self, message]
                        else:
                            args = [message]

                        match_list = []
                        for x in m.groups():
                            match_list.append(x)
                        args.append(match_list)

                        v['handler'](*args)

            if self.threading:
                # Set daemon is True, sub-thread will die if the main one exits
                threading.Thread(
                    target=response_update, daemon=True).start()
            else:
                response_update()
