import logging
import os
import Keyboards

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters, CallbackContext, CallbackQueryHandler
#from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

# BUG no message previews for submitted posts due to the function copy_message()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO
)

logger = logging.getLogger(__name__)

# Load credentials from enviroment variables
#load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
MY_USERNAME = os.getenv('MY_TG_HANDLE')
MY_CHANNEL_ID = os.getenv('MY_CHANNEL_ID')
MY_ID = os.getenv('MY_ID')
PORT = os.getenv('PORT')

def authentication(update: Update) -> bool:
    # Check if the sender is the channel owner
    return update.effective_user.username == MY_USERNAME

def buttons_or_confirmation(update: Update, context: CallbackContext) -> int:
    context.user_data['MESSAGE'] = update.message
    if authentication(update):
        update.message.reply_text(
            '❤Do you want to append reaction buttons to this post?',
            reply_markup = ReplyKeyboardMarkup(Keyboards.YES_NO, resize_keyboard = True)
        )
    else:
        if (update.message.text is None) & (update.message.caption is None) | (update.message.forward_date is not None):
            text = ''
        elif update.message.text != None:
            text = update.message.text
        else:
            text = update.message.caption
        entities = update.message.caption_entities
        t = f"""{text}
- {update.effective_user.first_name} {'' if update.effective_user.last_name is None else update.effective_user.last_name}
{datetime.now(timezone(timedelta(hours = 8))).strftime('%d/%m/%Y %H:%M:%S %Z')}"""
        if update.message.forward_date is not None:
            m = update.message.forward(chat_id = update.effective_message.chat_id)
            preview = update.message.reply_text(
                text = t,
                reply_to_message_id = m.message_id,
                reply_markup = InlineKeyboardMarkup(Keyboards.REACTIONS_KEYBOARD_FOR_DISPLAY)
            )
        else:
            msg_id = update.message.copy(chat_id = update.effective_message.chat_id)
            if update.message.text is not None:
                preview = context.bot.edit_message_text(
                    text = t,
                    chat_id = update.effective_message.chat_id,
                    message_id = msg_id.message_id,
                    reply_markup = InlineKeyboardMarkup(Keyboards.REACTIONS_KEYBOARD_FOR_DISPLAY),
                    entities = entities
                )
            elif (update.message.animation is not None) | (update.message.audio is not None) | (update.message.document is not None) | (len(update.message.photo) != 0)  | (update.message.video is not None) | (update.message.voice is not None):# (update.message.caption != None):
                preview = context.bot.edit_message_caption(
                    caption = t,
                    chat_id = update.effective_message.chat_id,
                    message_id = msg_id.message_id,
                    reply_markup = InlineKeyboardMarkup(Keyboards.REACTIONS_KEYBOARD_FOR_DISPLAY),
                    caption_entities = entities
                )
            else:
                preview = update.message.reply_text(
                    text = t,
                    reply_to_message_id = msg_id.message_id,
                    reply_markup = InlineKeyboardMarkup(Keyboards.REACTIONS_KEYBOARD_FOR_DISPLAY)
                )
        context.user_data['PREVIEW_MSG_ID'] = preview.message_id # Save this for returning approval result to the user as well for copying
        context.user_data['CHAT_ID'] = preview.chat.id # Save this for returning approval result to the user as well for copying
        update.message.reply_text(
            '❓This message is going to be sent to the channel owner for approval. Are you sure you want to do so?',
            reply_markup = ReplyKeyboardMarkup(Keyboards.YES_NO, resize_keyboard = True)
        )
        return 1
    return 0

def send_to_owner(update: Update, context: CallbackContext) -> int:
    if update.message.text == 'Yes':
        key = Keyboards.APPROVAL_KEYBOARD
        key[1][0].text = context.user_data['PREVIEW_MSG_ID'] # Save the IDs into the text of the button
        key[2][0].text = context.user_data['CHAT_ID']
        if ((context.user_data['MESSAGE'].text is not None) | (context.user_data['MESSAGE'].animation is not None) | (context.user_data['MESSAGE'].audio is not None) | (context.user_data['MESSAGE'].document is not None) | (len(context.user_data['MESSAGE'].photo) != 0) | (context.user_data['MESSAGE'].video is not None) | (context.user_data['MESSAGE'].voice is not None)) & (context.user_data['MESSAGE'].forward_date is None): #does_message_contain_text(update.message):
            context.bot.copy_message(
                chat_id = MY_ID,
                from_chat_id = context.user_data['CHAT_ID'],
                message_id = context.user_data['PREVIEW_MSG_ID'],
                reply_markup = InlineKeyboardMarkup(key)
            )
        else:
            if context.user_data['MESSAGE'].forward_date is not None:
                msg = context.bot.forward_message(
                    chat_id = MY_ID,
                    from_chat_id = context.user_data['MESSAGE'].chat.id,
                    message_id = context.user_data['MESSAGE'].message_id
                )
            else:
                msg = context.bot.copy_message(
                    chat_id = MY_ID,
                    from_chat_id = context.user_data['MESSAGE'].chat.id,
                    message_id = context.user_data['MESSAGE'].message_id
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

def confirmation_from_owner(update: Update, context: CallbackContext) -> int:
    context.user_data['WITH_REACTIONS'] = True if update.message.text == 'Yes' else False
    if context.user_data['MESSAGE'].forward_date == None:
        context.bot.copy_message(
            chat_id = context.user_data['MESSAGE'].chat.id,
            from_chat_id = context.user_data['MESSAGE'].chat.id,
            message_id = context.user_data['MESSAGE'].message_id,
            reply_markup = InlineKeyboardMarkup(Keyboards.REACTIONS_KEYBOARD_FOR_DISPLAY) if context.user_data['WITH_REACTIONS'] else None
        )
    else:
        m = context.bot.forward_message(
            chat_id = context.user_data['MESSAGE'].chat.id,
            from_chat_id = context.user_data['MESSAGE'].chat.id,
            message_id = context.user_data['MESSAGE'].message_id,
        )
        if context.user_data['WITH_REACTIONS']:
            update.message.reply_text(
                '🤔?',
                reply_markup = InlineKeyboardMarkup(Keyboards.REACTIONS_KEYBOARD_FOR_DISPLAY),
                reply_to_message_id = m.message_id
            )
    update.message.reply_text(
        '❓Do you want to send this message to the channel?',
        reply_markup = ReplyKeyboardMarkup(Keyboards.YES_NO, resize_keyboard = True)
    )
    return 2

def send_by_owner(update: Update, context: CallbackContext) -> int:
    if update.message.text == 'Yes':
        if context.user_data['MESSAGE'].forward_date is None:
            context.bot.copy_message(
                chat_id = MY_CHANNEL_ID,
                from_chat_id = context.user_data['MESSAGE'].chat.id,
                message_id = context.user_data['MESSAGE'].message_id,
                reply_markup = InlineKeyboardMarkup(Keyboards.REACTIONS_KEYBOARD) if context.user_data['WITH_REACTIONS'] else None,
                disable_notification = True
            )
        else:
            m = context.bot.forward_message(
                chat_id = MY_CHANNEL_ID,
                from_chat_id = context.user_data['MESSAGE'].chat.id,
                message_id = context.user_data['MESSAGE'].message_id,
            )
            if context.user_data['WITH_REACTIONS']:
                update.message.reply_text(
                    '🤔?',
                    reply_markup = InlineKeyboardMarkup(Keyboards.REACTIONS_KEYBOARD),
                    reply_to_message_id = m.message_id
                )
        update.message.reply_text('✅Sent successfully.', reply_markup = ReplyKeyboardRemove())
    else:
        update.message.reply_text('🗑Message discarded.', reply_markup = ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def inline_buttons(update: Update, context: CallbackContext) -> None:
    # Perform actions when inline buttons are clicked
    query = update.callback_query
    query.answer() # CallbackQueries need to be answered, even if no notification to the user is needed
    if query.data == '1': # Approve a post submission
        context.bot.edit_message_reply_markup( # Returning an approved feedback to the user
            chat_id = int(query.message.reply_markup.inline_keyboard[2][0].text),
            message_id = int(query.message.reply_markup.inline_keyboard[1][0].text),
            reply_markup = InlineKeyboardMarkup(Keyboards.APPROVED_KEYBOARD)
        )
        query.edit_message_reply_markup(reply_markup = InlineKeyboardMarkup(Keyboards.APPROVED_KEYBOARD))
        if query.message.reply_to_message is None:
            query.copy_message(MY_CHANNEL_ID, reply_markup = InlineKeyboardMarkup(Keyboards.REACTIONS_KEYBOARD), disable_notification = True)
        else:
            if query.message.reply_to_message.forward_date is not None:
                m = context.bot.forward_message(
                    chat_id = MY_CHANNEL_ID,
                    from_chat_id = query.message.reply_to_message.chat.id,
                    message_id = query.message.reply_to_message.message_id,
                    disable_notification = True
                )
            else:
                m = context.bot.copy_message(
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
    elif query.data == '0': # Reject a post submission
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

def cancel(update: Update, context: CallbackContext) -> int:
    # Escape from the conversation
    update.message.reply_text('ℹ️The process is cancelled. Send the command again to restart the program.', reply_markup = ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def about(update: Update, context: CallbackContext) -> None:
    # Send information of this bot
    update.message.reply_text(
        '@system\_logger\_bot *Beta*\n\nTailored for _System Logs_',
        parse_mode = ParseMode.MARKDOWN_V2,
        reply_markup = InlineKeyboardMarkup(Keyboards.ABOUT_KEYBOARD)
    )

def instruction(update: Update, context: CallbackContext) -> None:
    # Send instructions of this bot
    update.message.reply_text(
        '*Instructions*\nSend anything to me to create a post submission\.\nYes, literally _anything_: Text, image, sticker, gif, poll, location, voice, etc\.',
        parse_mode = ParseMode.MARKDOWN_V2
    )

def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Create a submission handler
    submission_handler = ConversationHandler(
        entry_points = [MessageHandler(~ Filters.command, buttons_or_confirmation)],
        states = {
            0: [MessageHandler(Filters.regex(f'^{Keyboards.YES_NO[0][0]}$') | Filters.regex(f'^{Keyboards.YES_NO[0][1]}$'), confirmation_from_owner)],
            1: [MessageHandler(Filters.regex(f'^{Keyboards.YES_NO[0][0]}$') | Filters.regex(f'^{Keyboards.YES_NO[0][1]}$'), send_to_owner)],
            2: [MessageHandler(Filters.regex(f'^{Keyboards.YES_NO[0][0]}$') | Filters.regex(f'^{Keyboards.YES_NO[0][1]}$'), send_by_owner)],
        },
        fallbacks = [CommandHandler('cancel', cancel)],
        conversation_timeout = 120 # 2 mins
    )
    # Register the submission handler
    dispatcher.add_handler(submission_handler)

    # Register handler for handling all inline button clicks
    dispatcher.add_handler(CallbackQueryHandler(inline_buttons))

    # Register handler for the command /about
    dispatcher.add_handler(CommandHandler('about', about))

    # Register handler for command /howto
    dispatcher.add_handler(CommandHandler('howto', instruction))

    # Start the Bot using polling
    #updater.start_polling()
    #updater.idle()

    # Start listening to webhook
    updater.start_webhook(listen = "0.0.0.0",
                      port = PORT,
                      url_path = BOT_TOKEN,
                      webhook_url = "https://system-logger-bot.herokuapp.com/" + BOT_TOKEN)
    updater.idle()

if __name__ == '__main__':
    main()