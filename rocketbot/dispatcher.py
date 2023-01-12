from rocketbot.bot import Bot
from rocketbot.utils import ContextInstanceMixin


class Dispatcher(ContextInstanceMixin):
    """Simple Updates dispatcher"""
    def __init__(self, bot):
        if not isinstance(bot, Bot):
            raise TypeError(
                f"Argument 'bot' must be an instance of Bot, not '{type(bot).__name__}'")

        self.bot: Bot = bot
        self._polling = False
