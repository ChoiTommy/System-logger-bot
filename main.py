'''
 References
 https://github.com/python-telegram-bot/python-telegram-bot/tree/master/examples
 https://python-telegram-bot.readthedocs.io/en/stable/index.html
 https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#heroku
 https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/inlinekeyboard.py
'''
# TODO drafting function, multiple photo attachments, divide this program into several files (e.g. constants.py, ...)
# BUG no message previews for submitted posts due to the function copy_message()

import logging, os, Keyboards

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters, CallbackContext, CallbackQueryHandler
from datetime import *
# from dotenv import load_dotenv

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO
)

logger = logging.getLogger(__name__)

# Load credentials from enviroment variables
# load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
MY_USERNAME = os.getenv('MY_TG_HANDLE')
MY_CHANNEL_ID = os.getenv('MY_CHANNEL_ID')
MY_ID = os.getenv('MY_ID')
PORT = os.getenv('PORT')

def authentication(update: Update) -> bool:
    # Check if the sender is the channel owner
    return update.effective_user.username == MY_USERNAME

'''For post submission using the command /new'''
def ask_for_text(update: Update, context: CallbackContext) -> int:
    # Request for text from the channel owner
    if authentication(update):
        update.message.reply_text(f'👋Welcome back, {update.effective_user.first_name}.\nFeel free to type /cancel at any time to stop the process.')
        update.message.reply_text(
            '🗒What would you like to post? Type in and send text to me. To create a post without text, click the button below.',
            reply_markup = ReplyKeyboardMarkup(Keyboards.NO_TEXT, resize_keyboard = True)
        )
        return 0
    else: # Restrict outsiders from accessing this function
        update.message.reply_text('⛔️You are not allowed to use this command.')
        return ConversationHandler.END

def ask_for_photo_with_text(update: Update, context: CallbackContext) -> int:
    # Request for an image (optional)
    context.user_data['TEXT'] = update.message.text # Retrive text from the previous state
    context.user_data['ENTITIES'] = update.message.entities
    update.message.reply_text(
        '📸Now send me an image if you wish to. Otherwise click the button below to skip this step. (Currently only the first image will be captured.)',
        reply_markup = ReplyKeyboardMarkup(Keyboards.NO_IMAGE, resize_keyboard = True)
    )
    return 1

def ask_for_photo_without_text(update: Update, context: CallbackContext) -> int:
    # Request for an image
    context.user_data['TEXT'] = '' # Set text to null
    context.user_data['ENTITIES'] = None
    update.message.reply_text(
        '📸Now send me an image that you wanna post. Currently only the first image will be captured.',
        reply_markup = ReplyKeyboardRemove()
    )
    return 2

def include_reactions(update: Update, context: CallbackContext) -> int:
    # Ask if the user want to include reaction buttons to the post
    photo = update.message.photo # Retrive image(s) sent by user from the previous state
    context.user_data['WITH_PHOTO'] = False if not photo else True
    context.user_data['PHOTO'] = photo[0] if photo else None # Save the first image to the memory
    update.message.reply_text(
        '❤Do you want to append reaction buttons to this post? Select the buttons below.',
        reply_markup = ReplyKeyboardMarkup(Keyboards.YES_NO, resize_keyboard = True)
    )
    return 3

def confirmation(update: Update, context: CallbackContext) -> int:
    # Send a preview of the post to the channel owner
    context.user_data['WITH_REACTIONS'] = True if update.message.text == 'Yes' else False
    if context.user_data['WITH_PHOTO']:
        m = update.message.reply_photo( # Use reply_photo() for post with image
            context.user_data['PHOTO'],
            caption = context.user_data['TEXT'],
            reply_markup = InlineKeyboardMarkup(Keyboards.REACTIONS_KEYBOARD_FOR_DISPLAY) if context.user_data['WITH_REACTIONS'] else None,
            caption_entities = context.user_data['ENTITIES']
        )
    else:
        m = update.message.reply_text( # Use reply_text() for post with just text
            context.user_data['TEXT'],
            reply_markup = InlineKeyboardMarkup(Keyboards.REACTIONS_KEYBOARD_FOR_DISPLAY) if context.user_data['WITH_REACTIONS'] else None,
            entities = context.user_data['ENTITIES']
        )
    context.user_data['CONFIRMATION_CHAT_ID'] = m.chat.id
    context.user_data['CONFIRMATION_MSG_ID'] = m.message_id
    update.message.reply_text(
        '❓The above message is going to be posted in the channel. Are you sure you want to do so?',
        reply_markup = ReplyKeyboardMarkup(Keyboards.YES_NO, resize_keyboard = True)
    )
    return 4

def send(update: Update, context: CallbackContext) -> int:
    # Post the content to the channel
    choice = update.message.text
    if choice == 'Yes':
        context.bot.copy_message(
            chat_id = MY_CHANNEL_ID,
            from_chat_id = context.user_data['CONFIRMATION_CHAT_ID'],
            message_id = context.user_data['CONFIRMATION_MSG_ID'],
            reply_markup = InlineKeyboardMarkup(Keyboards.REACTIONS_KEYBOARD) if context.user_data['WITH_REACTIONS'] else None,
            disable_notification = True # Slient post
        )
        update.message.reply_text('✅Sent successfully.', reply_markup = ReplyKeyboardRemove())
    else:
        update.message.reply_text('🗑Message discarded. Type /new to post again.', reply_markup = ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

'''For post submission of forwarded message'''
def confirmation_for_forwarded_msg(update: Update, context: CallbackContext) -> int:
    # Ask user to double check if that is the desired forwarded message
    context.user_data['FORWARDED_MSG'] = update.message
    if authentication(update):
        update.message.reply_text(
            '❓Do you want to forward this message to the channel?',
            reply_markup = ReplyKeyboardMarkup(Keyboards.YES_NO, resize_keyboard = True)
        )
        return 0
    else:
        context.user_data['FORWARDED_MSG_INFO'] =  f"""- {update.effective_user.first_name} {'' if update.effective_user.last_name == None else update.effective_user.last_name}
{datetime.now(timezone(timedelta(hours = 8))).strftime('%d/%m/%Y %H:%M:%S %Z')}"""
        preview = update.message.reply_text(
            context.user_data['FORWARDED_MSG_INFO'],
            reply_to_message_id = context.user_data['FORWARDED_MSG'].message_id,
            reply_markup = InlineKeyboardMarkup(Keyboards.REACTIONS_KEYBOARD_FOR_DISPLAY)
        )
        context.user_data['PREVIEW_MSG_ID'] = preview.message_id # Save this for returning approval result to the user as well for copying
        context.user_data['CHAT_ID'] = preview.chat.id # Save this for returning approval result to the user as well for copying
        update.message.reply_text(
            '❓The forwarded message is going to be sent to the channel owner for approval. Are you sure you want to do so?',
            reply_markup = ReplyKeyboardMarkup(Keyboards.YES_NO, resize_keyboard = True)
        )
        return 1

def forward_msg(update: Update, context: CallbackContext) -> int:
    # Forward the forwarded message to the channel (channel owner)
    choice = update.message.text
    if choice == 'Yes':
        context.bot.forward_message(
            chat_id = MY_CHANNEL_ID,
            from_chat_id = context.user_data['FORWARDED_MSG'].chat.id,
            message_id = context.user_data['FORWARDED_MSG'].message_id,
            disable_notification = True
        )
        update.message.reply_text('✅Sent successfully.', reply_markup = ReplyKeyboardRemove())
    else:
        update.message.reply_text('🗑Message discarded.', reply_markup = ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def approval_for_forward_msg(update: Update, context: CallbackContext) -> int:
    # Send the forwarded message to channel owner for approval
    choice = update.message.text
    if choice == 'Yes':
        key = Keyboards.FORWARD_APPROVAL_KEYBOARD
        key[1][0].text = context.user_data['PREVIEW_MSG_ID'] # Save the IDs into the text of the button
        key[2][0].text = context.user_data['CHAT_ID']
        msg = context.bot.forward_message( # the forwarded message itself
            chat_id = MY_ID,
            from_chat_id = context.user_data['FORWARDED_MSG'].chat.id,
            message_id = context.user_data['FORWARDED_MSG'].message_id
        )
        context.bot.copy_message(
            chat_id = MY_ID,
            from_chat_id = context.user_data['CHAT_ID'],
            message_id = context.user_data['PREVIEW_MSG_ID'],
            reply_markup = InlineKeyboardMarkup(key),
            reply_to_message_id = msg.message_id
        )
        update.message.reply_text(
            '✅Sent successfully. Your post will be posted if approved. Stay tuned!',
            reply_markup = ReplyKeyboardRemove()
        )
    else:
        update.message.reply_text('🗑Message discarded.', reply_markup = ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

'''For post submission using the command /submit'''
def ask_for_text_submission(update: Update, context: CallbackContext) -> int:
    # Request for text from other users
    if authentication(update):
        update.message.reply_text(f'ℹIt\'s your channel, {update.effective_user.first_name}. Use /new instead.')
        return ConversationHandler.END
    else:
        update.message.reply_text(f'👋Hello, {update.effective_user.first_name}. You are now going to submit a post.\nFeel free to type /cancel at any time to stop the process.')
        update.message.reply_text(
            '🗒What would you like to post? Type in and send text to me. To create a post without text, click the button below.',
            reply_markup = ReplyKeyboardMarkup(Keyboards.NO_TEXT, resize_keyboard = True)
        )
        return 0

def submission_confirmation(update: Update, context: CallbackContext) -> int:
    # Send a preview of the post to user
    photo = update.message.photo
    context.user_data['WITH_PHOTO'] = False if not photo else True
    context.user_data['PHOTO'] = photo[0] if photo else None
    context.user_data['TEXT'] = f"""{context.user_data['TEXT']}
- {update.effective_user.first_name} {'' if update.effective_user.last_name == None else update.effective_user.last_name}
{datetime.now(timezone(timedelta(hours = 8))).strftime('%d/%m/%Y %H:%M:%S %Z')}"""

    if context.user_data['WITH_PHOTO']:
        preview = update.message.reply_photo(
            context.user_data['PHOTO'],
            caption = context.user_data['TEXT'],
            reply_markup = InlineKeyboardMarkup(Keyboards.REACTIONS_KEYBOARD_FOR_DISPLAY), # Include reaction keyboard for submitted posts by default
            caption_entities = context.user_data['ENTITIES']
        )
    else:
        preview = update.message.reply_text(
            context.user_data['TEXT'],
            reply_markup = InlineKeyboardMarkup(Keyboards.REACTIONS_KEYBOARD_FOR_DISPLAY), # Include reaction keyboard for submitted posts by default
            entities = context.user_data['ENTITIES']
        )
    context.user_data['PREVIEW_MSG_ID'] = preview.message_id # Save this for returning approval result to the user
    context.user_data['CHAT_ID'] = preview.chat.id # Save this for returning approval result to the user
    update.message.reply_text(
        '❓The above message is going to be sent to the channel owner for approval. Are you sure you want to do so?',
        reply_markup = ReplyKeyboardMarkup(Keyboards.YES_NO, resize_keyboard = True)
    )
    return 3

def send_to_owner(update: Update, context: CallbackContext) -> int:
    # Send the post to channel owner for approval
    choice = update.message.text
    if choice == 'Yes':
        key = Keyboards.APPROVAL_KEYBOARD
        key[1][0].text = context.user_data['PREVIEW_MSG_ID'] # Save the IDs into the text of the button
        key[2][0].text = context.user_data['CHAT_ID']
        context.bot.copy_message(
            chat_id = MY_ID,
            from_chat_id = context.user_data['CHAT_ID'],
            message_id = context.user_data['PREVIEW_MSG_ID'],
            reply_markup = InlineKeyboardMarkup(key)
        )
        update.message.reply_text(
            '✅Sent successfully. The reaction buttons above will be replaced when your post has been approved/rejected. Stay tuned!',
            reply_markup = ReplyKeyboardRemove()
        )
    else:
        update.message.reply_text('🗑Message discarded. Type /submit to start again.', reply_markup = ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    # Escape from the conversation
    update.message.reply_text('ℹ️The process is cancelled. Send the command again to restart the program.', reply_markup = ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def inline_buttons(update: Update, context: CallbackContext) -> None:
    # Perform actions when inline buttons are clicked
    query = update.callback_query
    query.answer() # CallbackQueries need to be answered, even if no notification to the user is needed
    if query.data == '-1': # No action is performed
        return
    elif query.data == '1': # Approve a post submission
        context.bot.edit_message_reply_markup( # Returning an approved feedback to the user
            chat_id = int(query.message.reply_markup.inline_keyboard[2][0].text),
            message_id = int(query.message.reply_markup.inline_keyboard[1][0].text),
            reply_markup = InlineKeyboardMarkup(Keyboards.APPROVED_KEYBOARD)
        )
        query.copy_message(MY_CHANNEL_ID, reply_markup = InlineKeyboardMarkup(Keyboards.REACTIONS_KEYBOARD), disable_notification = True)
        query.edit_message_reply_markup(reply_markup = InlineKeyboardMarkup(Keyboards.APPROVED_KEYBOARD))
    elif query.data == '0': # Reject a post submission
        context.bot.edit_message_reply_markup( # Returning a rejected feedback to the user
            chat_id = int(query.message.reply_markup.inline_keyboard[2][0].text),
            message_id = int(query.message.reply_markup.inline_keyboard[1][0].text),
            reply_markup = InlineKeyboardMarkup(Keyboards.REJECTED_KEYBOARD)
        )
        query.edit_message_reply_markup(reply_markup = InlineKeyboardMarkup(Keyboards.REJECTED_KEYBOARD))
    elif query.data == '101': # Approve a post submission of forwarded message
        m = context.bot.forward_message(
            chat_id = MY_CHANNEL_ID,
            from_chat_id = query.message.reply_to_message.chat.id,
            message_id = query.message.reply_to_message.message_id,
            disable_notification = True
        )
        context.bot.copy_message(
            chat_id = MY_CHANNEL_ID,
            from_chat_id = query.message.chat.id,
            message_id = query.message.message_id,
            reply_to_message_id = m.message_id,
            reply_markup = InlineKeyboardMarkup(Keyboards.REACTIONS_KEYBOARD),
            disable_notification = True
        )
        context.bot.edit_message_reply_markup( # Returning an approved feedback to the user
            chat_id = int(query.message.reply_markup.inline_keyboard[2][0].text),
            message_id = int(query.message.reply_markup.inline_keyboard[1][0].text),
            reply_markup = InlineKeyboardMarkup(Keyboards.APPROVED_KEYBOARD),
        )
        query.edit_message_reply_markup(reply_markup = InlineKeyboardMarkup(Keyboards.APPROVED_KEYBOARD))
    elif query.data == '100': # Reject a post submission of forwarded message
        context.bot.edit_message_reply_markup( # Returning a rejected feedback to the user
            chat_id = int(query.message.reply_markup.inline_keyboard[2][0].text),
            message_id = int(query.message.reply_markup.inline_keyboard[1][0].text),
            reply_markup = InlineKeyboardMarkup(Keyboards.REJECTED_KEYBOARD)
        )
        query.edit_message_reply_markup(reply_markup = InlineKeyboardMarkup(Keyboards.REJECTED_KEYBOARD))
    elif query.data in Keyboards.REACTIONS_CALLBACK_DATA_LIST: # Increase the number count of reactions by 1
        emoji_keyboard = query.message.reply_markup.inline_keyboard
        number = int(emoji_keyboard[0][int(query.data)-1000].text[2::]) + 1
        emoji_keyboard[0][int(query.data)-1000].text = f'{Keyboards.EMOJI_LIST[int(query.data)-1000]} {number}'
        query.edit_message_reply_markup(InlineKeyboardMarkup(emoji_keyboard))

def about(update: Update, context: CallbackContext) -> None:
    # Send information of this bot
    update.message.reply_text(
        '@system\_logger\_bot *Beta*\n\nTailored for _System Logs_',
        parse_mode = ParseMode.MARKDOWN_V2,
        reply_markup = InlineKeyboardMarkup(Keyboards.ABOUT_KEYBOARD)
    )

def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Create new post handler
    new_post_handler = ConversationHandler(
        entry_points = [CommandHandler('new', ask_for_text)],
        states = { # dict
            0: [MessageHandler(Filters.regex(f'^{Keyboards.NO_TEXT[0][0]}$'), ask_for_photo_without_text), MessageHandler(Filters.text & ~Filters.command, ask_for_photo_with_text)],
            1: [MessageHandler(Filters.photo | Filters.regex(f'^{Keyboards.NO_IMAGE[0][0]}$'), include_reactions)],
            2: [MessageHandler(Filters.photo, include_reactions)],
            3: [MessageHandler(Filters.regex(f'^{Keyboards.YES_NO[0][0]}$') | Filters.regex(f'^{Keyboards.YES_NO[0][1]}$'), confirmation)],
            4: [MessageHandler(Filters.regex(f'^{Keyboards.YES_NO[0][0]}$') | Filters.regex(f'^{Keyboards.YES_NO[0][1]}$'), send)]
        },
        fallbacks = [CommandHandler('cancel', cancel)],
        conversation_timeout = 300 # 5 mins
    )
    # Register new post handler
    dispatcher.add_handler(new_post_handler)

    # Create submit post handler
    submit_post_handler = ConversationHandler(
        entry_points = [CommandHandler('submit', ask_for_text_submission)],
        states = {
            0: [MessageHandler(Filters.regex(f'^{Keyboards.NO_TEXT[0][0]}$'), ask_for_photo_without_text), MessageHandler(Filters.text & ~Filters.command, ask_for_photo_with_text)],
            1: [MessageHandler(Filters.photo | Filters.regex(f'^{Keyboards.NO_IMAGE[0][0]}$'), submission_confirmation)],
            2: [MessageHandler(Filters.photo, submission_confirmation)],
            3: [MessageHandler(Filters.regex(f'^{Keyboards.YES_NO[0][0]}$') | Filters.regex(f'^{Keyboards.YES_NO[0][1]}$'), send_to_owner)]
        },
        fallbacks = [CommandHandler('cancel', cancel)],
        conversation_timeout = 300 # 5 mins
    )
    # Register submit post handler
    dispatcher.add_handler(submit_post_handler)

    # Register handler for handling all inline button clicks
    dispatcher.add_handler(CallbackQueryHandler(inline_buttons))

    # Create forward message handler
    forward_handler = ConversationHandler(
        entry_points = [MessageHandler(Filters.forwarded, confirmation_for_forwarded_msg)],
        states = {
            0: [MessageHandler(Filters.regex(f'^{Keyboards.YES_NO[0][0]}$') | Filters.regex(f'^{Keyboards.YES_NO[0][1]}$'), forward_msg)],
            1: [MessageHandler(Filters.regex(f'^{Keyboards.YES_NO[0][0]}$') | Filters.regex(f'^{Keyboards.YES_NO[0][1]}$'), approval_for_forward_msg)]
        },
        fallbacks = [CommandHandler('cancel', cancel)],
        conversation_timeout = 120 # 2 mins
    )
    # Register forward message handler
    dispatcher.add_handler(forward_handler)

    # Register handler for the command /about
    dispatcher.add_handler(CommandHandler('about', about))

    # Start listening to webhook
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