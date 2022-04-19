import csv
from nsetools import Nse
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
    def check_stock_is_in_bse(self,stock_name):
        matched_key =[]
        for key in bse_stock_list:
            if stock_name in key:
                matched_key.append(bse_stock_list[key])

        return matched_key

    def check_stock_is_in_nse(self,stock_name):
        matched_key =[]
        for key in nse_stock_list:
            if stock_name in key:
                matched_key.append(nse_stock_list[key])

        return matched_key
        
    def get_stock_prediction(self,stock_name):
        
        nse_key_list = self.check_stock_is_in_nse(stock_name)
        bse_key_list = self.check_stock_is_in_bse(stock_name)
        recommandations_NSE = {}
        for code in nse_key_list:
            scrip = TA_Handler(
                symbol=code,
                screener="india",
                exchange="NSE",
                interval=Interval.INTERVAL_1_DAY,
                # proxies={'http': 'http://example.com:8080'} # Uncomment to enable proxy (replace the URL).
            )
            if scrip.get_analysis():
                print(scrip.get_analysis().summary)
                recommandations_NSE[code] = scrip.get_analysis().summary["RECOMMENDATION"]

        recommandations_BSE = {}
        for code in bse_key_list:
            scrip = TA_Handler(
                symbol=code,
                screener="india",
                exchange="BSE",
                interval=Interval.INTERVAL_1_DAY,
                # proxies={'http': 'http://example.com:8080'} # Uncomment to enable proxy (replace the URL).
            )
            if scrip.get_analysis():
                recommandations_BSE[code] = scrip.get_analysis().summary["RECOMMENDATION"]
        return recommandations_NSE, recommandations_BSE

    def get_return_message(self,stock_name):
        nse_result,bse_result = self.get_stock_prediction(stock_name)
        text = ''
        for code,result in nse_result.items():
            if result in choices:
                text += "NSE based Company: " + nse_stock_codes[code] +' '+ choices[result] + ' would be preferrable.'
                text += "                   "
        for code,result in bse_result.items():
            if result in choices:
                text += "BSE based Company: " + bse_stock_code[code] +' '+ choices[result] + ' would be preferrable.'
                text += "        "
        if text == "":
            text = "Please try with company full name with underscore pattern like /tata_power."

        if nse_result == {} and bse_result == {}:
            text = ""
            text += 'Mr. BiLLA have not enough data to calculate predictions for the '+ stock_name +'. Please Check regularly to get predictions.'
        return text
