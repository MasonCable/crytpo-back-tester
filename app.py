import pandas as pd
import requests as req
import json
import time

from pyti.smoothed_moving_average import smoothed_moving_average as sma

from plotly.offline import plot
import plotly.graph_objs as go

class TradingModel:

    def __init__(self, symbol):
        self.symbol = symbol
        self.df = self.getData()

    def getData(self):

        # Define URL
        base = 'https://api.binance.com'
        endpoint = '/api/v1/klines'
        params = '?&symbol='+self.symbol+'&interval=1d'

        url = base + endpoint + params

        # Download Data
        data = req.get(url)
        dictonary = json.loads(data.text)

        # Put in dataframe and clean-up
        df = pd.DataFrame.from_dict(dictonary)
        df = df.drop(range(6, 12), axis=1)

        # rename colums
        col_names = ['time', 'open', 'high', 'low', 'close', 'volume']
        df.columns = col_names
        
        # Transform values from string to float
        for col in col_names:
            df[col] = df[col].astype(float)
        df['fast_sma'] = sma(df['close'].tolist(), 10)
        df['slow_sma'] = sma(df['close'].tolist(), 30)

        return df

    def strategy(self):
        df = self.df
        
        
        buy_signals = []

        for i in range(1, len(df['close'])):
            if df['slow_sma'][i] > df['low'][i] and (df['slow_sma'][i] - df['low'][i]) > 0.03 * df['low'][i]:
                cur_price = df['low'][i]
                buy_signals.append([ 
                                    df['time'][i],
                                    df['low'][i],
                                    # df['shares'][i]
                                    ])
                    


        return self.plotData(buy_signals = buy_signals), self.managePositions()
        # print(self.getData())col_name

    def plotData(self, buy_signals = False):
        df = self.df
        
        candle = go.Candlestick(
            x = df['time'],
            open = df['open'],
            close = df['close'],
            high = df['high']
        )
        fsma = go.Scatter(
            x = df['time'],
            y = df['fast_sma'],
            name = "Fast SMA",
            line = dict(color = ('rgba(102, 207, 255, 50)'))
        )

        ssma = go.Scatter(
            x = df['time'],
            y = df['fast_sma'],
            name = 'Slow SMA',
            line = dict(color = ('rgba(255, 207, 102, 50)')))
        
        price = go.Scatter(
            x = df['time'],
            y = df['low'],
            name = "Price",
            line = dict(color = ('rgba(0, 0, 0, 100)'))
        )

        data = [candle, ssma, fsma, price]

        if buy_signals:
            buys = go.Scatter(
                x = [item[0] for item in buy_signals],
                y = [item[1] for item in buy_signals],
                name = "Buy Signals",
                mode = 'markers'                
            )

            sells = go.Scatter(
                x = [item[0] for item in buy_signals],
                y = [item[1] * 1.02 for item in buy_signals],
                name = "Sell Signals",
                mode = 'markers'
            )
            data = [candle, buys, sells, price]
        

        layout = go.Layout(title = self.symbol)
        fig = go.Figure(data = data, layout = layout)

        return plot(fig, filename=self.symbol)


def Main():
    symbol = "BTCUSDT"
    
    model = TradingModel(symbol)
    model.strategy()
    
    
if __name__ == '__main__':
    Main()


    