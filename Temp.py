import os
import csv
import numpy as np
import pandas as pd

# infile = 'DJ_results.csv'
#
# df_result = pd.read_csv(infile)
#
# grouped = df_result.groupby(['Subject', 'Style'])
#
# agg = grouped['Jump Height (Flight)'].agg(np.median)
#
# pd.DataFrame(agg).to_csv('DJ_median.csv')

folder = '20200131LAXDJ - U19/'
for the_file in os.listdir(folder):
    try:
        df = pd.read_csv(folder + the_file, header=[0,1])
        if len(df.columns) > 4:
            name = df.columns
            df = df.drop(columns=name[:-4])

            df.to_csv(folder + the_file, index=False)
    except Exception as e:
        print(e)