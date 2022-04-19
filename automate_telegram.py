
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
from tradingview_ta import TA_Handler, Interval, Exchange
import requests
from nsetools import Nse
import re
import time
from automate_ML import AutoML
from decouple import config
import os

ml = AutoML()
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
        chat_id = update["message"]["chat"]["id"]
        user_messaged = update["message"]["text"].replace('/','').lower()
        message = ml.get_return_message(user_messaged)
        context.bot.send_message(text=message,chat_id=chat_id)
        time.sleep(1)

def main():
    updater = Updater(API_KEY, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text, parse_msg))    
    # updater.start_polling()
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=API_KEY,
                          webhook_url='https://billatrader.herokuapp.com/' + API_KEY)
                          
    updater.idle()

if __name__ == '__main__':
    main()