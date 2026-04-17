import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# import seaborn as sns
from scipy import signal
from scipy.constants import g


class CMJ:
    """Countermovement jump"""

    def __init__(self, infile=None):
        self.import_csv(infile)

    def import_csv(self, infile):
        """Import .csv raw data."""

        col_label = ['Date and Time', 'Time (s)', 'Vertical Force A (N)', 'Vertical Force B (N)']

        if infile == None:
            print("Error! No input raw data file.\n")
        else:
            # 開啟 CSV 檔案
            with open(infile, newline='') as csvfile:

                # 讀取 CSV 檔案內容
                df = pd.read_csv(csvfile, header=1, names=col_label)

            df = df.dropna()

            df['Vertical Force Sum (N)'] = df['Vertical Force A (N)'] + df['Vertical Force B (N)']

        sample_rate = 1 / (df.at[1, 'Time (s)'] - df.at[0, 'Time (s)'])
        print(f"Sample rate is {sample_rate}.\n")

        #print(df.dropna())

        #Filter data
        #self.no_lag_butter(df, 4, 45, sample_rate)

        # print(df.columns)

        # df.plot(kind='line', subplots=False, x='Time (s)', y='Vertical Force Sum (N)', color='grey', legend=False)
        # plt.show()

        # Bodyweight
        BW = df.loc[0.5 * sample_rate:1.5 * sample_rate, 'Vertical Force Sum (N)'].mean() / g
        threshold = BW * g - 5 * df.loc[0.5 * sample_rate:1.5 * sample_rate, 'Vertical Force Sum (N)'].std(ddof=0)
        #print(BW)

        index_onset = df[df['Vertical Force Sum (N)'] < threshold].index[0]
        index_start = index_onset - 0.03 * sample_rate


        df['Phase'] = ""
        # df.at[index_onset, 'Phase'] = 'Unweighting'
        # print(df[df['Vertical Force Sum (N)'] < BW * g - threshold])

        index_flightref = df[df['Vertical Force Sum (N)'] < 0.05 * BW * g].index[0.05 * sample_rate]

        f_threshold = 5 * df.loc[index_flightref: index_flightref + 0.2 * sample_rate, 'Vertical Force Sum (N)'].std(ddof=0)
        # Need to jump higher than 16 cm

        df['Vertical Net Force (N)'] = df['Vertical Force Sum (N)'] - BW * g

        df['Phase'] = ""
        # df.at[index_start, 'Phase'] = 'Pre-unweighting'

        df['Impulse'] = np.nan
        df['Velocity'] = np.nan
        df['Height'] = np.nan

        check = 0
        for index, row in df.iterrows():
            if index < index_start:
                continue
            elif index == index_start:
                df.at[index, 'Impulse'] = 0.5 / sample_rate * (df.at[index - 1, 'Vertical Net Force (N)'] + df.at[index, 'Vertical Net Force (N)'])
                df.at[index, 'Velocity'] = df.at[index, 'Impulse'] / BW
                df.at[index, 'Height'] = 0
            else:
                df.at[index, 'Impulse'] = df.at[index - 1, 'Impulse'] + \
                    0.5 / sample_rate * (df.at[index - 1, 'Vertical Net Force (N)'] + df.at[index, 'Vertical Net Force (N)'])
                df.at[index, 'Velocity'] = df.at[index, 'Impulse'] / BW
                df.at[index, 'Height'] = df.at[index - 1, 'Height'] + \
                                         0.5 / sample_rate * (df.at[index - 1, 'Velocity'] + df.at[index, 'Velocity'])

            if df.at[index, 'Vertical Force Sum (N)'] < threshold and check == 0:
                df.at[index, 'Phase'] = 'Unweighting'
                check = 1
            elif df.at[index, 'Vertical Force Sum (N)'] > BW * g and check == 1:
                df.at[index, 'Phase'] = 'Braking'
                check = 2
            elif df.at[index, 'Velocity'] > 0 and check == 2:
                df.at[index, 'Phase'] = 'Propulsion'
                check = 3
            elif df.at[index, 'Vertical Force Sum (N)'] < f_threshold and check == 3:
                df.at[index, 'Phase'] = 'Flight'
                check = 4
            elif df.at[index, 'Vertical Force Sum (N)'] > f_threshold and check == 4:
                df.at[index, 'Phase'] = 'Landing'
                check = 5

            # print(df.at[index, 'Impulse'])
            # print(row)

        df['Phase'].replace('', inplace=True, method='ffill')
        df['Velocity'].fillna(0, inplace=True)
        df['Height'].fillna(0, inplace=True)

        # print(df['Phase'])

        # print(f"Jump height is {100 * df['Height'].max()} cm.\n")

        fig, axes = plt.subplots()
        plt.subplots_adjust(wspace=0.5, hspace=0.5)
        # axes.set_color_cycle(['yellow', 'red', 'green', 'grey', 'orange'])

        # df.plot(kind='line', subplots=False, x='Time (s)', y='Vertical Force Sum (N)', color='grey', legend=False)
        df.groupby('Phase')['Vertical Force Sum (N)'].plot(kind='line', ax=axes, subplots=False, x='Time (s)', legend=True)
        # df.groupby('Phase')['Velocity'].plot(kind='line', ax=axes[1], subplots=False, x='Time (s)', legend=True)
        # df.groupby('Phase')['Height'].plot(kind='line', ax=axes[2], subplots=False, x='Time (s)', legend=True)
        plt.text(100, 100, 'Jump height is ' + str(round(100 * df['Height'].max(), 2)) + ' cm', fontsize=12)

        delta_t = 1 / sample_rate * len(df[df['Phase'] == 'Flight'])
        h_flight = 0.5 * g * (delta_t / 2)**2
        plt.text(100, 200, 'Jump height using flight time is ' + str(round(100 * h_flight, 2)) + ' cm', fontsize=12)

        # grouped = df.groupby('Phase')
        #
        # for phase, group in grouped:
        #

        plt.show()





    def no_lag_butter(cls, df, order = 4, freq = 75, sample_rate = 1000):
        """No leg Butterworth filtering"""


        b, a = signal.butter(order/2 , 2*freq/sample_rate)

        df['Filtered Vertical Force A (N)'] = signal.filtfilt(b, a, df['Vertical Force A (N)'], padtype=None)
        df['Filtered Vertical Force B (N)'] = signal.filtfilt(b, a, df['Vertical Force B (N)'], padtype=None)

        df['Filtered Vertical Force Sum (N)'] = df['Filtered Vertical Force A (N)'] + df['Filtered Vertical Force B (N)']

        #print(df['Filtered Vertical Force B (N)'])


if __name__ == "__main__":
    infile = '/Users/Chinaeatshit/Documents/Temp/Jonny CMJ 2.csv'

    test = CMJ(infile)

