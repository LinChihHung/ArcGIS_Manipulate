from GIS.GIScalculate import GISControl
from GIS.GISplot import PlotFig
import os
import pandas as pd

def main():
    
    path = r'C:\Users\heteng\Desktop\桃園\通盤檢討修正_1100201\CSV'

    os.chdir(r'C:\Users\heteng\Desktop\桃園\通盤檢討修正_1100201')

    profileName = '剖面線.shp'
    hilltopName = '坡頂線.shp'
    drawoutName = '劃出範圍修正_1091221.shp'
    contourName = '95年以前等高線_clip範圍.shp'

    rasterName = 'dem_5m.tif'


    GIS_Error = []
    Plot_Error = []

    for i in range(34):
        try:
            print(i)
            GIS = GISControl(
                profileName=profileName, hilltopName=hilltopName, 
                contourName=contourName, drawoutName=drawoutName, 
                rasterName=rasterName,
                num=4, status='origin'
                )
                    
            finalDataFrame = GIS.finalDataFrame
            name = GIS.name
            proDrawoutCoords = GIS.proDrawoutCoords
            proHilltopCoords = GIS.proHilltopCoords
            hilltopIndex = GIS.hilltopIndex
            print(name)
            print(i)
            print('--------------------------------------------------------------------------------------')
            finalDataFrame.to_csv(path + os.sep + f'{name}.csv', index=None, encoding='utf_8_sig')

        except:
            print(i)
            print(f"Error!!! Profile number {i} has two same contour")
            GIS_Error.append(i)
        

        image = PlotFig(
            finalDataFrame=finalDataFrame, name=name,  
            proDrawoutCoords=proDrawoutCoords, proHilltopCoords=proHilltopCoords,
            hilltopIndex=hilltopIndex
            )
            
    print('GIS Error: ', GIS_Error)
    print('Plot_Error: ', Plot_Error)
    # finalDataFrame = pd.read_csv(r'C:\Users\heteng\Desktop\龜山1-3\CSV\龜山-1-1-80_New.csv')
    # name = '龜山1-3'
    # proDrawoutCoords = finalDataFrame['coordinates'].iloc[4]
    # proHilltopCoords = finalDataFrame['coordinates'].iloc[3]
    # hilltopIndex = 3

    # image = PlotFig(
    # finalDataFrame=finalDataFrame, name=name,  
    # proDrawoutCoords=proDrawoutCoords, proHilltopCoords=proHilltopCoords,
    # hilltopIndex=hilltopIndex
    # )

    
if __name__ == '__main__':
    main()