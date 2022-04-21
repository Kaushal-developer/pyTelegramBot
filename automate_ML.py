import csv
from os import remove
import queue
from nsetools import Nse
from numpy import append
from tradingview_ta import TA_Handler, Interval, Exchange

choices = {'STRONG_BUY':'STRONG BUY', 'STRONG_SELL': 'STRONG SELL','BUY': 'BUY', 'SELL':'SELL','NEUTRAL':'NEUTRAL'}

bse_stock_list = {}
bse_stock_code = {}

with open('bse_all_list.csv', mode ='r')as file:
    # reading the CSV file
    csvFile = csv.reader(file)
    # displaying the contents of the CSV file
    for lines in csvFile:
        bse_stock_list[lines[3].lower().replace(' ','_')] = lines[2]
        bse_stock_code[lines[2]] = lines[1]

nse = Nse()
nse_stock_codes = nse.get_stock_codes()
nse_stock_list = {}
for code, name in nse_stock_codes.items():
    nse_stock_list[name.lower().replace(' ','_')] = code


class AutoML:
    def check_stock(self,stock_name,exchange):
        if exchange == 'BSE':
            matched_key =[]
            for key in bse_stock_list:
                if stock_name in key:
                    matched_key.append(bse_stock_list[key])

            return matched_key
        else:
            matched_key =[]
            for key in nse_stock_list:
                if stock_name in key:
                    matched_key.append(nse_stock_list[key])

            return matched_key
        
    def get_stock_prediction(self,stock_name,exchange):
        
        key_list = self.check_stock(stock_name,exchange)
        recommandations = {}
       
        for code in key_list:
            scrip = TA_Handler(
                symbol=code,
                screener="india",
                exchange=exchange,
                interval=Interval.INTERVAL_1_DAY,
                proxies={'http': 'http://example.com:8080'} # Uncomment to enable proxy (replace the URL).
            )
            try:
                if scrip and scrip.get_analysis() and scrip.get_analysis().summary:
                    recommandations[code] = scrip.get_analysis().summary["RECOMMENDATION"]
            except Exception:
                continue
        return recommandations

    def get_return_message(self,stock_name,exchange):
        result = self.get_stock_prediction(stock_name,exchange)
        text = []
        for code,result in result.items():
            if result in choices:
                text.append(exchange + " based Company: " + nse_stock_codes[code] +' \n'+ choices[result] + ' would be preferrable.')
        if len(text) == 0:
            text.append("Please try with company full name with underscore pattern like /tata_power.")

        if result == {}:
            text = []
            text.append('Mr. BiLLA have not enough data to calculate predictions for the '+ stock_name +'. Please Check regularly to get predictions.')
        return text


class Queue:
    def __init__(self,queue_list):
        self.queue_list = queue_list

    def insert(self,data):
        self.queue_list.append(data)

    def remove(self,data):
        del self.queue_list[0]

    def get(self):
        return self.queue_list
