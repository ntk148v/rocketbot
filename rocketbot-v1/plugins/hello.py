"""/hello

Dead simple command, you give me a 'hello', I give you a 'hi' <3
"""


def handle(bot, message, *args):
    bot.send_message(message['rid'], f"hi @{message['u']['username']}")
