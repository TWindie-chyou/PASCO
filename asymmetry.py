import os
import re
import csv
import numpy as np
import pandas as pd
import pingouin as pg
# import pyvttbl as pt
from scipy import stats
from statsmodels.stats.multicomp import MultiComparison
from itertools import combinations

from dj import DJ
from Statistics import statistics

if __name__ == "__main__":

    infile = 'DJ_results.csv'

    df = pd.read_csv(infile)


    grouped = df.groupby(["Style", "Subject"])
    #Group by ["Style", "Subject"]
    mean = grouped.agg(np.mean)
    # Description stats
    # mean_stl = mean.mean(axis=0, level=0)
    # std_stl = mean.std(axis=0, level=0)
    # print(mean)
    # print(mean.index.get_level_values(0))
    for style in np.unique([name[0] for name, group in grouped]):
        # print(mean.loc['SF', 'Trial'])
        print(style)
        print('1st landing high-low GRF t-test')
        # print(f"High {round(mean_stl.loc[style, 'GRF_1st_high_(Normalized)'], 5)}  Low {round(mean_stl.loc[style, 'GRF_1st_low_(Normalized)'], 5)}")
        print(stats.ttest_rel(mean.loc[style, 'GRF_1st_high_(Normalized)'], mean.loc[style, 'GRF_1st_low_(Normalized)']))
        print('2nd landing high-low GRF t-test')
        # print(f"High {round(mean_stl.loc[style, 'GRF_2nd_high_(Normalized)'], 5)}  Low {round(mean_stl.loc[style, 'GRF_2nd_low_(Normalized)'], 5)}")
        print(stats.ttest_rel(mean.loc[style, 'GRF_2nd_high_(Normalized)'], mean.loc[style, 'GRF_2nd_low_(Normalized)']))
        print('1st landing high-low impulse t-test')
        # print(f"High {round(mean_stl.loc[style, 'GRF_2nd_high_(Normalized)'], 5)}  Low {round(mean_stl.loc[style, 'GRF_2nd_low_(Normalized)'], 5)}")
        print(stats.ttest_rel(mean.loc[style, 'Impulse_high_(Normalized)'], mean.loc[style, 'Impulse_low_(Normalized)']))

    print()

    # Paired samples t-test between 1st and 2nd landing
    for style in ['SF', 'SS', 'ST']:
        print('Paired samples t-test between 1st and 2nd landing')
        print(style)
        print('GRF_Max')
        print(stats.ttest_rel(mean.loc[style, 'GRF_Max_(Normalized)'], mean.loc[style, 'GRF_Max_2_(Normalized)']))
        print('GRF_Max_diff')
        print(stats.ttest_rel(mean.loc[style, 'Max_GRF_diff_1st_(Normalized)'], mean.loc[style, 'Max_GRF_diff_2nd_(Normalized)']))

    # var_list = df.columns[3:]
    var_list = ['Jump_Height_(Impulse)', 'GRF_Max_(Normalized)', 'GRF_Max_2_(Normalized)', \
                'GRF_1st_high_(Normalized)', 'GRF_1st_low_(Normalized)', \
                'GRF_2nd_high_(Normalized)', 'GRF_2nd_low_(Normalized)', \
                'Max_GRF_diff_1st_(Normalized)', 'Max_GRF_diff_2nd_(Normalized)', \
                'Impulse_high_(Normalized)', 'Impulse_low_(Normalized)']

    # RepANOVA among styles and description statistics
    df_stats = pd.DataFrame(columns=['Parameter', 'SF_mean', 'SF_std', 'SS_mean', 'SS_std','ST_mean', 'ST_std'])
    for item in var_list:
        # if item == 'Jump_Height_(Impulse)':
        dict = statistics.dscrpStats(df, item, 'Subject', ['Style'])
        df_stats = df_stats.append(dict, ignore_index=True)
        # statistics.anova_rm(df, item, 'Subject', ['Style'], aggregate_func='mean')
        # MultiComp = MultiComparison(mean[item], mean.index.get_level_values(0))
        # comp = MultiComp.allpairtest(stats.ttest_rel, method='Holm')
        # print (comp[0])

    df_stats.to_csv('Stats.csv', index=False)



    # # 2-way repeated measure ANOVA
    id_list = ['Subject', 'Style', 'Trial']
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(df.melt(id_vars=id_list, var_name="Landing", value_name="Max_GRF_diff_(Normalized", value_vars=['Max_GRF_diff_1st_(Normalized)', 'Max_GRF_diff_2nd_(Normalized)']))
    df_total = df.melt(id_vars=id_list, var_name="Landing", value_name="Max_GRF_total_(Normalized)", value_vars=['GRF_Max_(Normalized)', 'GRF_Max_2_(Normalized)'])
    df_total.replace({'Landing': {'GRF_Max_(Normalized)': '1st', 'GRF_Max_2_(Normalized)': '2nd'}}, inplace=True)
    # df_total.set_index(id_list)
    df_diff = df.melt(id_vars=id_list, var_name="Landing", value_name="Max_GRF_diff_(Normalized)", value_vars=['Max_GRF_diff_1st_(Normalized)', 'Max_GRF_diff_2nd_(Normalized)'])
    df_diff.replace({'Landing': {'Max_GRF_diff_1st_(Normalized)': '1st', 'Max_GRF_diff_2nd_(Normalized)': '2nd'}}, inplace=True)
    # df_diff.set_index(['Subject', 'Style', 'Trial', 'Landing'])
    df = pd.concat([df_total, df_diff], axis=1, join='inner')
    df = df.loc[:,~df.columns.duplicated()]
    # df.reset_index
    print(df.columns)
    df['Style_Landing'] = df['Style'] + '_' + df['Landing']
    for index, row in df.iterrows():
        if row.isnull().values.any() == True:
            print(row)
    # input()
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(df)
    # input()
    # statistics.anova_rm(df, 'Max_GRF_diff_(Normalized)', 'Subject', within=['Style', 'Landing'], aggregate_func='mean')

    comp_list = ["Max_GRF_total_(Normalized)", 'Max_GRF_diff_(Normalized)']
    # 2-way RepANOVA using pingouin (including post hoc) & pyvttbl
    # print(df)
    for item in comp_list:
        print(item)
        # pingouin
        # Compute the 2-way repeated measures ANOVA. This will return a dataframe.
        # 'Style', 'Landing'
        aov = pg.rm_anova(dv=item, within=['Style', 'Landing'], subject='Subject', data=df)
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(aov.round(3))
        # # Optional post-hoc tests
        # # 'Style', 'Landing'
        # posthocs = pg.pairwise_ttests(dv=item, within=['Style', 'Landing'], subject='Subject', data=df, padjust='holm', within_first='False')
        # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        #     print(posthocs.round(3))
        # # 'Landing', 'Style'
        # posthocs = pg.pairwise_ttests(dv=item, within=['Landing', 'Style'], subject='Subject', data=df, padjust='holm', within_first='False')
        # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        #     print(posthocs.round(3))
        # Multiple comparison
        df_multicomp = pd.DataFrame(columns=['A', 'B', 'P', 'Reject', 'P_corr'])
        combo = combinations(df['Style'].unique(), 2)
        for pair in combo:
            p_temp = stats.ttest_rel(df[df['Style'] == pair[0]][item], df[df['Style'] == pair[1]][item]).pvalue
            if pd.isna(p_temp) == True:
                print(pair[0])
                print(df[df['Style'] == pair[0]][item])
                print(pair[1])
                print(df[df['Style'] == pair[1]][item])
            df_multicomp.loc[len(df_multicomp)] = list(pair) + [p_temp, None, None]
        combo = combinations(df['Landing'].unique(), 2)
        for pair in combo:
            p_temp = stats.ttest_rel(df[df['Landing'] == pair[0]][item], df[df['Landing'] == pair[1]][item]).pvalue
            if pd.isna(p_temp) == True:
                print(pair[0])
                print(df[df['Style'] == pair[0]][item])
                print(pair[1])
                print(df[df['Style'] == pair[1]][item])
            df_multicomp.loc[len(df_multicomp)] = list(pair) + [p_temp, None, None]
        combo = combinations(df['Style_Landing'].unique(), 2)
        for pair in combo:
            p_temp = stats.ttest_rel(df[df['Style_Landing'] == pair[0]][item], df[df['Style_Landing'] == pair[1]][item]).pvalue
            if pd.isna(p_temp) == True:
                print(pair[0])
                print(df[df['Style'] == pair[0]][item])
                print(pair[1])
                print(df[df['Style'] == pair[1]][item])
            df_multicomp.loc[len(df_multicomp)] = list(pair) + [p_temp, None, None]
            
        reject, pvals_corr = pg.multicomp(df_multicomp['P'].tolist(), method='holm')
        df_multicomp['Reject'] = reject
        df_multicomp['P_corr'] = pvals_corr
        print(df_multicomp.round(3))

        # # pyvttbl
        # aov = df.anova('item', sub='Subject', wfactors=['Style', 'Landing'])
        # print(aov)


    # # Holm-Bonferroni Method (Post hoc)
    # # print(df)
    # for item in comp_list:
    #     print(item)
    #     MultiComp = MultiComparison(df[item], df['Style_Landing'])
    #     comp = MultiComp.allpairtest(stats.ttest_rel, method='Holm')
    #     print(comp[0])
