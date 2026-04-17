import os
import numpy as np
import pandas as pd
from itertools import combinations
from statsmodels.stats.anova import AnovaRM
from scipy import stats
from math import sqrt
import matplotlib.pyplot as plt

class statistics:
    """Statistics"""

    @classmethod
    def anova_rm(cls, data, depvar, subject, within=None, between=None, aggregate_func=None):
        aovrm = AnovaRM(data, depvar, subject, within, between=None, aggregate_func=aggregate_func)
        res = aovrm.fit()

        print(res)

    # @classmethod
    # def t_test(cls, data, depvar=None, subject=None, within=None, between=None, aggregate_func=None):


    @classmethod
    def Bonferroni(cls, data, depvar=None, subject=None, within=None, between=None, aggregate_func=None):
        alpha = 0.05 / 2 / 3
        print('Post-hoc Bonferroni analyses')
        print(depvar)

        # data.sort_values(['Style', 'Subject', 'Trial'], inplace=True)

        grouped = data.groupby(within + [subject])
        #Group by ["Style", "Subject"]
        mean = grouped.agg(np.mean)

        # print(np.unique([name[0] for name, group in grouped]))

        str = ''
        for combo in combinations(np.unique([name[0] for name, group in grouped]), 2):  # 2 for pairs, 3 for triplets, etc
            # print(combo)
            cndt1 = combo[0]
            mean1 = np.mean(mean.loc[combo[0], depvar])
            std1 = np.std(mean.loc[combo[0], depvar], ddof=1)
            cndt2 = combo[1]
            mean2 = np.mean(mean.loc[combo[1], depvar])
            std2 = np.std(mean.loc[combo[1], depvar], ddof=1)

            print(f"{cndt1} {round(mean1, 5)}({round(std1, 5)})  {cndt2} {round(mean2, 5)}({round(std2, 5)})")

            print(stats.ttest_rel(mean.loc[combo[0], depvar], mean.loc[combo[1], depvar]))

            t_score, p_value = stats.ttest_rel(mean.loc[combo[0], depvar], mean.loc[combo[1], depvar])
            # print(p_value)

            if p_value < alpha:
                # print(combo)
                if str != '':
                    str = str + ', (' + combo[0] + ', ' + combo[1] + ')'
                else:
                    str = '(' + combo[0] + ', ' + combo[1] + ')'

        return str

    @classmethod
    def dscrpStats(cls, data, depvar=None, subject=None, within=None, between=None, aggregate_func=None):
        grouped = data.groupby(within + [subject])
        mean = grouped.agg(np.mean)

        dict = {'Parameter': depvar}

        for item in np.unique([name[0] for name, group in grouped]):
            dict[item+'_mean'] = np.mean(mean.loc[item, depvar])
            dict[item+'_std'] = np.std(mean.loc[item, depvar], ddof=1)
            shapiro_test = stats.shapiro(mean.loc[item, depvar])
            # print(shapiro_test)
            dict[item+'_shapiro'] = shapiro_test.pvalue

        # print(dict)
        return dict

    # function to calculate Cohen's d for independent samples
    @classmethod
    def cohend(cls, d1, d2):
        # calculate the size of samples
        n1, n2 = len(d1), len(d2)
        # calculate the variance of the samples
        s1, s2 = np.var(d1, ddof=1), np.var(d2, ddof=1)
        # calculate the pooled standard deviation
        s = sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))
        # calculate the means of the samples
        u1, u2 = np.mean(d1), np.mean(d2)
        # calculate the effect size
        return (u1 - u2) / s

    @classmethod
    def effect_size(cls, data, depvar=None, subject=None, within=None, between=None, aggregate_func=None):
        grouped = data.groupby(within + [subject])
        mean = grouped.agg(np.mean)

        pair_tuple = (['SF','SS'], ['SS','ST'], ['SF','ST'])

        dict = {'Parameter': depvar}

        for pair in pair_tuple:
            dict[pair[0] + ',' + pair[1]] = statistics.cohend(mean.loc[pair[1], depvar], mean.loc[pair[0], depvar])

        # print(dict)
        return dict

    @classmethod
    def bar_effect(cls, df, label, pair):
        var_tuple = ('Stiffness', 'Contact_Time', 'Depth', 'Jump_Height_(Impulse)', 'GRF_Max_(Normalized)', \
                     'GRF_at_Bottom_(Normalized)', 'Average_Power_(Normalized)', 'Peak_Power_(Normalized)', \
                     'RSI_(Impulse)')
        df = df[df[label].isin(var_tuple)]
        # df.reindex(index=df.index[::-1])
        df_plot = pd.DataFrame()
        for item in var_tuple:
            df_plot = df_plot.append(df[df[label] == item])

        # x = np.arange(len(var_tuple))
        x = np.arange(start=len(var_tuple) - 1, stop=-1, step=-1)
        y1 = df_plot[pair[0]]
        print(y1)
        y2 = df_plot[pair[1]]
        y3 = df_plot[pair[2]]
        width = 0.2

        # plt.figure(dpi=1200)
        plt.rcParams["figure.figsize"] = (8, 6)
        plt.xlim(-4,4)

        # plt.bar(x-width, y1, width)
        # plt.bar(x, y2, width)
        # plt.bar(x+width, y3, width)
        plt.axvline(x=0, color='k', linestyle='-', linewidth=1)
        # plt.axvline(x=-0.5, color='k', linestyle=':', linewidth=0.5)
        # plt.axvline(x=0.5, color='k', linestyle=':', linewidth=0.5)
        # plt.axvline(x=-0.8, color='k', linestyle=':', linewidth=0.5)
        # plt.axvline(x=0.8, color='k', linestyle=':', linewidth=0.5)
        # plt.axvline(x=-0.5, color='k', linestyle=':', linewidth=0.5)
        # plt.axvline(x=0.5, color='k', linestyle=':', linewidth=0.5)
        plt.axvspan(0, 0.2, facecolor='oldlace', label='Trivial')
        plt.axvspan(0.2, 0.5, facecolor='papayawhip', label='Small')
        plt.axvspan(0.5, 0.8, facecolor='navajowhite', label='Moderate')
        plt.axvspan(0.8, 4, facecolor='burlywood', label='Large')
        plt.axvspan(0, -0.2, facecolor='oldlace')
        plt.axvspan(-0.2, -0.5, facecolor='papayawhip')
        plt.axvspan(-0.5, -0.8, facecolor='navajowhite')
        plt.axvspan(-0.8, -4, facecolor='burlywood')

        plt.barh(x+width, y1, width, label='ES (' + pair[0] + ')')
        plt.barh(x, y2, width, label='ES (' + pair[1] + ')')
        plt.barh(x-width, y3, width, label='ES (' + pair[2] + ')')

        plt.xlabel('ES', fontweight='bold')
        # plt.set_xticks(x)
        # plt.set_xticklabels(df[label])
        # plt.xticks(x, df[label])
        plt.xticks(np.arange(-4, 5, 1))
        # plt.yticks(x, var_tuple)
        plt.tick_params(
            axis='y',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            left=False,        # ticks along the left edge are off
            labelleft=False) # labels along the bottom edge are off
        plt.legend(framealpha=1)

        # plt.show()
        plt.savefig('Plot/effect_size.png')
        plt.close()

    @classmethod
    def bar_plot(cls, dict, ylabel):
        labels = ['SF', 'SS', 'ST']
        cmap = ['dimgrey', 'lightgrey', 'k']

        x = np.arange(len(labels))
        y = [dict['SF_mean'], dict['SS_mean'], dict['ST_mean']]
        yerr_upper = [dict['SF_std'], dict['SS_std'], dict['ST_std']]
        yerr_lower = np.zeros(len(yerr_upper))

        fig, ax = plt.subplots()
        ax.bar(x, y, width=0.8, color=cmap, edgecolor='k', yerr=[yerr_lower, yerr_upper], capsize=10)

        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=16)
        ax.set_ylabel(ylabel, fontsize=16, fontweight='bold')
        plt.rcParams.update({'font.size': 16})
        # ax.set_title(dict['Parameter'], {'fontweight': 'bold','verticalalignment': 'top'})
        plt.margins(y=0.1, tight=False)

        txt = cls.Bonferroni(df, dict['Parameter'], 'Subject', ['Style'])
        # ax.text(0.5, 0.95, txt, horizontalalignment='center', verticalalignment='center', transform = ax.transAxes, fontsize=20)

        #Custome function to draw significance label
        def label_sig(i, text, X, Y, Yerr):
            x = X[i]
            y = 1.02*(Y[i] + Yerr[i])

            ax.annotate(text, xy=(x,y))

        if txt == "(SF, SS)":
            label_sig(1, u"\u2020", x, y, yerr_upper)
        elif txt == "(SF, SS), (SF, ST)":
            label_sig(1, u"\u2020", x, y, yerr_upper)
            label_sig(2, u"\u2020", x, y, yerr_upper)
        elif txt == "(SF, SS), (SF, ST), (SS, ST)":
            label_sig(1, u"\u2020", x, y, yerr_upper)
            label_sig(2, u"\u2020,\u2021", x, y, yerr_upper)
        elif txt == "(SS, ST)":
            label_sig(2, u"\u2021", x, y, yerr_upper)
        else:
            pass

        plt.savefig('Plot/' + dict['Parameter'] + '.png')
        plt.close()




if __name__ == "__main__":

    infile = 'DJ_results.csv'

    df = pd.read_csv(infile)

    folder = 'Plot/'
    for the_file in os.listdir(folder):
        try:
            os.unlink(folder + the_file)
            # elif os.path.isdir(file_path): shutil.rmtree(file_path)
            # print(the_file)
        except Exception as e:
            print(e)

    var_list = df.columns[3:]
    # print(var_list)
    # input()

    ylabel_dict = {
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
        'Time_GRF_Ecc_Max': 'Time(s)',
        'Time_GRF_Con_Max': 'Time(s)',
        'RSI_(Impulse)': 'RSI(m/s)',
        'RSI_(Flight)': 'RSI(m/s)',
        'Stiffness': 'Stiffness(N/m)'
    }

    df_stats = pd.DataFrame(columns=['Parameter', 'SF_mean', 'SF_std', 'SF_shapiro', \
                                     'SS_mean', 'SS_std', 'SS_shapiro','ST_mean', 'ST_std', 'ST_shapiro'])
    #Processing 1 parameter at a time
    # print(var_list)
    for item in var_list:
        if item in ylabel_dict:
            pass
        else:
            # print(item)
            continue

        # if item == 'Jump_Height_(Impulse)':
        dict = statistics.dscrpStats(df, item, 'Subject', ['Style'])
        df_stats = df_stats.append(dict, ignore_index=True)
        statistics.anova_rm(df, item, 'Subject', ['Style'], aggregate_func='mean')

        statistics.bar_plot(dict, ylabel_dict[item])

    df_stats.to_csv('Stats.csv', index=False)

    #Calculate effect size
    df_effect = pd.DataFrame(columns=['Parameter', 'SF,SS', 'SS,ST', 'SF,ST'])

    for item in var_list:
        if item in ylabel_dict:
            pass
        else:
            # print(item)
            continue

        dict = statistics.effect_size(df, item, 'Subject', ['Style'])
        df_effect = df_effect.append(dict, ignore_index=True)

    df_effect.to_csv('Effect_Size.csv', index=False)
    statistics.bar_effect(df_effect, 'Parameter', ['SF,SS', 'SS,ST', 'SF,ST'])


    # var_list = df.columns[3:]

    #
    # for item in var_list:
    #     print(item)
    #     statistics.anova_rm(df, item, 'Subject', ['Style'], aggregate_func='mean')
    #     statistics.Bonferroni(df, item, 'Subject', ['Style'])