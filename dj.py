import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# import seaborn as sns
from scipy import signal
from scipy.constants import g
from math import sqrt


class DJ:
    """Drop jump"""

    def __init__(self, d_height, infile):
        self.analysis(infile, d_height)


    def analysis(self, infile, d_height):
        """Import .csv raw data."""

        col_label = ['Date and Time', 'Time (s)', 'Vertical Force A (N)', 'Vertical Force B (N)']

        # df = df.reindex(columns=col_label)

        if infile == None:
            print("Error! No input raw data file.\n")
        else:
            # 開啟 CSV 檔案
            with open(infile, newline='') as csvfile:

                # 讀取 CSV 檔案內容
                df = pd.read_csv(csvfile, header=1, names=col_label)

        df.dropna(inplace=True)

        # Filtering
        # self.no_lag_butter(df)

        df['Vertical Force Sum (N)'] = df['Vertical Force A (N)'] + df['Vertical Force B (N)']

        sample_rate = 1 / (df.at[1, 'Time (s)'] - df.at[0, 'Time (s)'])
        #print(f"Sample rate is {sample_rate}.\n")

        # Bodyweight
        BW = df.loc[0:0.3 * sample_rate, 'Vertical Force Sum (N)'].mean() / g
        #print(BW)

        index_flightref = df[df['Vertical Force Sum (N)'] < 0.05 * BW * g].index[int(0.05 * sample_rate)]
        threshold = 50 * df.loc[index_flightref: index_flightref + 0.2 * sample_rate, 'Vertical Force Sum (N)'].std(ddof=0)
        # 50 * SD
        # Need to jump higher than 16 cm

        df['Vertical Net Force (N)'] = df['Vertical Force Sum (N)'] - BW * g

        df['Phase'] = ""
        # df.at[index_start, 'Phase'] = 'Pre-unweighting'

        df['Bodymass'] = np.nan
        df['Impulse_GRF'] = np.nan
        df['Impulse'] = np.nan
        df['Velocity'] = np.nan
        df['Height'] = np.nan
        df['Time_C1'] = np.nan
        df['Time_C2'] = np.nan

        index_onset = df[df['Vertical Force Sum (N)'] < threshold].index[0]
        index_start = index_onset - 0.03 * sample_rate

        check = 0
        for index, row in df.iterrows():
            df.at[index, 'Bodymass'] = BW

            if index <= 5 * sample_rate:
                continue

            if check >= 2:
                df.at[index, 'Impulse_GRF'] = df.at[index - 1, 'Impulse_GRF'] + \
                                              0.5 / sample_rate * (df.at[index - 1, 'Vertical Force Sum (N)'] + df.at[index, 'Vertical Force Sum (N)'])
                df.at[index, 'Impulse'] = df.at[index - 1, 'Impulse'] + \
                                          0.5 / sample_rate * (df.at[index - 1, 'Vertical Net Force (N)'] + df.at[index, 'Vertical Net Force (N)'])
                df.at[index, 'Velocity'] = - sqrt(2 * g * d_height) + df.at[index, 'Impulse'] / BW
                df.at[index, 'Height'] = df.at[index - 1, 'Height'] + \
                                         0.5 / sample_rate * (df.at[index - 1, 'Velocity'] + df.at[index, 'Velocity'])
                df.at[index, 'Work_GRF'] = df.at[index - 1, 'Work_GRF'] + \
                                           0.5 * (df.at[index - 1, 'Vertical Force Sum (N)'] + df.at[index, 'Vertical Force Sum (N)']) * \
                                           (df.at[index, 'Height'] - df.at[index - 1, 'Height'])
                df.at[index, 'Power_GRF'] = (df.at[index, 'Work_GRF'] - df.at[index - 1, 'Work_GRF']) * sample_rate

            if check >= 2:
                df.at[index, 'Time_C1'] = df.at[index - 1, 'Time_C1'] + 1

            if check == 5:
                df.at[index, 'Time_C2'] = df.at[index - 1, 'Time_C2'] + 1

            if df.at[index, 'Vertical Force Sum (N)'] < threshold and check == 0:
                df.at[index, 'Phase'] = 'Idle'
                check = 1
            elif df.at[index, 'Vertical Force Sum (N)'] > threshold and check == 1:
                df.at[index, 'Impulse_GRF'] = 0.5 / sample_rate * (df.at[index - 1, 'Vertical Force Sum (N)'] + df.at[index, 'Vertical Force Sum (N)'])
                df.at[index, 'Impulse'] = 0.5 / sample_rate * (df.at[index - 1, 'Vertical Net Force (N)'] + df.at[index, 'Vertical Net Force (N)'])
                df.at[index, 'Velocity'] = - sqrt(2 * g * d_height) + df.at[index, 'Impulse'] / BW
                df.at[index, 'Height'] = 0
                df.at[index, 'Work_GRF'] = 0
                df.at[index, 'Power_GRF'] = 0
                df.at[index, 'Time_C1'] = 0
                df.at[index, 'Phase'] = 'Braking'
                check = 2
            elif df.at[index, 'Velocity'] > 0 and check == 2:
                df.at[index, 'Phase'] = 'Propulsion'
                check = 3
            elif df.at[index, 'Vertical Force Sum (N)'] < threshold and check == 3:
                df.at[index, 'Phase'] = 'Flight'
                index_takeoff = index
                check = 4
            elif df.at[index, 'Vertical Force Sum (N)'] > threshold and check == 4 and index > index_takeoff + 0.2 * sample_rate:
                df.at[index, 'Time_C2'] = 0
                df.at[index, 'Phase'] = 'Landing'
                check = 5

            # print(df.at[index, 'Impulse'])
            # print(row)

        df['Time_Mod'] = df['Time (s)'] - df.at[df[df['Phase'] == 'Braking'].index[0], 'Time (s)']
        # print(df['Time_Mod'])
        # input()

        df['Phase'].replace('', inplace=True, method='ffill')
        df['Velocity'].fillna(0, inplace=True)
        df['Height'].fillna(0, inplace=True)
        # df['Time_C1'].fillna(0, inplace=True)
        # df['Time_C2'].fillna(0, inplace=True)

        # Determine higher GRF side in the first landing
        if df[(df['Phase'] == 'Braking') | (df['Phase'] == 'Propulsion')]['Vertical Force A (N)'].max() \
            > df[(df['Phase'] == 'Braking') | (df['Phase'] == 'Propulsion')]['Vertical Force B (N)'].max():
            df['GRF_1h_(Normalized)'] = df['Vertical Force A (N)']
            df['GRF_1l_(Normalized)'] = df['Vertical Force B (N)']
            GRF_1high_side = 'A'
        else:
            df['GRF_1h_(Normalized)'] = df['Vertical Force B (N)']
            df['GRF_1l_(Normalized)'] = df['Vertical Force A (N)']
            GRF_1high_side = 'B'

        if df[df['Phase'] == 'Landing']['Vertical Force A (N)'].max() > \
                df[df['Phase'] == 'Landing']['Vertical Force B (N)'].max():
            df['GRF_2h_(Normalized)'] = df['Vertical Force A (N)'] / BW
            df['GRF_2l_(Normalized)'] = df['Vertical Force B (N)'] / BW
            GRF_2high_side = 'A'
        else:
            df['GRF_2h_(Normalized)'] = df['Vertical Force B (N)'] / BW
            df['GRF_2l_(Normalized)'] = df['Vertical Force A (N)'] / BW
            GRF_2high_side = 'B'

        df['GRF_(Normalized)'] = df['Vertical Force Sum (N)'] / BW
        df['GRF_diff_(Normalized)'] = abs(df['Vertical Force A (N)'] - df['Vertical Force B (N)']) / BW

        df['Impulse_1h_(Normalized)'] = np.nan
        df['Impulse_1l_(Normalized)'] = np.nan
        check = 0
        for index, row in df.iterrows():
            if df.at[index, 'Time_C1'] > 0:
                df.at[index, 'Impulse_1h_(Normalized)'] = \
                    df.at[index - 1, 'Impulse_1h_(Normalized)'] + 0.5 / sample_rate * (df.at[index - 1, 'GRF_1h_(Normalized)'] + df.at[index, 'GRF_1h_(Normalized)'])
                df.at[index, 'Impulse_1l_(Normalized)'] = \
                    df.at[index - 1, 'Impulse_1l_(Normalized)'] + 0.5 / sample_rate * (df.at[index - 1, 'GRF_1l_(Normalized)'] + df.at[index, 'GRF_1l_(Normalized)'])
            elif df.at[index, 'Time_C1'] == 0:
                df.at[index, 'Impulse_1h_(Normalized)'] = 0
                df.at[index, 'Impulse_1l_(Normalized)'] = 0
                # check == 1


        # print(df['Height'])

        jh_impulse = (df.at[df[df['Phase'] == 'Propulsion'].index[-1], 'Velocity'])**2 / (2*g)
        jh_flighttime = 0.5 * g * (0.5 * df[df['Phase'] == 'Flight'].__len__() / sample_rate)**2
        impulseGRF_norm = df.at[df[df['Phase'] == 'Propulsion'].index[-1], 'Impulse_GRF'] / BW
        impulse_norm = df.at[df[df['Phase'] == 'Propulsion'].index[-1], 'Impulse'] / BW
        c_impulseGRF_norm = impulseGRF_norm - df.at[df[df['Phase'] == 'Braking'].index[-1], 'Impulse_GRF'] / BW
        c_impulse_norm = impulse_norm - df.at[df[df['Phase'] == 'Braking'].index[-1], 'Impulse'] / BW
        impulse1h_norm = df['Impulse_1h_(Normalized)'].max()
        impulse1l_norm = df['Impulse_1l_(Normalized)'].max()
        GRFmax = df[(df['Phase'] == 'Braking') | (df['Phase'] == 'Propulsion')]['Vertical Force Sum (N)'].max()
        GRFmax_norm = GRFmax / BW
        GRFmax2 = df[df['Phase'] == 'Landing']['Vertical Force Sum (N)'].max()
        GRFmax2_norm = GRFmax2 / BW
        GRFA1max = df[(df['Phase'] == 'Braking') | (df['Phase'] == 'Propulsion')]['Vertical Force A (N)'].max()
        GRFB1max = df[(df['Phase'] == 'Braking') | (df['Phase'] == 'Propulsion')]['Vertical Force B (N)'].max()
        GRFA1max_norm = GRFA1max / BW
        GRFB1max_norm = GRFB1max / BW
        GRFA2max = df[df['Phase'] == 'Landing']['Vertical Force A (N)'].max()
        GRFB2max = df[df['Phase'] == 'Landing']['Vertical Force B (N)'].max()
        GRFA2max_norm = GRFA2max / BW
        GRFB2max_norm = GRFB2max / BW
        GRF1h_norm = max(GRFA1max_norm, GRFB1max_norm)
        GRF1l_norm = min(GRFA1max_norm, GRFB1max_norm)
        GRF2h_norm = max(GRFA2max_norm, GRFB2max_norm)
        GRF2l_norm = min(GRFA2max_norm, GRFB2max_norm)
        GRF1max_norm_diff = abs(GRFA1max_norm - GRFB1max_norm)
        GRF2max_norm_diff = abs(GRFA2max_norm - GRFB2max_norm)
        # print(GRFmax_norm)
        # print(df[((df['Phase'] == 'Braking') | (df['Phase'] == 'Propulsion')) & (df['Vertical Force Sum (N)'] == GRFmax_norm * BW)]['Time_Mod'])
        t_GRF_max = df[((df['Phase'] == 'Braking') | (df['Phase'] == 'Propulsion')) & (df['Vertical Force Sum (N)'] == GRFmax)]['Time_Mod'].iloc[0]
        Fmax_norm = df[(df['Phase'] == 'Braking') | (df['Phase'] == 'Propulsion')]['Vertical Net Force (N)'].max() / BW
        bottomGRF_norm = df.at[df[df['Phase'] == 'Propulsion'].index[0], 'Vertical Force Sum (N)'] / BW
        GRFecc_max = df[df['Phase'] == 'Braking']['Vertical Force Sum (N)'].max()
        t_GRFecc_max = df[(df['Phase'] == 'Braking') & (df['Vertical Force Sum (N)'] == GRFecc_max)]['Time_Mod'].iloc[0]
        GRFcon_max = df[df['Phase'] == 'Propulsion']['Vertical Force Sum (N)'].max()
        t_GRFcon_max = df[(df['Phase'] == 'Propulsion') & (df['Vertical Force Sum (N)'] == GRFcon_max)]['Time_Mod'].iloc[0]
        power_avg_norm = (df.at[df[df['Phase'] == 'Propulsion'].index[-1], 'Work_GRF'] - df.at[df[df['Phase'] == 'Braking'].index[-1], 'Work_GRF']) / \
                         (len(df[df['Phase'] == 'Propulsion']) / sample_rate * BW)
        power_peak_norm = df[df['Phase'] == 'Propulsion']['Power_GRF'].max() / BW
        depth = - df.at[df[df['Phase'] == 'Braking'].index[-1], 'Height']
        t_contact = len(df[(df['Phase'] == 'Braking') | (df['Phase'] == 'Propulsion')]) / sample_rate
        rsi_impulse = jh_impulse / t_contact
        rsi_flighttime = jh_flighttime / t_contact
        k_leg = GRFmax_norm / depth

        self.parm_dict = {
            'Jump_Height_(Impulse)': jh_impulse,
            'Jump_Height_(Flight)': jh_flighttime,
            'Bodyweight': BW,
            'GRF_Impulse_(Normalized)': impulseGRF_norm,
            'Net_Impulse_(Normalized)': impulse_norm,
            'Concentric_GRF_Impulse_(Normalized)': c_impulseGRF_norm,
            'Concentric_Net_Impulse_(Normalized)': c_impulse_norm,
            'GRF_Max_(Normalized)': GRFmax_norm,
            'Net_F_Max_(Normalized)': Fmax_norm,
            'GRF_at_Bottom_(Normalized)': bottomGRF_norm,
            'Average_Power_(Normalized)': power_avg_norm,
            'Peak_Power_(Normalized)': power_peak_norm,
            'Depth': depth,
            'Contact_Time': t_contact,
            'RSI_(Impulse)': rsi_impulse,
            'RSI_(Flight)': rsi_flighttime,
            'Stiffness': k_leg,
            'Time_GRF_Max': t_GRF_max,
            'Time_GRF_Ecc_Max': t_GRFecc_max,
            'Time_GRF_Con_Max': t_GRFcon_max,
            'GRF_Max_2_(Normalized)': GRFmax2_norm,
            'GRF_1st_high_(Normalized)': GRF1h_norm,
            'GRF_1st_low_(Normalized)': GRF1l_norm,
            'GRF_2nd_high_(Normalized)': GRF2h_norm,
            'GRF_2nd_low_(Normalized)': GRF2l_norm,
            'Max_GRF_diff_1st_(Normalized)': GRF1max_norm_diff,
            'Max_GRF_diff_2nd_(Normalized)': GRF2max_norm_diff,
            'GRF_1st_Higher_Side': GRF_1high_side,
            'GRF_2nd_Higher_Side': GRF_2high_side,
            'Impulse_high_(Normalized)': impulse1h_norm,
            'Impulse_low_(Normalized)': impulse1l_norm
        }

        self.df_raw = df


        # # Visualization
        # print(jh_impulse)
        # print(jh_flighttime)
        # print(impulseGRF_norm)
        # print(impulse_norm)
        # print(c_impulseGRF_norm)
        # print(c_impulse_norm)
        # print(GRFmax_norm)
        # print(Fmax_norm)
        # print(bottomGRF_norm)
        # print(power_avg_norm)
        # print(power_peak_norm)
        # print(depth)
        # print(t_contact)
        # print(threshold)
        #
        # plt.figure(figsize=(3,4))

        # # Plot
        # fig, axes = plt.subplots(figsize=[20,5]) #nrows
        # plt.subplots_adjust(wspace=0.5, hspace=0.5)
        # df_plot = df[(df['Phase'] == 'Braking') | (df['Phase'] == 'Propulsion') | (df['Phase'] == 'Flight') | (df['Phase'] == 'Landing')]
        # df_plot = df_plot.set_index('Time_Mod')
        # df_plot.groupby('Phase')['Vertical Force Sum (N)'].plot(kind='line', ax=axes, subplots=False, legend=True, markersize=40)
        # axes.set_xlim(right=1.75)
        # axes.set_xlabel('Time (s)', fontsize=16, fontweight='bold')
        # axes.set_ylabel('Vertical Force Sum (N)', fontsize=16, fontweight='bold')
        # axes.legend(fontsize=12)
        # # plt.rcParams.update({'xtick.labelsize':})
        # plt.xticks(fontsize=12)
        # plt.yticks(fontsize=12)
        # plt.show()
        # # plt.savefig('Plot/SF/Work.png')



    def no_lag_butter(cls, df, order = 4, freq = 20, sample_rate = 1000):
        """No leg Butterworth filtering"""


        b, a = signal.butter(order/2 , 2*freq/sample_rate)

        df['Vertical Force A (N)'] = signal.filtfilt(b, a, df['Vertical Force A (N)'], padtype=None)
        df['Vertical Force B (N)'] = signal.filtfilt(b, a, df['Vertical Force B (N)'], padtype=None)

        #df['Filtered Vertical Force Sum (N)'] = df['Filtered Vertical Force A (N)'] + df['Filtered Vertical Force B (N)']

        #print(df['Filtered Vertical Force B (N)'])

if __name__ == "__main__":
    infile = 'Individual/12_ST_2.csv'
    # 19_ST_3
    # 19_SS_2
    # 19_SF_3

    test = DJ(0.42, infile)
    print(test.parm_dict)