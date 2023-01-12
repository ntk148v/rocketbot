import requests
from loguru import logger
from rocketchat_API.rocketchat import RocketChat

from rocketbot.utils import ContextInstanceMixins


class RocketBot(RocketChat, ContextInstanceMixins):
    """Base bot class"""

    def __init__(self, user=None, password=None, auth_token=None, user_id=None,
                 server_url="http://127.0.0.1:3000", ssl_verify=True, proxies=None,
                 timeout=30, session=None, client_certs=None):
        """Creates a RocketChat object and does login on the specified server"""
        # TODO(kiennt26): May be aiohttp's Session?
        if not session:
            session = requests.Session()
        super().__init__(user, password, auth_token, user_id, server_url,
                         ssl_verify, proxies, timeout, session, client_certs)

    @property
    def me(self):
        if not hasattr(self, '_me'):
            setattr(self, '_me', self.me().json())
        return getattr(self, '_me')

    @me.deleter
    def me(self):
        """
        Reset `me`
        """
        if hasattr(self, '_me'):
            delattr(self, '_me')

    def send_message(self, text: str, chat_id: str, color: str = None):
        """Posts a new chat text message

        :param text: text message
        :param chat_id: the room id of where the message is to be sent
        :param color: the color you want the order on the left side to be, any value
                      background-css supports:
                      https://developer.mozilla.org/en-US/docs/Web/CSS/background-color

        Source: https://developer.rocket.chat/reference/api/rest-api/endpoints/core-endpoints/chat-endpoints/postmessage
        """
        return self.chat_post_message(text, room_id=chat_id, color=color).json()

    def send_image(self, image_url: str, chat_id: str, text: str = None, title: str = None):
        """Posts a new image

        :param title: title to display for this attachment, displays under the author.
        :param image_url: the image to display, will be "big" and easy to see
        :param chat_id: the room id of where the message is to be sent
        :param text: the text be sent along the image

        Source: https://developer.rocket.chat/reference/api/rest-api/endpoints/core-endpoints/chat-endpoints/postmessage
        """
        title = title or "I send you an image"
        return self.chat_post_message(text, room_id=chat_id,
                                      attachments=[{
                                          "image_url": image_url,
                                          "title": title
                                      }]).json()

    def send_audio(self, audio_url: str, chat_id: str, text: str = None, title: str = None):
        """Posts a new audio

        :param title: title to display for this attachment, displays under the author.
        :param audio_url: Audio file to play, only supports what html audio does.
        :param chat_id: the room id of where the message is to be sent
        :param text: the text be sent along the audio

        Source: https://developer.rocket.chat/reference/api/rest-api/endpoints/core-endpoints/chat-endpoints/postmessage
        """
        title = title or "I send you an audio"
        return self.chat_post_message(text, room_id=chat_id,
                                      attachments=[{
                                          "audio_url": audio_url,
                                          "title": title
                                      }]).json()

    def send_video(self, video_url: str, chat_id: str, text: str = None):
        """Posts a new video

        :param title: title to display for this attachment, displays under the author.
        :param video_url: Video file to play, only supports what html video does.
        :param chat_id: the room id of where the message is to be sent
        :param text: the text be sent along the video

        Source: https://developer.rocket.chat/reference/api/rest-api/endpoints/core-endpoints/chat-endpoints/postmessage
        """
        title = title or "I send you a video"
        return self.chat_post_message(text, room_id=chat_id,
                                      attachments=[{
                                          "video_url": video_url,
                                          "title": title}]).json()

    def send_richmessage(self, chat_id):
        # TODO(kiennt26): Rich message
        # https://github.com/jadolg/rocketchat_API/wiki/Send-richmessage
        pass

    def subscribe(self):
        """Get all subscriptions, use this method to receive incoming
        updates.

        Source: https://developer.rocket.chat/reference/api/rest-api/endpoints/core-endpoints/subscriptions-endpoints/get-all-subscriptions
        """
        return self.subscriptions_get().json().get('update', list())

    def get_chat_history(self, room_id, room_type='d'):
        """Retrieve the messages from room

        Source:
        - https://developer.rocket.chat/reference/api/rest-api/endpoints/core-endpoints/channels-endpoints/history
        - https://developer.rocket.chat/reference/api/rest-api/endpoints/core-endpoints/im-endpoints/history
        - https://developer.rocket.chat/reference/api/rest-api/endpoints/core-endpoints/groups-endpoints/history
        """
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
