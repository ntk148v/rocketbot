"""/help

Type /help to get a list of supported commands
"""


def handle(bot, message, *args):
    content = ""
    commands = bot.get_commands()
    for k, v in commands.items():
        content += f"""{k}
{v['usage']}

"""
        help = f"""```

{content}```
"""
    bot.send_message(message['rid'], help)
