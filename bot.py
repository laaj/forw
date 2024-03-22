import logging
import os
import psutil
import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.constants import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, CallbackContext, CallbackQueryHandler, Filters
from pymongo import MongoClient
from config import BOT_TOKEN, MONGODB_URI, API_ID, API_HASH

# Initialize logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Telegram bot
bot = telegram.Bot(token=BOT_TOKEN)

# Create a MongoDB client
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client['your_database_name']  # Replace with your actual database name
user_settings_collection = db['user_settings']
forwarded_messages_collection = db['forwarded_messages']

# Define conversation states if needed
CHOOSING, SELECT_OPTION = range(2)

# Define command handlers
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_html(
        f"ʜɪ {user.mention_html()}!\n"
        f"ɪ'ᴍ ᴀ ᴀᴅᴠᴀɴᴄᴇᴅ ᴀᴜᴛᴏ ꜰᴏʀᴡᴀʀᴅ ʙᴏᴛ\n"
        f"ɪ ᴄᴀɴ ꜰᴏʀᴡᴀʀᴅ ᴀʟʟ ᴍᴇssᴀɢᴇ ꜰʀᴏᴍ ᴏɴᴇ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴀɴᴏᴛʜᴇʀ ᴄʜᴀɴɴᴇʟ\n"
        f"ᴄʟɪᴄᴋ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ ᴀʙᴏᴜᴛ ᴍᴇ"
    )

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🔆 HELP\n"
        "📚 Available commands:\n"
        "⏣ /start - check I'm alive\n"
        "⏣ /forward - forward messages\n"
        "⏣ /private_forward - forward messages from private chat\n"
        "⏣ /unequify - delete duplicate media messages in chats\n"
        "⏣ /settings - configure your settings\n"
        "⏣ /stop - stop your ongoing tasks\n"
        "⏣ /reset - reset your settings\n"
        "\n"
        "💢 Features:\n"
        "► Forward message from public channel to your channel without admin permission. if the channel is private need admin permission\n"
        "► Forward message from private channel to your channel by using userbot(user must be member in there)\n"
        "► custom caption\n"
        "► custom button\n"
        "► support restricted chats\n"
        "► skip duplicate messages\n"
        "► filter type of messages\n"
        "► skip messages based on extensions & keywords & size"
    )

def start_settings(update: Update, context: CallbackContext):
    user = update.effective_user
    reply_keyboard = [
        [InlineKeyboardButton("Bots", callback_data="bots"), InlineKeyboardButton("Channels", callback_data="channels")],
        [InlineKeyboardButton("Caption", callback_data="caption")],
        [InlineKeyboardButton("Database", callback_data="database"), InlineKeyboardButton("Filters", callback_data="filters")],
        [InlineKeyboardButton("Button", callback_data="button")],
        [InlineKeyboardButton("Back", callback_data="back")]
    ]

    update.message.reply_html(
        f"Hi {user.mention_html()}! Change your settings as you wish.",
        reply_markup=InlineKeyboardMarkup(reply_keyboard)
    )

    return CHOOSING

def select_option(update: Update, context: CallbackContext):
    query = update.callback_query
    option = query.data

    if option == 'bots':
        query.message.reply_html("You can manage your bots here.")
    elif option == 'channels':
        query.message.reply_html("Change your settings as your wish.")
    elif option == 'caption':
        query.message.reply_text("🖋️ Custom Caption\n\nYou can set a custom caption to videos and documents. Normally, you would use the default caption. Available fillings include:\n\n• {filename} : File Name\n• {size} : File Size\n• {caption} : original caption")
    elif option == 'database':
        query.message.reply_text("🗃️ Database\n\nA database is necessary to store your duplicate messages and for the de-duplication process.")
    elif option == 'filters':
        query.message.reply_text("🌟 Custom Filters\n\nConfigure the type of messages which you want to forward.")
    elif option == 'button':
        query.message.reply_text("🔘 Custom Button\n\nYou can add inline buttons to messages with the following format:\n\nSingle Button in a row:\n\n[forward bot][buttonurl:https://t.me/mdforwardbot]\n\nMore than one button in the same row:\n\n[forward bot][buttonurl:https://t.me/mdforwardbot]\n[forward bot][buttonurl:https://t.me/mdforwardbot(:same)]")
    elif option == 'back':
        return end_settings(update, context)

    return CHOOSING

def end_settings(update: Update, context: CallbackContext):
    query = update.callback_query
    query.message.reply_text("Your settings have been updated.")
    query.message.reply_text("Change your settings as your wish.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Define conversation handler for settings
    settings_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('settings', start_settings)],
        states={
            CHOOSING: [CallbackQueryHandler(select_option)],
        },
        fallbacks=[],
    )

    dispatcher.add_handler(settings_conv_handler)

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
