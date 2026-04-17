import os
import re
import csv
import numpy as np
import pandas as pd

from dj import DJ

test_list = []
group_dict = {
    'A': [1, 2, 3, 4],
    'B': [5, 6, 7, 8],
    'C': [9, 10, 11, 12],
    'D': [13, 14, 15, 16],
    'E': [17, 18, 19, 20],
    'F': [21, 22, 23, 24],
    'G': [25, 26]
}
# group_list = ['A', 'A', 'A', 'A', 'A', 'A',
#               'B', 'B', 'B', 'B', 'B',
#               'C', 'C', 'C', 'C', 'C', 'C',
#               'D', 'D', 'D', 'D', 'D',
#               'E', 'E', 'E', 'E', 'E', 'E',
#               'F', 'F', 'F', 'F', 'F', ]

dir_path = '/Users/Chinaeatshit/Library/Mobile Documents/com~apple~CloudDocs/Documents/PycharmProjects/PASCO/Lacrosse DJ raw data'

df = pd.DataFrame(columns=['Subject', 'Group', 'Style', 'Trial', 'Date and Time', 'Time (s)', 'Vertical Force A (N)', 'Vertical Force B (N)'])

for file in os.listdir(dir_path):
    if file.endswith('.csv') and not file.startswith('.'):
        print(file)
        match = re.search('([ABCDEFG])_(\D\D).csv', file)
        group = match.group(1)
        style = match.group(2)
        colname1 = []
        colname2 = []
        col2_n = 0
        colname3 = []
        # print(group, style)
        for num in group_dict[group]:
            colname1 = colname1 + [num] * 4
            col2_n = col2_n + 1
            colname3 = colname3 + ['Date and Time', 'Time (s)', 'Vertical Force A (N)', 'Vertical Force B (N)']
        colname1 = colname1 * 5
        colname2 = [1] * 4 * col2_n + [2] * 4 * col2_n + [3] * 4 * col2_n + [4] * 4 * col2_n + [5] * 4 * col2_n
        colname3 = colname3 * 5
        # print(colname1.__len__(), colname2.__len__(), colname3.__len__())
        df_temp = pd.read_csv(os.path.join(dir_path, file), header=[0,1], low_memory=False)
        df_temp.columns = [colname1, colname2, colname3]
        # print(df.columns)

        df_temp = df_temp.stack([0,1])
        df_temp.sort_index(level=[1,2], inplace=True)
        df_temp.reset_index(level=[1,2], inplace=True)
        df_temp.reset_index(drop=True, inplace=True)
        df_temp.columns = ['Subject', 'Trial', 'Date and Time', 'Time (s)', 'Vertical Force A (N)', 'Vertical Force B (N)']
        df_temp['Group'] = np.nan
        df_temp['Style'] = np.nan
        df_temp = df_temp.reindex(columns=['Subject', 'Group', 'Style', 'Trial', 'Date and Time', 'Time (s)', 'Vertical Force A (N)', 'Vertical Force B (N)'])
        # df_temp.astype({'Group': 'str', 'Style': 'str'})
        df_temp[['Group', 'Style']] = df_temp[['Group', 'Style']].astype('object')
        # print(df_temp[['Group', 'Style']].dtypes)
        df_temp.at[0, 'Group'] = group
        df_temp.at[0, 'Style'] = style

    #     with pd.option_context('display.max_rows', 100, 'display.max_columns', None):
    #         print(df_temp)
    #
        df = df.append(df_temp, ignore_index=True)
        df = df.reset_index(drop=True)

df.fillna(method='ffill', inplace=True)
# print(df)

# df_par = pd.DataFrame(columns=['Subject', 'Style', 'Trial', 'Jump Height'])


# test_name1 = 2
# test_name2 = 'ST'
# test_name3 = 3
# df_temp = df[['Date and Time', 'Time (s)', 'Vertical Force A (N)', 'Vertical Force B (N)']][(df['Subject'] == test_name1) & (df['Style'] == test_name2) & (df['Trial'] == test_name3)].reset_index(drop=True)
# DJ(0.42, df_temp)

folder = 'Individual/'
for the_file in os.listdir(folder):
    try:
        os.unlink(the_file)
        #elif os.path.isdir(file_path): shutil.rmtree(file_path)
    except Exception as e:
        print(e)


grouped = df.groupby(['Subject', 'Style', 'Trial'])
for name,group in grouped:
    # print(name[0])
    # print(group)

    # print((df['Subject'] == name[0]) & (df['Style'] == name[1]) & (df['Trial'] == name[2]))
    # print(df[['Date and Time', 'Time (s)', 'Vertical Force A (N)', 'Vertical Force B (N)']][(df['Subject'] == name[0]) & (df['Style'] == name[1]) & (df['Trial'] == name[2])])

    df_temp = df[['Date and Time', 'Time (s)', 'Vertical Force A (N)', 'Vertical Force B (N)']][(df['Subject'] == name[0]) & (df['Style'] == name[1]) & (df['Trial'] == name[2])].reset_index(drop=True)

    file_name = str(name[0]) + '_' + name[1] + '_' + str(name[2])
    df_temp.to_csv('Individual/' + file_name + '.csv', index=False)
    # DJ_inst = DJ(0.42, df_temp)
    # print(DJ_inst.j_height)
    # print(group[['Date and Time', 'Time (s)', 'Vertical Force A (N)', 'Vertical Force B (N)']])
    # print((DJ(45, group[['Date and Time', 'Time (s)', 'Vertical Force A (N)', 'Vertical Force B (N)']]).j_height))
    # print(list(name) + [DJ_inst.j_height])

#     df_par.loc[len(df_par)] =  list(name) + [DJ_inst.j_height]
#
# df_par.to_csv('DJ_results.csv', index=False)
# print(df_par)




