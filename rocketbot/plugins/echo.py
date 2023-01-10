"""/echo (.*)

I repeat what you say
"""


def handle(bot, message, *args):
    match_list = args[0]
    bot.send_message(message['rid'], match_list[0])
