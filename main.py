from GIS.GIScalculate import GISControl
from GIS.GISplot import PlotFig
import os
import pandas as pd

def main():
    
    path = r'C:\Users\heteng\Desktop\桃園\龜山\CSV'

    os.chdir(r'C:\Users\heteng\Desktop\桃園\龜山')

    profileName = '龜山剖面線0507.shp'
    hilltopName = '龜山坡頂_5.10.shp'
    drawoutName = '龜山劃出範圍_5.10.shp'
    contourName = '第五版大湖等高線.shp'

    rasterName = '龜山區.tif'


    GIS_Error = []
    Plot_Error = []

    for i in range(1, 2):
        try:
            print(i)
            GIS = GISControl(
                profileName=profileName, hilltopName=hilltopName, 
                contourName=contourName, drawoutName=drawoutName, 
                rasterName=rasterName,
                num=20, status='complex'
                )
                    
            finalDataFrame, plotDataFrame = GIS.finalDataFrame
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
            finalDataFrame=finalDataFrame, plotDataFrame=plotDataFrame, name=name,  
            proDrawoutCoords=proDrawoutCoords, proHilltopCoords=proHilltopCoords,
            hilltopIndex=hilltopIndex
            )
            
    print('GIS Error: ', GIS_Error)
    print('Plot_Error: ', Plot_Error)

    
if __name__ == '__main__':
    main()