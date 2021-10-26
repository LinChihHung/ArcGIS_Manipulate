from GIS.GIScalculate import GISControl
from GIS.GISplot import PlotFig
import os
import pandas as pd
import numpy as np

import os
os.chdir(r'C:\Users\heteng\Desktop\桃園') 
fileList = os.listdir()
csv = [i for i in fileList if i.endswith('.csv')]
for csvName in csv:
    finalDataFrame = pd.read_csv(csvName)

    coordinates = [0] + list(finalDataFrame['coordinates'])
    elevation = [list(finalDataFrame['elevation'])[0]] + list(finalDataFrame['elevation'])
    deltaEL = [0] + list(finalDataFrame['deltaEL'])
    distance = [0]+list(finalDataFrame['distance'])

    distanceSum = [0]+[i+10 for i in list(finalDataFrame['distanceSum'])]
    distanceSum[-1] = distanceSum[-2] + 10

    slope = [0] + list(finalDataFrame['slope'])
    slopeFactor = [0] + list(finalDataFrame['slopeFactor'])
    withdraw = [0] + list(finalDataFrame['withdraw'])
    withdrawSum = [0] + list(finalDataFrame['withdrawSum'])

    allDict = {
        'coordinates': coordinates, 'elevation': elevation, 'deltaEL': deltaEL,
        'distance':distance, 'distanceSum': distanceSum, 'slopeDegree': slope, 'slopeFactor': slopeFactor,
        'withdraw': withdraw, 'withdrawSum': withdrawSum
    }

    dataframe = pd.DataFrame(allDict, columns=[
        'coordinates', 'elevation', 'deltaEL', 
        'distance', 'distanceSum', 
        'slopeDegree', 'slopeFactor', 
        'withdraw', 'withdrawSum'])

    name = csvName.split('.')[0]
    hilltopIndex = np.flatnonzero(dataframe['slopeDegree'][0:-2].values > 15)[-1]
    proHilltopCoords = dataframe['coordinates'][hilltopIndex]
    proDrawoutCoords = finalDataFrame['coordinates'].iloc[-2]

    image = PlotFig(
    finalDataFrame=dataframe, name=name,  
    proDrawoutCoords=proDrawoutCoords, proHilltopCoords=proHilltopCoords,
    hilltopIndex=hilltopIndex
    )