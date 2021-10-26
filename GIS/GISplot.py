import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as patches
import numpy as np
import six

class PlotFig():

    def __init__(
        self, finalDataFrame, plotDataFrame, name,
        proDrawoutCoords, proHilltopCoords, hilltopIndex, 
        base=20, divisor=4
        ):
        self.finalDataFrame = finalDataFrame
        self.plotDataFrame = plotDataFrame
        self.name = name

        self.proDrawoutCoords = proDrawoutCoords
        self.proHilltopCoords = proHilltopCoords
        self.hilltopIndex = hilltopIndex
        self.base = base
        self.divisor = divisor

        self.distance = self.finalDataFrame['distanceSum']
        self.elevation = self.finalDataFrame['elevation']
        self.slope = self.finalDataFrame['slopeDegree']
        # print(self.distance)

        self.hilltopX = None
        self.drawoutX = None
        self.withdrawX = None
        self.vline()

        # self.legalWithdraw = round((self.withdrawX - self.hilltopX), 1)
        self.legalWithdraw = round(max(self.finalDataFrame['withdrawSum']), 1) #法定退縮距離
        self.actualWithdraw = round((self.drawoutX - self.hilltopX), 1) #實際退縮距離

        self.hilldef()
        self.mainplot()


    def hilldef(self):
        if self.elevation.iloc[0] < self.elevation.iloc[-1]:
            # ascending
            self.hillType = 'ascending'
        if self.elevation.iloc[0] > self.elevation.iloc[-1]:
            # descending
            self.hillType = 'descending'


    def vline(self):
        
        self.hilltopX = self.finalDataFrame.loc[self.finalDataFrame['coordinates'] == self.proHilltopCoords]['distanceSum'].values[0]
        self.drawoutX = self.finalDataFrame.loc[self.finalDataFrame['coordinates'] == self.proDrawoutCoords]['distanceSum'].values[0]
        self.withdrawX = self.hilltopX + max(self.finalDataFrame['withdrawSum'])


    def mainplot(self):

        # Some Basic Setup
        # size, set ax3 height
        col_width=3.0
        row_height=0.625
        size = ((np.array(self.plotDataFrame.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height]))[1]
        fig, (ax, ax2, ax3) = plt.subplots(3, 1, figsize=(21, 10+size), gridspec_kw={'height_ratios': [9, 1, size]})
        plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
        plt.rcParams['xtick.labelsize'] = 18
        plt.rcParams['ytick.labelsize'] = 18
        ax.minorticks_on()

        # plot hillside
        ax.plot(self.distance, self.elevation, linewidth=3)
        
        # vertical line
        ax.axvline(x=self.hilltopX, linestyle='--', linewidth=3, color='tab:orange', label='退縮起點')
        ax.axvline(x=self.withdrawX, linestyle='--', linewidth=3, color='tab:green', label='退縮終點')
        ax.axvline(x=self.drawoutX, linestyle='--', linewidth=3, color='tab:brown', label='建議劃出範圍')
        
        
        # settings
        ax.set_title(f'{self.name} 地形剖面之退縮距離計算', fontsize=28)
        ax.set_xlabel('水平距離 (m)', fontsize=24)
        ax.set_ylabel('高程 (m)', fontsize=24)
        ymin = np.floor(min(self.elevation)) - 15
        ymax = np.ceil(max(self.elevation)) + 15
        ax.set_xlim([0, self.distance.iloc[-1]])
        ax.set_ylim([ymin, ymax])
        
        # Set major and minor grid lines on X
        ax.xaxis.set_major_locator(mticker.MultipleLocator(base=self.base))
        ax.xaxis.set_minor_locator(mticker.MultipleLocator(base=self.base / self.divisor))

        ax.yaxis.set_major_locator(mticker.MultipleLocator(base=self.base))
        ax.yaxis.set_minor_locator(mticker.MultipleLocator(base=self.base / self.divisor))

        ax.grid(ls='-', color='grey', linewidth=1, alpha=0.8)
        ax.grid(which="minor", ls=':', color='grey', linewidth=0.5, alpha=0.5)


        # 圖軸上的圖例箭頭與文字
        # 如果山坡地的形式為遞增上去的
        # 圖例置於左上角
        # 箭頭與文字自ymin開始起算
        if self.hillType == 'ascending':
            # 圖例
            legend = ax.legend(loc='upper left', fontsize=16)
            legend.set_title('D1 : 法定退縮距離 (m) \nD2 : 實際退縮距離 (m)', prop={'size': 16})
            legend._legend_box.align = "left"
            # 1. 法定退縮距離的箭頭與文字
            # (1) 法定退縮距離的箭頭
            ax.annotate(
                text='', 
                xy=(self.hilltopX, ymin+13), 
                xytext=(self.withdrawX, ymin+13), 
                arrowprops=dict(facecolor='black', arrowstyle='<|-|>'), va='center', fontsize=16)
            # (2) 法定退縮距離的文字
            ax.annotate(
                text=f'D1 : {self.legalWithdraw} m', 
                xy=(self.hilltopX, ymin+15), 
                va='center', fontsize=16, weight='bold')
            
            # 2. 實際退縮距離的箭頭與文字
            # (1) 實際退縮距離的箭頭
            ax.annotate(
                text='', 
                xy=(self.hilltopX, ymin+5), 
                xytext=(self.drawoutX, ymin+5), 
                arrowprops=dict(facecolor='black', arrowstyle='<|-|>'), va='center', fontsize=16)
            # (2) 實際退縮距離的文字
            ax.annotate(
                text=f'D2 : {self.actualWithdraw} m', 
                xy=(self.hilltopX, ymin+8), 
                va='center', fontsize=16, weight='bold')
            
            # 3. 坡長的箭頭與文字
            for i in range(1, self.hilltopIndex):
                ax.annotate(
                    text='',
                    xy=(self.distance[i], ymin+5),
                    xytext=(self.distance[i+1], ymin+5),
                    arrowprops=dict(facecolor='black', arrowstyle='<|-|>'), va='center', fontsize=16)
                center = (self.distance[i] + self.distance[i+1])/2
                # ax.text(center, ymin+8, r'$\circ$', fontsize=60)
                ax.annotate(
                    text=f'S{i}', 
                    xy=(center, ymin+8), 
                    va='center', ha='center', fontsize=16, weight='bold')
        # 如果山坡地的形式為遞減下去的
        # 圖例置於左下角
        # 箭頭與文字自ymmax開始起算       
        if self.hillType == 'descending':
            # 圖例
            ax.legend(loc='lower left', fontsize=16)
            legend.set_title('D1 : 法定退縮距離 (m) \nD2 : 實際退縮距離 (m)', prop={'size': 16})
            legend._legend_box.align = "left"            
            # 1. 法定退縮距離的箭頭與文字
            # (1) 法定退縮距離的箭頭
            ax.annotate(
                text='', 
                xy=(self.hilltopX, ymax-10), 
                xytext=(self.withdrawX, ymax-10), 
                arrowprops=dict(facecolor='black', arrowstyle='<|-|>'), va='center', fontsize=16)
            # (2) 法定退縮距離的文字
            ax.annotate(
                text=f'D1 : {self.legalWithdraw} m', 
                xy=(self.hilltopX, ymax-13), 
                va='center', fontsize=16, weight='bold')
            
            # 2. 實際退縮距離的箭頭與文字
            # (1) 實際退縮距離的箭頭
            ax.annotate(
                text='', 
                xy=(self.hilltopX, ymax-18), 
                xytext=(self.drawoutX, ymax-18), 
                arrowprops=dict(facecolor='black', arrowstyle='<|-|>'), va='center', fontsize=16)
            # (2) 實際退縮距離的文字
            ax.annotate(
                text=f'D2 : {self.actualWithdraw} m', 
                xy=(self.hilltopX, ymax-21), 
                va='center', fontsize=16, weight='bold')
            
            # 3. 坡長的箭頭與文字
            for i in range(1, self.hilltopIndex):
                ax.annotate(
                    text='',
                    xy=(self.distance[i], ymax-10),
                    xytext=(self.distance[i+1], ymax-10),
                    arrowprops=dict(facecolor='black', arrowstyle='<|-|>'), va='center', fontsize=16)
                center = (self.distance[i] + self.distance[i+1])/2
                # ax.text(center, ymin+8, r'$\circ$', fontsize=60)
                ax.annotate(
                    text=f'S{i}', 
                    xy=(center, ymax-13), 
                    va='center', ha='center', fontsize=16, weight='bold')

        # 坡度的標示以及弧度
        for i in range(len(self.slope)-1):
            if i == 0:
                # mode = 'pass'
                if self.elevation.iloc[i] < self.elevation.iloc[i+1]:
                    mode = 'rise'
                if self.elevation.iloc[i] > self.elevation.iloc[i+1]:
                    mode = 'pass'
                if self.elevation.iloc[i] == self.elevation.iloc[i+1]:
                    mode = 'pass'
            elif self.elevation.iloc[i] > self.elevation.iloc[i+1] and self.elevation.iloc[i] > self.elevation.iloc[i-1]:
                mode = 'peak'
            elif self.elevation.iloc[i] < self.elevation.iloc[i+1] and self.elevation.iloc[i] < self.elevation.iloc[i-1]:
                mode = 'valley'
            elif self.elevation.iloc[i] < self.elevation.iloc[i-1]:
                mode = 'drop'
            elif self.elevation.iloc[i] < self.elevation.iloc[i+1]:
                mode = 'rise'
            elif self.elevation.iloc[i] == self.elevation.iloc[i+1] or self.elevation.iloc[i] == self.elevation.iloc[i-1]:
                mode = 'pass'
            elif i == len(self.slope)-2:
                if self.elevation.iloc[i] > 15:
                    mode = 'pass'
                elif self.elevation.iloc[i] < self.elevation.iloc[i-1]:
                    mode = 'drop'
                elif self.elevation.iloc[i] > self.elevation.iloc[i-1]:
                    mode = 'rise'
            else:
                raise ValueError


            if mode == 'rise' or mode == 'valley':
                slopeValue = np.floor(self.finalDataFrame['slopeDegree'][i+1])
                if slopeValue == 0:
                    pass
                else:
                    ax.annotate(
                        text='', 
                        xy=(self.finalDataFrame['distanceSum'][i], self.finalDataFrame['elevation'][i]), 
                        xytext=(self.finalDataFrame['distanceSum'][i]+5, self.finalDataFrame['elevation'][i]), 
                        arrowprops=dict(facecolor='black', arrowstyle='-'), 
                        va='center', ha='center', fontsize=24)
                    ax.annotate(
                        text=f"{np.floor(self.finalDataFrame['slopeDegree'][i+1]):.0f}$^\circ$", 
                        xy=(self.finalDataFrame['distanceSum'][i]+10, self.finalDataFrame['elevation'][i]),
                        va='center', ha='center', fontsize=16)
                    ax.add_patch(
                        patches.Wedge(
                            (self.finalDataFrame['distanceSum'][i], self.finalDataFrame['elevation'][i]),         # (x,y)
                            r=4,            # radius
                            theta1=0,             # theta1 (in degrees)
                            theta2=self.finalDataFrame['slopeDegree'][i+1],            # theta2
                            color='k', fill=False)
                            )
            if mode == 'drop' or mode == 'valley':
                slopeValue = np.floor(self.finalDataFrame['slopeDegree'][i])
                if slopeValue == 0:
                    pass
                else:
                    ax.annotate(
                        text='', 
                        xy=(self.finalDataFrame['distanceSum'][i], self.finalDataFrame['elevation'][i]), 
                        xytext=(self.finalDataFrame['distanceSum'][i]-5, self.finalDataFrame['elevation'][i]), 
                        arrowprops=dict(facecolor='black', arrowstyle='-'), 
                        va='center', ha='center', fontsize=24)
                    ax.annotate(
                        text=f"{np.floor(self.finalDataFrame['slopeDegree'][i]):.0f}$^\circ$", 
                        xy=(self.finalDataFrame['distanceSum'][i]-10, self.finalDataFrame['elevation'][i]),
                        va='center', ha='center', fontsize=16)
                    ax.add_patch(
                        patches.Wedge(
                            (self.finalDataFrame['distanceSum'][i], self.finalDataFrame['elevation'][i]),   # (x,y)
                            r=4,    # radius
                            theta1=180-self.finalDataFrame['slopeDegree'][i],   # theta1 (in degrees)
                            theta2=180,     # theta2
                            color='k', fill=False)
                            )
            if mode == 'peak' or mode == 'pass':
                pass

        #### ax2, 實際退縮距離大於法定退縮文字 ###
        txt = f'實際退縮距離 {self.actualWithdraw} m $\geq$ 法定退縮距離 {self.legalWithdraw} m'
        ax2.text(0.5, 0.5, txt, horizontalalignment='center', verticalalignment='center', transform=ax2.transAxes, fontsize=36)
        ax2.axis('off')


        #### ax3, table ###
        header_color='#40466e'
        row_colors=['#f1f1f2', 'w']
        edge_color='k'
        bbox=[0, 0, 1, 1]
        header_columns=0        
        
        table = ax3.table(cellText=self.plotDataFrame.values, bbox=bbox, colLabels=self.plotDataFrame.columns, loc ='center')
        table.set_fontsize(36)
        for k, cell in  six.iteritems(table._cells):
            cell.set_edgecolor(edge_color)
            cell.set_text_props(ha='center')
            cell.set_text_props(va='center_baseline')
            if k[0] == 0 or k[1] < header_columns:
                cell.set_text_props(weight='bold', color='w')
                cell.set_facecolor(header_color)
            else:
                cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
        ax3.axis('off')

        ax.set_aspect('equal', adjustable='box')
        fig.tight_layout()

        path = r'C:\Users\heteng\Desktop\桃園'
        plt.savefig(path + os.sep + f'{self.name}.jpg', dpi=300)


if __name__ == '__main__':
    pass