import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# import seaborn as sns
import scipy.stats as st
from math import sqrt
import time


class Timeplot:
    @classmethod
    def data_gen(cls, infile, t_label):
        """generate plot .csv data."""

        df = pd.read_csv(infile, header=0)
        df = df.loc[:, ['Style', t_label, \
                'GRF_1h_(Normalized)', 'GRF_1l_(Normalized)', 'GRF_2h_(Normalized)', 'GRF_2l_(Normalized)', \
                'GRF_(Normalized)', 'GRF_diff_(Normalized)', 'Impulse_1h_(Normalized)', 'Impulse_1l_(Normalized)', \
                'Velocity']]
        df.rename(columns={t_label: 'Time'}, inplace=True)
        # print(df.columns)
        # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        #     print(df['Time'])
        # input()

        # df_plot_1 = pd.DataFrame(columns=['Style', 'Time_C1', 'Mean_GRF_1', 'STD_GRF_1', 'CIUB_GRF_1', 'CILB_GRF_1', \
        #                                   'Mean_GRF_1h', 'STD_GRF_1h', 'CIUB_GRF_1h', 'CILB_GRF_1h', \
        #                                   'Mean_GRF_1l', 'STD_GRF_1l',  'CIUB_GRF_1l', 'CILB_GRF_1l'])
        # df_plot_2 = pd.DataFrame(columns=['Style', 'Time_C2', 'Mean_GRF_2', 'STD_GRF_2', 'CIUB_GRF_2', 'CILB_GRF_2', \
        #                                   'Mean_GRF_2h', 'STD_GRF_2h', 'CIUB_GRF_2h', 'CILB_GRF_2h', \
        #                                   'Mean_GRF_2l', 'STD_GRF_2l',  'CIUB_GRF_2l', 'CILB_GRF_2l'])

        z = st.norm.ppf(.95)

        grouped = df.groupby(['Style', 'Time'])
        aggregations = [np.mean, lambda x: z * np.std(x) / sqrt(len(x))]

        df_plot = grouped.agg(aggregations).rename(columns={'<lambda_0>': 'r_CI'})
        df_plot.to_csv('timeplot.csv', index=True)

        return df_plot


    @classmethod
    def plot(cls, df, item, start, end):
        linestyle_dict = {'SF': '--', 'SS': '-.', 'ST': ':'}
        # color_dict = {'SF': 'r', 'SS': 'g', 'ST': 'b'}
        color_dict = {'SF': 'k', 'SS': 'k', 'ST': 'k'}
        ylabel_dict = {
            'GRF_(Normalized)': '$vGRF_{total}$ (N/kg)',
            'GRF_diff_(Normalized)': '$vGRF_{diff}$ (N/kg)',
            'Velocity' : 'Velocity (m/s)'
        }

        plt.figure(dpi=1200)
        plt.rcParams["figure.figsize"] = (8, 6)
        params = {'mathtext.default': 'regular' }
        plt.rcParams.update(params)

        fig, axs = plt.subplots(len(item))
        for idx, val in enumerate(item):
            print(idx, val)
            for style in ['SF', 'SS', 'ST']:
                df_temp = df.loc[(style, start):(style, end)]
                df_temp.reset_index(level='Style', inplace=True)

                axs[idx].plot(df_temp.index, df_temp[val]['mean'], linestyle=linestyle_dict[style], color=color_dict[style], label=style)
                y1 = df_temp[val]['mean'] - df_temp[val]['r_CI']
                y2 = df_temp[val]['mean'] + df_temp[val]['r_CI']
                axs[idx].fill_between(df_temp.index, y1, y2, color=color_dict[style], alpha=0.1)
            # Label
            axs[idx].set_xlim(right=end)
            axs[idx].set_ylabel(ylabel_dict[val], fontsize='large', fontweight='bold')
            axs[idx].axhline(linewidth=1, linestyle=':', color='k')
            # Legend
            axs[idx].legend(loc='upper right', shadow=True, fontsize='large')
        # Put a nicer background color on the legend.
        # legend.get_frame().set_facecolor('#00FFCC')
        plt.xlabel('Time (ms)', fontsize='large', fontweight='bold')
        # plt.savefig('timeplot_initial_600.tiff', dpi=1200)
        # plt.show()
        return plt



if __name__ == "__main__":
    # start = time.time()

    csvfile = 'DJ_raw.csv'

    df_plot = Timeplot.data_gen(csvfile, 'Time_C1')
    plot_list = ['GRF_(Normalized)', 'GRF_diff_(Normalized)', 'Velocity']
    plot = Timeplot.plot(df_plot, plot_list, 0, 600)
    plot.savefig('/Users/Chinaeatshit/Documents/Texpad/LaTeX project/Asymmetry study/fig/timeplot_initial_600.tiff', dpi=1200)
    plot.savefig('/Users/Chinaeatshit/Documents/Texpad/LaTeX project/Asymmetry study/fig/timeplot_initial_600.png', dpi=1200)

    df_plot = Timeplot.data_gen(csvfile, 'Time_C2')
    plot_list = ['GRF_(Normalized)', 'GRF_diff_(Normalized)', 'Velocity']
    plot = Timeplot.plot(df_plot, plot_list, 0, 400)
    plot.savefig('/Users/Chinaeatshit/Documents/Texpad/LaTeX project/Asymmetry study/fig/timeplot_final_400.tiff', dpi=1200)
    plot.savefig('/Users/Chinaeatshit/Documents/Texpad/LaTeX project/Asymmetry study/fig/timeplot_final_400.png', dpi=1200)

    # end = time.time()
    # print(end - start)

    # # Trial plot maybe in dj
    # df = pd.read_csv(infile, header=0)
    #
    # fig, axes = plt.subplots(figsize=[20,5]) #nrows
    # plt.subplots_adjust(wspace=0.5, hspace=0.5)
    # df_plot = df[(df['Phase'] == 'Braking') | (df['Phase'] == 'Propulsion') | (df['Phase'] == 'Flight') | (df['Phase'] == 'Landing')]
    # df_plot = df_plot.set_index('Time_Mod')
    # df_plot.groupby('Phase')['Work_GRF'].plot(kind='line', ax=axes, subplots=False, legend=True, markersize=40)
    # axes.set_xlim(right=1.75)
    # axes.set_xlabel('Time (s)', fontsize=16, fontweight='bold')
    # axes.set_ylabel('Work (J)', fontsize=16, fontweight='bold')
    # axes.legend(fontsize=12)
    # # plt.rcParams.update({'xtick.labelsize':})
    # plt.xticks(fontsize=12)
    # plt.yticks(fontsize=12)
    # plt.savefig('Plot/SF/Work.png')

