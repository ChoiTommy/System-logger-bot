
from telegram import InlineKeyboardButton

'''
 This is a file that saves all constant keyboard layouts used in main.py.

 '1' corresponds to True and '0' corresponds to False.
 '-1' implies no action is performed if clicked.

 Callback data offsets:
 Post submissions: 0
 Forwarded post submissions: 100
 Reactions buttons: 1000
'''

# Inline keyboard for channel owner to accept/reject post submissions
APPROVAL_KEYBOARD = [
    [InlineKeyboardButton("✔", callback_data = '1'), InlineKeyboardButton("❌", callback_data = '0')],
    [InlineKeyboardButton("", callback_data = '-1')], # these two buttons are added for saving message id and chat id for returning final decision from the owner
    [InlineKeyboardButton("", callback_data = '-1')]
]

# Inline keyboard for channel owner to accept/reject forwarded post submissions (no feedback channel implemented)
FORWARD_APPROVAL_KEYBOARD = [[InlineKeyboardButton("✔", callback_data = '101'), InlineKeyboardButton("❌", callback_data = '100')]]

# Inline keyboard for displaying the final decision from the channel owner
# No action will be performed if clicked
APPROVED_KEYBOARD = [[InlineKeyboardButton("✅Approved and posted", callback_data = '-1')]]
REJECTED_KEYBOARD = [[InlineKeyboardButton("❌Rejected", callback_data = '-1')]]

# Inline keyboard showing the GitHub repo of the bot
ABOUT_KEYBOARD = [[InlineKeyboardButton("GitHub", url='https://github.com/ChoiTommy/System-logger-bot')]]

# Inline keyboard for subscribers to give reactions
EMOJI_LIST = ["👍", "😲", "🤨", "🤬"]
REACTIONS_CALLBACK_DATA_LIST = ['1000', '1001', '1002', '1003']
REACTIONS_KEYBOARD = [[
    InlineKeyboardButton(f'{EMOJI_LIST[0]} 0', callback_data = REACTIONS_CALLBACK_DATA_LIST[0]),
    InlineKeyboardButton(f'{EMOJI_LIST[1]} 0', callback_data = REACTIONS_CALLBACK_DATA_LIST[1]),
    InlineKeyboardButton(f'{EMOJI_LIST[2]} 0', callback_data = REACTIONS_CALLBACK_DATA_LIST[2]),
    InlineKeyboardButton(f'{EMOJI_LIST[3]} 0', callback_data = REACTIONS_CALLBACK_DATA_LIST[3]),
    ]]
REACTIONS_KEYBOARD_FOR_DISPLAY = [[
    InlineKeyboardButton(f'{EMOJI_LIST[0]} 0', callback_data = '-1'),
    InlineKeyboardButton(f'{EMOJI_LIST[1]} 0', callback_data = '-1'),
    InlineKeyboardButton(f'{EMOJI_LIST[2]} 0', callback_data = '-1'),
    InlineKeyboardButton(f'{EMOJI_LIST[3]} 0', callback_data = '-1'),
    ]]


# Reply keyboard for no-text submissions
NO_TEXT = [['Post without text']]

# Reply keyboard for no-image submissions
NO_IMAGE = [['Post without image']]

# Reply keyboard for Yes/No selection
YES_NO = [['Yes', 'No']]