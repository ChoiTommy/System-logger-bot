'''
 References
 https://github.com/python-telegram-bot/python-telegram-bot/tree/master/examples
 https://python-telegram-bot.readthedocs.io/en/stable/index.html
 https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#heroku
'''
# TODO drafting function, multiple photo attachments, text formatting

import logging, os

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters, CallbackContext
# from dotenv import load_dotenv

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
MY_USERNAME = os.getenv('MY_TG_HANDLE')
MY_CHANNEL_ID = os.getenv('MY_CHANNEL_ID')
PORT = os.getenv('PORT')

def authentication(update: Update) -> bool:
    return update.effective_user.username == MY_USERNAME

def ask_for_text(update: Update, context: CallbackContext) -> int:
    if authentication(update) == False:
        update.message.reply_text('⛔️You are not allowed to use this command.')
        return ConversationHandler.END
    else:
        update.message.reply_text(f'Welcome back, {update.effective_user.first_name}.\nFeel free to type /cancel at any time to stop the process.')
        update.message.reply_text(
            '🗒What would you like to post? Type in and send your text to me. To create a post without text, click the button below.',
            reply_markup = ReplyKeyboardMarkup([['Post without text']], resize_keyboard = True)
        )
    return 0

def ask_for_photo_without_text(update: Update, context: CallbackContext) -> int:
    context.user_data['TEXT'] = ''
    update.message.reply_text(
        '📸Now send me a photo that you wanna post.',
        reply_markup = ReplyKeyboardRemove()
    )
    return 2

def ask_for_photo_with_text(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    context.user_data['TEXT'] = text
    update.message.reply_text(
        '📸Now send me a photo if you wish to. Otherwise click the button below to skip this step.',
        reply_markup = ReplyKeyboardMarkup([['Post without images']], resize_keyboard = True)
    )
    return 1

def confirmation(update: Update, context: CallbackContext) -> int:
    photo = update.message.photo
    context.user_data['WITH_PHOTO'] = False if not photo else True
    context.user_data['PHOTO'] = photo[0] if photo else None

    if context.user_data['WITH_PHOTO']:
        update.message.reply_photo(context.user_data['PHOTO'], caption=context.user_data['TEXT'])
    else:
        update.message.reply_text(context.user_data['TEXT'])

    update.message.reply_text(
        '❓The above message is going to be posted in the channel. Are you sure you want to do so?',
        reply_markup = ReplyKeyboardMarkup([['Yes', 'No']], resize_keyboard = True)
    )
    return 3

def send(update: Update, context: CallbackContext) -> int:
    choice = update.message.text
    if choice == 'Yes':
        if context.user_data['WITH_PHOTO']:
            context.bot.send_photo(MY_CHANNEL_ID, context.user_data['PHOTO'], caption=context.user_data['TEXT'])
        else:
            context.bot.send_message(MY_CHANNEL_ID, context.user_data['TEXT'])
        update.message.reply_text('✅Sent successfully.', reply_markup=ReplyKeyboardRemove(), disable_notification=True)
    else:
        update.message.reply_text('🗑Message discarded. Type /new to post again.', reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('ℹ️The process is cancelled. Send /new again to restart the program.', reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # add conversation handler
    new_post_handler = ConversationHandler(
        entry_points = [CommandHandler("new", ask_for_text)],
        states = { # dict
            0: [MessageHandler(Filters.regex('^Post without text$'), ask_for_photo_without_text), MessageHandler(Filters.text & ~Filters.command, ask_for_photo_with_text)],
            1: [MessageHandler(Filters.photo | Filters.regex('^Post without images$'), confirmation)],
            2: [MessageHandler(Filters.photo, confirmation)],
            3: [MessageHandler(Filters.regex('^Yes$') | Filters.regex('^No$'), send)]
        },
        fallbacks = [CommandHandler('cancel', cancel)],
        conversation_timeout = 300 # 5 mins
    )

    dispatcher.add_handler(new_post_handler)

    updater.start_webhook(listen = "0.0.0.0",
                      port = PORT,
                      url_path = BOT_TOKEN,
                      webhook_url = "https://system-logger-bot.herokuapp.com/" + BOT_TOKEN)
    updater.idle()

    # Start the Bot
    # updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    # updater.idle()

if __name__ == '__main__':
    main()