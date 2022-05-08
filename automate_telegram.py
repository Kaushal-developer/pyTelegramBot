import csv
from os import remove
from nsetools import Nse
from tradingview_ta import TA_Handler, Interval, Exchange
from nsepy import get_history
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn import linear_model
from datetime import datetime, timedelta
import numpy as np

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
               
            except Exception as e:
                print(e)
                continue

        return recommandations

    def get_return_message(self,stock_name,exchange):
        result = self.get_stock_prediction(stock_name,exchange)
        text = []
        price_bands = None
        for code,result in result.items():
            try:
                if exchange == "NSE":
                    price_bands = self.get_predicted_prices(code)
            except Exception as e:
                print(e)
            data = ""
            if result in choices:
                data = (exchange + " based Company: " + nse_stock_codes[code] +' \n'+ choices[result] + ' would be preferrable.\n')
                if price_bands is not None and 'score' in price_bands and 'bands' in price_bands:
                    data += 'Acuracy score: ' + str(round(price_bands["score"],2)) + ' \n'
                    string_form = [str(round(i,2)) for i in price_bands["bands"]]
                    data += "Upcoming Targets for a Week: \n" + ' ,\n'.join(string_form)
                text.append(data)
        if len(text) == 0:
            text.append("Please try with company full name with underscore pattern like /tata_power.")

        if result == {}:
            text = []
            text.append('Mr. BiLLA have not enough data to calculate predictions for the '+ stock_name +'. Please Check regularly to get predictions.')
        return text
    
    def get_predicted_prices(self,script):
        response={}
        to_date = datetime.now()
        from_date = to_date - timedelta(30)
        nse = Nse()
        if nse.is_valid_code(script):
            history= get_history(symbol=script, start=datetime.strptime(from_date.strftime("%Y-%m-%d"), '%Y-%m-%d'), end=datetime.strptime(to_date.strftime("%Y-%m-%d"), '%Y-%m-%d'))
            forecast_col = 'Close'
            forecast_out = 5 #how far to forecast 
            test_size = 0.2; #the size of my test set
            X_train, X_test, Y_train, Y_test , X_lately =prepare_data(history,forecast_col,forecast_out,test_size); 
            learner = linear_model.LinearRegression(); #initializing linear regression model
            learner.fit(X_train,Y_train); #training the linear regression model
            score=learner.score(X_test,Y_test);#testing the linear regression model
            forecast= learner.predict(X_lately); #set that will contain the forecasted data
            #creting json object
            response['score']=score
            response['bands']=forecast.tolist()
            
            return response
        else:
            return response

class Queue:
    def __init__(self,queue_list):
        self.queue_list = queue_list

    def insert(self,data):
        self.queue_list.append(data)

    def remove(self,data):
        del self.queue_list[0]

    def get(self):
        return self.queue_list


class QueueManager:
    def insert():
        pass
    def update_status():
        pass
    def create_user():
        pass


def prepare_data(df,forecast_col,forecast_out,test_size):
    label = df[forecast_col].shift(-forecast_out);#creating new column called label with the last 5 rows are nan\
    X = np.array(df[[forecast_col]]); #creating the feature array
    X = preprocessing.scale(X) #processing the feature array
    X_lately = X[-forecast_out:] #creating the column i want to use later in the predicting method
    X = X[:-forecast_out] # X that will contain the training and testing
    label.dropna(inplace=True); #dropping na values
    y = np.array(label)  # assigning Y
    X_train, X_test, Y_train, Y_test = train_test_split(X, y, test_size=test_size) #cross validation 
    response = [X_train,X_test , Y_train, Y_test , X_lately]
    return response
