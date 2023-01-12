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
        self._closed = True

    def start_polling(self, relax=1):
        """Start long-polling

        :param relax: time to wait between loop
        """
        if self._polling:
            raise RuntimeError('Polling already started')

        Dispatcher.set_current(self)
        Bot.set_current(self.bot)

        self._polling = True

    def _process_updates(self, updates):
        """Process updates received from long-polling"""
        pass

    def stop_polling(self):
        """Break long-polling process"""
        if hasattr(self, '_polling') and self._polling:
            self._polling = False

    def is_polling(self):
        """
        Check if polling is enabled
        """
        return self._polling

    def register_message_handler(self, callback , commands=None, regexp=None):
        """Register handler for message"""
        pass

    def message_handler(self, commands=None, regexp=None):
        """Decorator for message handler"""
        def decorator(callback):
            # Execute!
            return callback

        return decorator
