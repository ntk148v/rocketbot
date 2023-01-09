"""/echo  (.*)

I repeat what you say
"""
def handle(bot, message, match_list):
    bot.send_message(message['rid'], match_list[0])
