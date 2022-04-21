
from gc import callbacks
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters,CallbackQueryHandler
from tradingview_ta import TA_Handler, Interval, Exchange
import telegram
import time
from automate_ML import AutoML,Queue
from decouple import config
import os

ml = AutoML()
queue = Queue([])
API_KEY = config('KEY')

PORT = int(os.environ.get('PORT', '8443'))

import logging
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def parse_msg(update, context):
    if update is None:
        context.bot.send_message(chat_id='@channelid', text='this is a test')    
    if '/' in update["message"]["text"]:
        keyboard = [
            [
                telegram.InlineKeyboardButton("NSE",callback_data='NSE'),
                telegram.InlineKeyboardButton("BSE", callback_data='BSE'),
            ]
        ]
        queue.insert({"chat_id":update["message"]["chat"]["id"],"text":update["message"]["text"].replace('/','').lower()})
        reply_markup = telegram.InlineKeyboardMarkup(keyboard)        
        message = 'Please choose the stock exchange....\n' + 'NSE - National stock exchange\n' + 'BSE - Bombay stock exchange\n'
        update.message.reply_text(message, reply_markup=reply_markup)


def call_back_button(update, context):
    selection = update["callback_query"]["data"] if update["callback_query"]["data"] else ""
    previouse_chat = queue.get()
    current_queue = previouse_chat[0] if len(previouse_chat) > 0 else None
    if current_queue:
        user_messaged = current_queue["text"] 
        messages = ml.get_return_message(user_messaged,selection)
        for msg in messages:
            queue.remove(previouse_chat[0])
            time.sleep(0.5)
            context.bot.send_message(text=msg,chat_id=current_queue["chat_id"] )
            


def main():
    updater = Updater(API_KEY, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text, parse_msg))    
    dp.add_handler(CallbackQueryHandler(call_back_button, 
        pattern='^(NSE|BSE)$'))
    # updater.start_polling()
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=API_KEY,
                          webhook_url='https://bigbullsindia.herokuapp.com/' + API_KEY)
                          
    updater.idle()

if __name__ == '__main__':
    main()