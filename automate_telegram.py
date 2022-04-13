
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
from tradingview_ta import TA_Handler, Interval, Exchange
import requests
from nsetools import Nse
import re
import time
nse = Nse()
all_stock_codes = nse.get_stock_codes()
dynamic_dict = {}
for code, name in all_stock_codes.items():
    dynamic_dict[name.lower().replace(' ','_')] = code


from decouple import config


API_KEY = config('KEY')

# print(dynamic_dict)
import os
PORT = int(os.environ.get('PORT', '8443'))

import logging
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def predict_buy_sel_one_day(codes):
    recommandations = {}
    for code in codes:
        scrip = TA_Handler(
            symbol=code,
            screener="india",
            exchange="NSE",
            interval=Interval.INTERVAL_1_DAY,
            # proxies={'http': 'http://example.com:8080'} # Uncomment to enable proxy (replace the URL).
        )
        if scrip.get_analysis().summary:
            recommandations[code] = scrip.get_analysis().summary["RECOMMENDATION"]
    return recommandations


def quote(update,context):
    chat_id = update["message"]["chat"]["id"]
    user_messaged = update["message"]["text"]
    for code,name in all_stock_codes.items():
        # time.sleep(5)
        context.bot.send_message(text='Name: '+name+' '+' code: '+code,chat_id=chat_id)
        time.sleep(2)


def parse_msg(update, context):
    if update is None:
        context.bot.send_message(chat_id='@channelid', text='this is a test')
    else:
        chat_id = update["message"]["chat"]["id"]
        user_messaged = update["message"]["text"].replace('/','').lower()
        print(user_messaged)
        matched_key = []
        for key in dynamic_dict:
            if user_messaged in key:
                matched_key.append(dynamic_dict[key])

        #lets predict the buy or sell
        results = predict_buy_sel_one_day(matched_key)
        for code,result in results.items():
            msg = "For " + all_stock_codes[code] +' '+ result + ' is recommended(As per the daily chart pattern basis).'
            context.bot.send_message(text=msg,chat_id=chat_id)
            time.sleep(2)

# def get_daily_updates():

def main():
    updater = Updater(API_KEY, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('quote',quote))
    dp.add_handler(MessageHandler(Filters.text, parse_msg))    
    # updater.start_polling()
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=API_KEY,
                          webhook_url='https://billatrader.herokuapp.com/' + API_KEY)
                          
    updater.idle()

if __name__ == '__main__':
    main()