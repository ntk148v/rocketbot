<div align="center">
  <h1>rocketbot</h1>
  <blockquote align="center">
    Python framework to build RocketChat bot
  </blockquote>
  <p>
    <a href="https://github.com/ntk148v/rocketbot/blob/master/LICENSE">
      <img
        alt="GitHub license"
        src="https://img.shields.io/github/license/ntk148v/rocketbot?style=for-the-badge"
      />
    </a>
    <a href="https://github.com/ntk148v/rocketbot/stargazers">
      <img
        alt="GitHub stars"
        src="https://img.shields.io/github/stars/ntk148v/rocketbot?style=for-the-badge"
      />
    </a>
    <br />
  </p>
  <br />
</div>

Table of contents

- [1. Installation](#1-installation)
- [2. Usage](#2-usage)
  - [2.1. Create new bot](#21-create-new-bot)
  - [2.2. Create a new plugin (command)](#22-create-a-new-plugin-command)
  - [2.3. Custom logger configuration](#23-custom-logger-configuration)
  - [2.4. Run it](#24-run-it)
- [3. Credits](#3-credits)

## 1. Installation

```shell
pip install git+https://github.com/ntk148v/rocketbot.git
```

## 2. Usage

Check out the [sample](./sample.py).

### 2.1. Create new bot

```python
import os

from rocketbot import RocketBot

username = os.environ.get('ROCKET_USERNAME')
password = os.environ.get('ROCKET_PASSWORD')
server_url = os.environ.get('ROCKET_SERVER_URL')

rocket = RocketBot(user=username, password=password,
                   server_url=server_url, ssl_verify=False,
                   session=requests.sessions.Session(),
                   threading_updates=True)


```

### 2.2. Create a new plugin (command)

You can add a new plugin to initialized bot by using decorator `add_command`. `add_command` requires 2 arguments:

- The regex that bot will respond if matching.
- The bot's usage.

```python
@rocket.add_command(r'/start', usage='Start working with bot')
def start(message, *args):
    rocket.send_message(
        message['rid'], f"hi @{message['u']['username']}, let's start")
```

### 2.3. Custom logger configuration

By default, RocketBot writes log to stderr with default level is "INFO". You can customize it by passing a configuration dict. You can refer to [loguru's offical document](https://loguru.readthedocs.io/en/stable/api/logger.html#loguru._logger.Logger.configure).

```python
rocket = RocketBot(user=username, password=password,
                   server_url=server_url, ssl_verify=False,
                   session=requests.sessions.Session(),
                   logger_config={
                       "handlers": [
                           {"sink": sys.stdout, "format": "{time} - {message}"},
                           {"sink": "/tmp/file.log", "serialize": True},
                       ],
                   },
                   threading_updates=True)
```

### 2.4. Run it

```python
rocket.run(sleep=10)
```

## 3. Credits

This library is highly inspired by:

- [seyed-dev/rocketchatbot](https://github.com/seyed-dev/rocketchatbot)
- [jadolg/RocketChatBot](https://github.com/jadolg/RocketChatBot)
