import os
import re
import csv
import numpy as np
import pandas as pd

from dj import DJ

dir_path = 'Individual_Replace_13ST2'

df_par = pd.DataFrame(columns=['Subject', 'Style', 'Trial', 'Jump_Height_(Impulse)', 'Jump_Height_(Flight)', \
                               'Bodyweight', 'GRF_Impulse_(Normalized)', 'Net_Impulse_(Normalized)', \
                               'Concentric_GRF_Impulse_(Normalized)', 'Concentric_Net_Impulse_(Normalized)', \
                               'GRF_Max_(Normalized)', 'Net_F_Max_(Normalized)', 'GRF_at_Bottom_(Normalized)', \
                               'Average_Power_(Normalized)', 'Peak_Power_(Normalized)', 'Depth', 'Contact_Time', \
                               'RSI_(Impulse)', 'RSI_(Flight)', 'Stiffness', 'Time_GRF_Max', 'Time_GRF_Ecc_Max', \
                               'Time_GRF_Con_Max', 'GRF_Max_2_(Normalized)', 'GRF_1st_high_(Normalized)', 'GRF_1st_low_(Normalized)', \
                               'GRF_2nd_high_(Normalized)', 'GRF_2nd_low_(Normalized)', 'Max_GRF_diff_1st_(Normalized)', \
                               'Max_GRF_diff_2nd_(Normalized)', 'GRF_1st_Higher_Side', 'GRF_2nd_Higher_Side', \
                               'Impulse_high_(Normalized)', 'Impulse_low_(Normalized)'])

df = pd.DataFrame(columns=['Subject', 'Style', 'Trial'])

for file in os.listdir(dir_path):
    if file.endswith('.csv') and not file.startswith('.'):
        print(file)
        match = re.search('(\d+)_(\D\D)_(\d).csv', file)
        subject = match.group(1)
        style = match.group(2)
        trial = match.group(3)
        # print(subject, style, trial)

        DJ_inst = DJ(0.42, os.path.join(dir_path, file))
        temp_dict = DJ_inst.parm_dict
        temp_dict.update({'Subject': subject, 'Style': style, 'Trial': trial})
        # print(temp_dict)

        df_par = df_par.append(temp_dict, ignore_index=True)
        # print(df_par)
        # input()

        temp_df = DJ_inst.df_raw
        df = df.append(temp_df, ignore_index=True)
        df.fillna({'Subject': subject, 'Style': style, 'Trial': trial}, inplace=True)
        # print(df)
        # input()

df_par = df_par.astype({'Subject': int, 'Trial': int})
df_par = df_par[(df_par.Subject != 2) & (df_par.Subject != 26)]
# print(df_par.Subject != 2)
# print(df_par.Subject != 26)
# print((df_par.Subject != 2) & (df_par.Subject != 26))
df_par.replace({'Subject': 25}, 2, inplace=True)
df_par.sort_values(['Subject', 'Style', 'Trial'], inplace=True)
df_par.to_csv('DJ_results.csv', index=False)
df.to_csv('DJ_raw.csv', index=False)

