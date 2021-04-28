import os
import glob
import pandas as pd

def computeMACD(price):
    exp1 = price.ewm(span=12, adjust=False).mean()
    exp2 = price.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    return macd

#########################################################
# Compute Relative Strength Index
# BE AWARE THAT PRICE HAS TO BE SORTED CHRONOLOGICALLY
#########################################################
def computeRSI(price, days=14):
    price = list(price)
    # determine if the price is higher or lower than the last one
    price_diff = [0] + [p - price[i - 1]
                        for i, p in enumerate(price[1:])]
    price_diff = pd.Series(price_diff)
    diff_rolling_window = price_diff.rolling(window=days)

    # Compute mean of bullish and bearish days
    RSI = []
    for i, period in enumerate(list(diff_rolling_window)):
        bulish_days = []
        bearish_days = []
        for j, day in enumerate(list(period)):
            if day > 0:  # bullish
                bulish_days.append(day)
            elif day <= 0:
                bearish_days.append(day)
        try:
            avg_gain = sum(bulish_days) / len(bulish_days)
        except ZeroDivisionError:
            avg_gain = 0
        try:
            avg_loss = sum(bearish_days) / len(bearish_days)
        except ZeroDivisionError:
            avg_loss = 0
        avg_gain = avg_gain / days
        avg_loss = abs(avg_loss / days)

        try:
            RSI.append(100 - (100 / (1 + (avg_gain / avg_loss))))
        except ZeroDivisionError:
            RSI.append(0)

    return RSI

def main():
    init_folder = os.getcwd() + '\\data'
    final_folder = os.getcwd() + '\\data_clean'
    if not os.path.exists(final_folder):
        os.mkdir(final_folder)

    for f in glob.glob(init_folder + '\\*.csv'):
        name = f.split('\\')[-1]
        print(f"Processing {name}...")
        df = pd.read_csv(f)

        # 1. Usamos Date como index
        df = df.set_index('Date')

        # 2. Borramos la columna SNo y Name dado que está duplicada
        df = df.drop(['SNo', 'Name'], axis = 1)

        # 3. Computamos el porcentaje de cambio
        _open = list(df['Open'])
        _close = list(df['Close'])
        diff = [round(_close[i] - _open[i], 2) for i in range(len(_open))]

        df['DiffDay'] = diff
        df['Up/Down'] = [1 if d > 0 else 0 for d in diff]

        change = []
        for i, today in enumerate(_close):
            if i == 0:
                change.append(None)
            else:
                yesterday = _close[i - 1]
                if yesterday > today:
                    diff = -((yesterday - today) / today)*100
                else:
                    diff = ((today - yesterday) / yesterday)*100
                change.append(diff)
        df['Change'] = change
        
        df['MACD'] = computeMACD(df['Close'])
        df['RSI'] = computeRSI(df['Close'])

        df['sma5'] = df['Close'].rolling(window=5).mean()
        df['sma10'] = df['Close'].rolling(window=10).mean()

        df.to_csv(final_folder + '\\' + name)

if __name__ == '__main__':
    main()
