import os
import numpy as np
import pandas as pd
from itertools import combinations
from scipy.stats import linregress
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams['text.usetex'] = True
rcParams['font.family'] = 'serif'
rcParams['font.weight'] = 'black'

infile = 'DJ_results.csv'

df = pd.read_csv(infile)

df_reg = pd.DataFrame(columns=['Style', 'X', 'Y', 'Slope', 'Intercept', 'R', 'P', 'STD'])
df_reg_2 = pd.DataFrame()

yx_list = [['Jump_Height_(Impulse)', 'Depth'], \
           ['Jump_Height_(Impulse)', 'Contact_Time'], \
           ['Jump_Height_(Impulse)', 'GRF_Max_(Normalized)'], \
           ['Jump_Height_(Impulse)', 'GRF_at_Bottom_(Normalized)'], \
           ['Jump_Height_(Impulse)', 'Average_Power_(Normalized)'], \
           ['Jump_Height_(Impulse)', 'Peak_Power_(Normalized)'], \
           ['Average_Power_(Normalized)', 'GRF_Max_(Normalized)'], \
           ['Average_Power_(Normalized)', 'GRF_at_Bottom_(Normalized)'], \
           ['Average_Power_(Normalized)', 'Depth'], \
           ['Average_Power_(Normalized)', 'Contact_Time'], \
           ['Peak_Power_(Normalized)', 'GRF_Max_(Normalized)'], \
           ['Peak_Power_(Normalized)', 'GRF_at_Bottom_(Normalized)'], \
           ['Peak_Power_(Normalized)', 'Depth'], \
           ['Peak_Power_(Normalized)', 'Contact_Time'], \
           ['RSI_(Impulse)', 'GRF_Max_(Normalized)'], \
           ['RSI_(Impulse)', 'GRF_at_Bottom_(Normalized)'], \
           ['RSI_(Impulse)', 'Jump_Height_(Impulse)'], \
           ['RSI_(Impulse)', 'Contact_Time'], \
           ['RSI_(Impulse)', 'Average_Power_(Normalized)'], \
           ['RSI_(Impulse)', 'Peak_Power_(Normalized)'], \
           ['Time_GRF_Max', 'Time_GRF_Ecc_Max'], \
           ['Time_GRF_Max', 'Time_GRF_Con_Max']
           ]

label_dict = {
    'Jump_Height_(Impulse)': 'Height(m)',
    'Jump_Height_(Flight)': 'Height(m)',
    'Bodyweight': 'BW(kg)',
    'GRF_Impulse_(Normalized)': 'Impulse(N*s/kg)',
    'Net_Impulse_(Normalized)': 'Impulse(N*s/kg)',
    'Concentric_GRF_Impulse_(Normalized)': 'Impulse(N*s/kg)',
    'Concentric_Net_Impulse_(Normalized)': 'Impulse(N*s/kg)',
    'GRF_Max_(Normalized)': 'Force(N/kg)',
    'Net_F_Max_(Normalized)': 'Force(N/kg)',
    'GRF_at_Bottom_(Normalized)': 'Force(N/kg)',
    'Average_Power_(Normalized)': 'Power(W/kg)',
    'Peak_Power_(Normalized)': 'Power(W/kg)',
    'Depth': 'Depth(m)',
    'Contact_Time': 'Time(s)',
    'Time_GRF_Max': 'Time(s)',
    'Time_GRF_Ecc_Max': 'Time to maximum braking GRF(s)',
    'Time_GRF_Con_Max': 'Time to maximum propulsive GRF(s)',
    'RSI_(Impulse)': 'RSI(m/s)',
    'RSI_(Flight)': 'RSI(m/s)',
    'Stiffness': 'Stiffness(N/m)'
}

for style in ['SF', 'SS', 'ST']:
    for yx in yx_list:
        y = df.loc[df['Style'] == style, yx[0]]
        x = df.loc[df['Style'] == style, yx[1]]
        # print(yx[0])

        slope, intercept, rvalue, pvalue, stderr = linregress(x, y)
        # print([style, yx[1], yx[0], slope, intercept, rvalue, pvalue, stderr])

        df_temp = pd.DataFrame([[style, yx[1], yx[0], slope, intercept, rvalue, pvalue, stderr]], columns=['Style', 'X', 'Y', 'Slope', 'Intercept', 'R', 'P', 'STD'])
        # print(df_temp)
        df_reg = df_reg.append(df_temp)
        # print(df_reg)

        # fig, ax = plt.subplots()

        plt.scatter(x, y, color='black')
        plt.plot(x, slope * x + intercept, color='blue', linewidth=3)

        # plt.xticks(())
        plt.xlabel(label_dict[yx[1]], fontsize=16, fontweight='bold')
        # plt.yticks(())
        plt.ylabel(label_dict[yx[0]], fontsize=16, fontweight='bold')

        plt.savefig('Plot_Regression/' + style + '_' + yx[1] + '_' + yx[0] + '.png')

        plt.close()

df_reg.to_csv('Regression.csv', index=False)

for yx in [['Time_GRF_Max', 'Time_GRF_Ecc_Max'], ['Time_GRF_Max', 'Time_GRF_Con_Max']]:
    y = df[yx[0]]
    x = df[yx[1]]

    slope, intercept, rvalue, pvalue, stderr = linregress(x, y)

    df_temp = pd.DataFrame([[yx[1], yx[0], slope, intercept, rvalue, pvalue, stderr]], columns=['X', 'Y', 'Slope', 'Intercept', 'R', 'P', 'STD'])

    df_reg_2 = df_reg_2.append(df_temp)

    plt.scatter(x, y, color='black')
    plt.plot(x, slope * x + intercept, color='black', linewidth=1, linestyle=':')

    # plt.tight_layout()
    # plt.xticks(())
    plt.xlabel(label_dict[yx[1]], fontsize=24, fontfamily='sans-serif', fontweight='bold')
    # plt.yticks(())
    plt.ylabel(r"Time to GRF\textsubscript{Max} (s)", fontsize=24, fontfamily='sans-serif', fontweight='bold')
    plt.tight_layout()

    plt.savefig('Plot_Regression/' + yx[1] + '_' + yx[0] + '.png')

    plt.close()

df_reg_2.to_csv('Regression_2.csv', index=False)

# slope, intercept, rvalue, pvalue, stderr = linregress(x, y)
#
# print(slope, intercept, rvalue, pvalue, stderr)
#
# plt.scatter(x, y, color='black')
# plt.plot(x, slope * x + intercept, color='blue', linewidth=3)
#
# plt.xticks(())
# plt.yticks(())
#
# plt.show()