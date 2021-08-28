# System Logger Bot
A custom telegram channel bot built for my own channel. It supports post submissions for both channel owner and channel subscribers. Optional reaction buttons can be appended to each channel post for engaging interaction with subscribers. 

[![CodeFactor](https://www.codefactor.io/repository/github/choitommy/system-logger-bot/badge)](https://www.codefactor.io/repository/github/choitommy/system-logger-bot)

Features:

- Post submission for channel owner (with or without reaction buttons)
- Post submission for outsiders (with reaction buttons)
- Post submission with forwarded messages
- Text supports formatting features
- Approval for post submissions from outsiders
- Reactions number counts

## Quick Start

### Setup

It is only compatible with Python versions 3.6+. Make sure a proper version of Python is installed.

Then proceed to install [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) with:

```bash
$ pip install python-telegram-bot
```

Install [python-dotenv](https://github.com/theskumar/python-dotenv) if your credentials are saved in a `.env` file and to be accessed during runtime:

```bash
$ pip install python-dotenv
```

### Run

Key in your own bot token and respective IDs to a `.env` file or the corresponding places in the code. You may need to change a portion of the code to fit your situation. Finally, run the following command: 

```bash
$ python main.py
```
