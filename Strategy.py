class Strategy():
    # option setting needed
    def __setitem__(self, key, value):
        self.options[key] = value

    # option setting needed
    def __getitem__(self, key):
        return self.options.get(key, '')

    def __init__(self):
        # strategy property
        self.subscribedBooks = {
            'Binance': {
                'pairs': ['BTC-USDT'],
            },
        }
        self.period = 15 * 60 #15分鐘線
        self.options = {}

        # user defined class attribute
        self.last_type = 'sell'
        self.last_macdHist = None
        self.max_profit = None
        self.buy_price = None
        self.high_price_trace = np.array([])
        self.low_price_trace = np.array([])
        self.close_price_trace = np.array([])
        self.fastperiod = 12
        self.slowperiod = 26
        self.signalperiod = 9
        self.timeperiodWR = 14
        self.timeperiodB = 21
        self.nbdevup = 2
        self.nbdevdn = 2
        self.matype = 0
        self.ma_long = 120
    

    # called every self.period
    def trade(self, information):

        exchange = list(information['candles'])[0]
        pair = list(information['candles'][exchange])[0]
        open_price = information['candles'][exchange][pair][0]['open']
        close_price = information['candles'][exchange][pair][0]['close']
        high_price = information['candles'][exchange][pair][0]['high']
        low_price = information['candles'][exchange][pair][0]['low']

        if (self['assets'][exchange]['USDT'] + self['assets'][exchange]['BTC']* close_price) < 85000 :
            if self['assets'][exchange]['BTC'] > 0 :
                return [
                        {
                            'exchange': exchange,
                            'amount':  - self['assets'][exchange]['BTC'],
                            'price': -1,
                            'type': 'MARKET',
                            'pair': pair,
                        }
                    ]  
            return []
        
        # add latest price into trace
        self.high_price_trace  = np.append(self.high_price_trace, [float(high_price)])
        self.low_price_trace    = np.append(self.low_price_trace, [float(low_price)])
        self.close_price_trace = np.append(self.close_price_trace, [float(close_price)])

        macd = talib.MACD(self.close_price_trace, self.fastperiod, self.slowperiod, self.signalperiod)[0][-2]
        macdHist = talib.MACD(self.close_price_trace, self.fastperiod, self.slowperiod, self.signalperiod)[2][-2]
        valueWR = talib.WILLR(self.high_price_trace, self.low_price_trace, self.close_price_trace, self.timeperiodWR)[-1]
        bollUP = talib.BBANDS(self.close_price_trace, self.timeperiodB, self.nbdevup, self.nbdevdn, self.matype)[0][-1]
        bollMB = talib.BBANDS(self.close_price_trace, self.timeperiodB, self.nbdevup, self.nbdevdn, self.matype)[1][-1]
        bollDN = talib.BBANDS(self.close_price_trace, self.timeperiodB, self.nbdevup, self.nbdevdn, self.matype)[2][-1]
        #ma_long = talib.SMA(self.close_price_trace, self.ma_long)[-1]

        if self.last_macdHist is None :
            self.last_macdHist = macdHist
            return []

        macdHistSlope = macdHist - self.last_macdHist
        self.last_macdHist = macdHist

        if  macd < 0 :
            macdAbs = -macd
        else : 
            macdAbs = macd

        if macdAbs// 15 > macd// macdHist :
            mul = macdAbs// 15
        else:
            mul = macd// macdHist 

        if bollDN* 998/ 1000 < low_price < bollDN* 1001/ 1000 :
            borderD = 'T'
        else:
            borderD = 'F'

        # cross up 1
        if macdHist < 0 and macdHistSlope > -5 and valueWR < -50 and macd < 0 : #self.last_type == 'sell'

            if  macdHist < -30 and macd < (macdHist/ 2) and (valueWR < -90 or (valueWR < -80 and borderD == 'T')) :      #  (valueWR <  -80 or borderD == 'T')
                self.last_type = 'buy'
                self.buy_price = close_price
                self.max_profit = 0
                if ((1+ mul)* close_price/ 4) < (self['assets'][exchange]['USDT'] - 5000 ):
                    amount =  (1+ mul)/ 4 
                else:
                    amount = (self['assets'][exchange]['USDT'] - 5000 ) / close_price
                Log('Buy1 ' + pair + ': ' + str(amount)) 
                if amount > 1/100 :
                    return [
                        {
                            'exchange': exchange,
                            'amount': amount,
                            'price': -1,
                            'type': 'MARKET',
                            'pair': pair,
                        }
                    ]
                return []
            elif -30 <= macdHist < -15 and macd < -15 and (valueWR < -90 or (valueWR < -80 and borderD == 'T')) :   
                self.last_type = 'buy'
                self.buy_price = close_price
                self.max_profit = 0
                if ((1+ mul)* close_price/ 4) < (self['assets'][exchange]['USDT'] - 5000 ):
                    amount =  (1+ mul)/ 4 
                else:
                    amount = (self['assets'][exchange]['USDT'] - 5000 ) / close_price
                Log('Buy2 ' + pair + ': ' + str(amount)) 
                if amount > 1/100 :
                    return [
                        {
                            'exchange': exchange,
                            'amount': amount,
                            'price': -1,
                            'type': 'MARKET',
                            'pair': pair,
                        }
                    ]
                return []
            elif macdHist >= -15 and macd < (macdHist* 8) and borderD == 'T' :   
                self.last_type = 'buy'
                self.buy_price = close_price
                self.max_profit = 0
                if ((1+ mul)* close_price/ 4) < (self['assets'][exchange]['USDT'] - 5000 ):
                    amount =  (1+ mul)/ 4 
                else:
                    amount = (self['assets'][exchange]['USDT'] - 5000 ) / close_price
                Log('Buy3 ' + pair + ': ' + str(amount)) 
                if amount > 1/100 :
                    return [
                        {
                            'exchange': exchange,
                            'amount': amount,
                            'price': -1,
                            'type': 'MARKET',
                            'pair': pair,
                        }
                    ]
                return []    
         
                
        # cross down 1
        elif  self.last_type == 'buy' : 
            #Log('selling, ' + exchange + ':' + pair)
            profit = high_price - self.buy_price

            if profit < (self.max_profit * 9 / 10 ) and self.max_profit > (self.buy_price * 12 / 100) and close_price < bollMB :
                self.last_type = 'sell'
                return [
                    {
                        'exchange': exchange,
                        'amount':  - self['assets'][exchange]['BTC'],
                        'price': -1,
                        'type': 'MARKET',
                        'pair': pair,
                    }
                ]
            elif profit < (self.max_profit * 8 / 10 ) and self.max_profit > (self.buy_price * 6 / 100) :
                self.last_type = 'sell'
                return [
                    {
                        'exchange': exchange,
                        'amount':  - self['assets'][exchange]['BTC'],
                        'price': -1,
                        'type': 'MARKET',
                        'pair': pair,
                    }
                ]   
            elif profit < (self.max_profit * 7 / 10 ) and self.max_profit > (self.buy_price * 3 / 100) :
                self.last_type = 'sell'
                return [
                    {
                        'exchange': exchange,
                        'amount':  - self['assets'][exchange]['BTC'],
                        'price': -1,
                        'type': 'MARKET',
                        'pair': pair,
                    }
                ]
            elif (close_price < (self.buy_price * 995 / 1000) or close_price < (bollDN * 995 / 1000)) and valueWR > -80 :
                self.last_type = 'sell'
                return [
                    {
                        'exchange': exchange,
                        'amount':  - self['assets'][exchange]['BTC'],
                        'price': -1,
                        'type': 'MARKET',
                        'pair': pair,
                    }
                ]    
            elif profit > self.max_profit:
                self.max_profit = profit    

        return []
