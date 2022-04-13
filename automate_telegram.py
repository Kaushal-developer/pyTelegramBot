from unicodedata import name
from unittest import result
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
# print(dynamic_dict)


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
            print(scrip.get_analysis().summary)
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
            print(chat_id)
            context.bot.send_message(text=msg,chat_id=chat_id)
            time.sleep(2)

# def get_daily_updates():

def main():
    updater = Updater('5114313901:AAHVPAjF-rez-7hC4BNy2ds9u71vc4qIHqo', use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('quote',quote))
    dp.add_handler(MessageHandler(Filters.text, parse_msg))    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()