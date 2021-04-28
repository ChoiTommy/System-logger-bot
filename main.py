'''
 References
 https://github.com/python-telegram-bot/python-telegram-bot/tree/master/examples
 https://python-telegram-bot.readthedocs.io/en/stable/index.html
 https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#heroku
 https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/inlinekeyboard.py
'''
# TODO drafting function, multiple photo attachments, text formatting

import logging, os

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters, CallbackContext, CallbackQueryHandler
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
MY_ID = os.getenv('MY_ID')
PORT = os.getenv('PORT')

keyboard = [[InlineKeyboardButton("✔", callback_data='1'), InlineKeyboardButton("❌", callback_data='0')]]
approved_keyboard = [[InlineKeyboardButton("✅Approved and posted", callback_data='-1')]]
rejected_keyboard = [[InlineKeyboardButton("❌Rejected", callback_data='-1')]]
about_keyboard = [[InlineKeyboardButton("Github", url='https://github.com/ChoiTommy/System-logger-bot')]]

def authentication(update: Update) -> bool:
    return update.effective_user.username == MY_USERNAME

def ask_for_text(update: Update, context: CallbackContext) -> int:
    if authentication(update):
        update.message.reply_text(f'👋Welcome back, {update.effective_user.first_name}.\nFeel free to type /cancel at any time to stop the process.')
        update.message.reply_text(
            '🗒What would you like to post? Type in and send text to me. To create a post without text, click the button below.',
            reply_markup = ReplyKeyboardMarkup([['Post without text']], resize_keyboard = True)
        )
        return 0
    else:
        update.message.reply_text('⛔️You are not allowed to use this command.')
        return ConversationHandler.END

# for post submission
def ask_for_text_submission(update: Update, context: CallbackContext) -> int:
    if authentication(update):
        update.message.reply_text(f'ℹIt\'s your channel, {update.effective_user.first_name}. Use /new instead.')
        return ConversationHandler.END
    else:
        update.message.reply_text(f'👋Hello, {update.effective_user.first_name}. You are now going to submit a post.\nFeel free to type /cancel at any time to stop the process.')
        update.message.reply_text(
            '🗒What would you like to post? Type in and send text to me. To create a post without text, click the button below.',
            reply_markup = ReplyKeyboardMarkup([['Post without text']], resize_keyboard = True)
        )
        return 0

def ask_for_photo_without_text(update: Update, context: CallbackContext) -> int:
    context.user_data['TEXT'] = ''
    update.message.reply_text(
        '📸Now send me an image that you wanna post. Currently only the first image will be captured.',
        reply_markup = ReplyKeyboardRemove()
    )
    return 2

def ask_for_photo_with_text(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    context.user_data['TEXT'] = text
    update.message.reply_text(
        '📸Now send me an image if you wish to. Otherwise click the button below to skip this step. (Currently only the first image will be captured.)',
        reply_markup = ReplyKeyboardMarkup([['Post without image']], resize_keyboard = True)
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

def submission_confirmation(update: Update, context: CallbackContext) -> int:
    photo = update.message.photo
    context.user_data['WITH_PHOTO'] = False if not photo else True
    context.user_data['PHOTO'] = photo[0] if photo else None
    context.user_data['TEXT'] = f"{context.user_data['TEXT']}\n - {update.effective_user.first_name} {'' if update.effective_user.last_name == None else update.effective_user.last_name }"

    if context.user_data['WITH_PHOTO']:
        update.message.reply_photo(context.user_data['PHOTO'], caption=context.user_data['TEXT'])
    else:
        update.message.reply_text(context.user_data['TEXT'])

    update.message.reply_text(
        '❓The above message is going to be sent to the channel owner for approval. Are you sure you want to do so?',
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

def send_to_owner(update: Update, context: CallbackContext) -> int:
    choice = update.message.text
    if choice == 'Yes':
        if context.user_data['WITH_PHOTO']:
            context.bot.send_photo(MY_ID, context.user_data['PHOTO'], caption=context.user_data['TEXT'], reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            context.bot.send_message(MY_ID, context.user_data['TEXT'], reply_markup=InlineKeyboardMarkup(keyboard))
        update.message.reply_text('✅Sent successfully. If your post is approved, it will appear in the channel. Stay tuned!', reply_markup=ReplyKeyboardRemove(), disable_notification=True)
    else:
        update.message.reply_text('🗑Message discarded. Type /submit to start again.', reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('ℹ️The process is cancelled. Send the command again to restart the program.', reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def approval(update: Update, _: CallbackContext) -> None:
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    if query.data == '1':
        query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(approved_keyboard))
        query.copy_message(MY_CHANNEL_ID)
    elif query.data == '0':
        query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(rejected_keyboard))

def about(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        '@system\_logger\_bot *Beta*\n\nDedicated for _System Logs_',
        parse_mode = ParseMode.MARKDOWN_V2,
        reply_markup = InlineKeyboardMarkup(about_keyboard)
    )

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # add new post handler
    new_post_handler = ConversationHandler(
        entry_points = [CommandHandler('new', ask_for_text)],
        states = { # dict
            0: [MessageHandler(Filters.regex('^Post without text$'), ask_for_photo_without_text), MessageHandler(Filters.text & ~Filters.command, ask_for_photo_with_text)],
            1: [MessageHandler(Filters.photo | Filters.regex('^Post without image$'), confirmation)],
            2: [MessageHandler(Filters.photo, confirmation)],
            3: [MessageHandler(Filters.regex('^Yes$') | Filters.regex('^No$'), send)]
        },
        fallbacks = [CommandHandler('cancel', cancel)],
        conversation_timeout = 300 # 5 mins
    )
    dispatcher.add_handler(new_post_handler)

    # add submit post handler
    submit_post_handler = ConversationHandler(
        entry_points = [CommandHandler('submit', ask_for_text_submission)],
        states = {
            0: [MessageHandler(Filters.regex('^Post without text$'), ask_for_photo_without_text), MessageHandler(Filters.text & ~Filters.command, ask_for_photo_with_text)],
            1: [MessageHandler(Filters.photo | Filters.regex('^Post without image$'), submission_confirmation)],
            2: [MessageHandler(Filters.photo, submission_confirmation)],
            3: [MessageHandler(Filters.regex('^Yes$') | Filters.regex('^No$'), send_to_owner)]
        },
        fallbacks = [CommandHandler('cancel', cancel)],
        conversation_timeout = 300 # 5 mins
    )

    dispatcher.add_handler(submit_post_handler)
    dispatcher.add_handler(CallbackQueryHandler(approval))

    # add handler for /about
    dispatcher.add_handler(CommandHandler('about', about))

    # start listening to webhook
    updater.start_webhook(listen = "0.0.0.0",
                      port = PORT,
                      url_path = BOT_TOKEN,
                      webhook_url = "https://system-logger-bot.herokuapp.com/" + BOT_TOKEN)
    updater.idle()

    '''# Start the Bot using polling
    updater.start_polling()
    updater.idle()'''

if __name__ == '__main__':
    main()