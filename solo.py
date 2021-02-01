from GIS.GIScalculate import GISControl
from GIS.GISplot import PlotFig
import os
import pandas as pd
    
finalDataFrame = pd.read_csv(r'C:\Users\heteng\Desktop\龜山1-3\CSV\龜山-1-1-80_New.csv')

name = '龜山1-3'
hilltopIndex = finalDataFrame[finalDataFrame['remarks'] == '坡頂線'].index.values[0]
proHilltopCoords = finalDataFrame['coordinates'][hilltopIndex]
proDrawoutCoords = finalDataFrame['remarks']

image = PlotFig(
finalDataFrame=finalDataFrame, name=name,  
proDrawoutCoords=proDrawoutCoords, proHilltopCoords=proHilltopCoords,
hilltopIndex=hilltopIndex
)