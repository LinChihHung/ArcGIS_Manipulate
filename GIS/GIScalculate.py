import os
import geopandas as gpd
import rasterio
import pandas as pd
import math
import numpy as np
import pdb
import collections

class GISControl():
    def __init__(
        self,
        profileName, hilltopName, drawoutName, contourName, 
        rasterName, 
        num, status='complex'):
        self.profile = gpd.read_file(profileName)
        self.hilltop = gpd.read_file(hilltopName)
        self.drawout = gpd.read_file(drawoutName)
        self.contour = gpd.read_file(contourName)
        self.raster = rasterio.open(rasterName)

        self.num = num
        self.name = str(self.profile['name'][num]) + '-' + str(self.profile['Id'][num])
        self.status = status

        self.profileGeo = self.profile.geometry
        self.hilltopGeo = self.hilltop.geometry
        self.drawoutGeo = self.drawout.geometry
        self.contourGeo = self.contour.geometry

        self.drawoutShape = self.drawout.shape[0]
        self.hilltopShape = self.hilltop.shape[0]
        self.contourShape = self.contour.shape[0]

        self.profileInnerCoords = None
        self.profileOuterCoords = None
        self.proDrawoutCoords = None
        self.proHilltopCoords = None
        self.power = None
        self.hilltopIndex = None
        # self.dataframe will generate above parameters
        self.finalDataFrame = self.dataframe()

    
    def _elevation(self, coordinates):
        # 輸入twd97座標點位得到該點位高程
        for (lon, lat) in coordinates:
            py, px = self.raster.index(lon, lat)
            height = self.raster.read()[0][py, px]
        
        
        return height


    def _identify_power(self, profileInnerCoords, profileOuterCoords):
        # 利用x座標判斷升冪or降冪
        if profileInnerCoords[0] > profileOuterCoords[0]:
            power = 'ascending'
        elif profileInnerCoords[0] < profileOuterCoords[0]:
            power = 'descending'
        else:
            raise ValueError


        return power


    def dataframe(self):
        '''
        找出與剖面線交點的座標並return一個raw dictionary
        1. 剖面線的兩個端點: profileInner (在劃出範圍內的點) & profileOuter (在劃出範圍外的點)
        2. 剖面線與劃出範圍的交點: proDrawout
        3. 剖面線與坡頂線的交點: proHilltop
        4. 剖面線與等高線的交點
        '''        

        _rawDict = collections.defaultdict(dict) # raw dictionary
        # 先找出剖面線的兩個端點座標以及剖面線與劃出範圍的交點
        # profileNodes: [Inner and Outer] 順序不一定
        # proDrawoutIntersects:[Inner and proDrawout] 順序不一定
        profileNodes = list(self.profileGeo[self.num].coords)
        for drw in range(self.drawoutShape):
            if self.profileGeo[self.num].intersects(self.drawoutGeo[drw]) == True:
                proDrawoutIntersects = list(self.profileGeo[self.num].intersection(self.drawoutGeo[drw]).coords)
                break

        # 剖面線的兩個端點
        # profileInner 同時存在於兩個list裡, 利用此特性找出剖面線兩個端點的座標
        profileInner = [i for i in profileNodes if i in proDrawoutIntersects]
        profileOuter = [i for i in profileNodes if i not in proDrawoutIntersects]
        
        # 剖面線與劃出範圍的交點
        # 交點不在端點的list裡
        proDrawout = [i for i in proDrawoutIntersects if i not in profileNodes]
        
        # 剖面線端點與劃出範圍交點的高程
        # 為了畫圖方便 設定profileInnerEL = proDrawoutEL
        # 使得劃出範圍後都是平的
        profileOuterEL = self._elevation(profileOuter)
        profileInnerEL = self._elevation(profileInner)
        proDrawoutEL = self._elevation(proDrawout)

        # 剖面線端點與劃出範圍交點的座標
        profileInnerCoords = profileInner[0]
        profileOuterCoords = profileOuter[0]
        proDrawoutCoords = proDrawout[0]

        # 座標與高程輸入 _rawDict
        _rawDict[profileInnerCoords]['elevation'] = profileInnerEL
        _rawDict[profileInnerCoords]['remarks'] = '剖面線端點(內)'

        _rawDict[profileOuterCoords]['elevation'] = profileOuterEL
        _rawDict[profileOuterCoords]['remarks'] = '剖面線端點(外)'

        _rawDict[proDrawoutCoords]['elevation'] = proDrawoutEL
        _rawDict[proDrawoutCoords]['remarks'] = '劃出範圍'


                
        # 剖面線與等高線的交點
        for cntr in range(self.contourShape):
            if self.contourGeo[cntr].intersects(self.profileGeo[self.num]) == True:
                proContour = list(self.profileGeo[self.num].intersection(self.contourGeo[cntr]).coords)
                contourEL = self.contour['Height'][cntr]
                _rawDict[proContour[0]]['elevation'] = contourEL
                _rawDict[proContour[0]]['remarks'] = '等高線'

        # 判斷該剖面是否存在坡頂線
        # hillFlag default False: 一開始預設不存在坡頂線
        hillFlag = False
        for hill in range(self.hilltopShape):
            if self.hilltopGeo[hill].intersects(self.profileGeo[self.num]) == True:
                hillFlag = True
                proHilltop = list(self.profileGeo[self.num].intersection(self.hilltopGeo[hill]).coords)
                proHilltopCoords = proHilltop[0]

                # 如果坡頂線已經指定高程，則使用該高程
                # 如果沒有指定的話，使用DEM判斷高程
                try:
                    proHilltopEL = self.hilltop.iloc[hill]['Height']

                except:
                    proHilltopEL = self._elevation(proHilltop)


                # check is the proHilltopCoords have the same coords with proContour
                # 先對坡頂線的XY高程進行小數點以下7位無條件捨去
                proHilltopCoordsX = np.floor(proHilltopCoords[0])
                proHilltopCoordsY = np.floor(proHilltopCoords[1])
                _rawDictKeys = list(_rawDict.keys())
                
                coordsFlag = False
                for i in range(len(_rawDictKeys)):
                    keyX = np.floor(_rawDictKeys[i][0])
                    keyY = np.floor(_rawDictKeys[i][1])
                    
                    if proHilltopCoordsX == keyX and proHilltopCoordsY == keyY:
                        coordsFlag = True
                        proHilltopCoords = _rawDictKeys[i]
                        _rawDict[proHilltopCoords]['remarks'] = '坡頂線'
                        break

                if coordsFlag == False:
                    _rawDict[proHilltopCoords]['elevation'] = proHilltopEL
                    _rawDict[proHilltopCoords]['remarks'] = '坡頂線'

        # 判斷升冪或降冪
        # 依照升降冪對 X座標排序
        power = self._identify_power(
            profileInnerCoords=profileInnerCoords, 
            profileOuterCoords=profileOuterCoords
            )
        
        if power == 'ascending':
            _coordsDict = {
                'coordinates': [k for k, v in sorted(_rawDict.items(), key=lambda x:x[0][0])], 
                'elevation': [list(v.values())[0] for k, v in sorted(_rawDict.items(), key=lambda x:x[0][0])],
                'remarks': [list(v.values())[1] for k, v in sorted(_rawDict.items(), key=lambda x:x[0])]
                }  
        elif power == 'descending':
            _coordsDict = {
                'coordinates': [k for k, v in sorted(_rawDict.items(), key=lambda x:x[0][0], reverse=True)], 
                'elevation': [list(v.values())[0] for k, v in sorted(_rawDict.items(), key=lambda x:x[0][0], reverse=True)],
                'remarks': [list(v.values())[1] for k, v in sorted(_rawDict.items(), key=lambda x:x[0], reverse=True)]
                }
        else:
            raise ValueError

        # generate a datafrmae which contain all informations
        # if hillFlag = False, hilltopCoords has not been define
        # hilltopCoords will be define later
        # withdraw and withdrawSum has not been define as well
        _coordsDF = pd.DataFrame(_coordsDict, columns=['coordinates', 'elevation', 'remarks'])
        rawDataFrame = self.generate(_coordsDF)

        # 為了之後算退縮距離方便先取index, 取劃出範圍外第一個大於15度的坡為退縮起點 (坡頂線)
        # if hillFlag == False, 判斷坡頂線的index得到坡頂線的座標點位
        # 由於坡頂線的定義為劃出範圍外第一個大於15度的坡為退縮起點，所以倒數兩個點位不須列入考慮
        # 倒數兩個點位為剖面線的端點以及剖面線與劃出範圍的交點
        if hillFlag:
            rawHilltopIndex = rawDataFrame[rawDataFrame['remarks'] == '坡頂線'].index.values[0]
        else:
            rawHilltopIndex = np.flatnonzero(rawDataFrame['slopeDegree'][0:-2].values > 15)[-1]
            proHilltopCoords = rawDataFrame['coordinates'][rawHilltopIndex]
            rawDataFrame.loc[rawHilltopIndex, 'remarks'] = '坡頂線'
        

        # calculate composite hill
        complexDataframe, hilltopIndex = self.composite(
            dataframe=rawDataFrame, 
            rawHilltopIndex=rawHilltopIndex, 
            proHilltopCoords=proHilltopCoords
            )
        # calculate withdraw and withdrawSum
        finalDataFrame = self.withdraw(complexDataframe, hilltopIndex)     
        

        """Some Coordinates"""
        self.profileInnerCoords = profileInnerCoords
        self.profileOuterCoords = profileOuterCoords
        self.proDrawoutCoords = proDrawoutCoords
        self.proHilltopCoords = proHilltopCoords
        self.power = power
        self.hilltopIndex = hilltopIndex
        
        
        return finalDataFrame

    def generate(self, dataframe):
        """
        Input coordinates and elevation
        generate some details and total dataframe
        details include
        1. delta Elevation
        2. distance
        3. distance Sum
        4. slope
        5. slope Factor
        Didn't include withdraw and withdraw Sum
        """
        _coordsDF = dataframe[['coordinates', 'elevation', 'remarks']]
        dfShape = len(_coordsDF)

        deltaELList = []
        distanceList = []
        distanceSumList = []
        slopeDegreeList = []
        slopePercentList = []
        slopeFactorList = []

        distanceSum = 0
        for i in range(dfShape):

            if i == 0:
                deltaELList.append(0)
                distanceList.append(0)
                distanceSumList.append(0)
                slopeDegreeList.append(0)
                slopePercentList.append(0)
                slopeFactorList.append(0)
            
            else:
                # delta Elevation (高程差)
                deltaEL = abs(
                    float(_coordsDF['elevation'].iloc[i]) - float(_coordsDF['elevation'].iloc[i-1])
                    )
                deltaELList.append(deltaEL)

                # distance (水平距離) and distanceSUm (水平累距)
                if i == dfShape-1:
                    # 劃出範圍外延伸10公尺
                    # 最後一個distance不計算直接加10公尺
                    distance = 10
                
                elif i == 1:
                    # 剖面線端點到等高線固定10公尺
                    distance = 10
                
                else:
                    distance = math.sqrt(
                        (_coordsDF['coordinates'].iloc[i][0] - _coordsDF['coordinates'].iloc[i-1][0])**2 + 
                        (_coordsDF['coordinates'].iloc[i][1] - _coordsDF['coordinates'].iloc[i-1][1])**2
                        )
                distanceSum += distance
                distanceList.append(distance)
                distanceSumList.append(distanceSum)

                # slope (斜率, 度)
                # slope pecent (斜率, 趴)
                try:
                    slopeDegree = np.degrees(np.arctan(deltaEL/distance))
                    slopePercent = (deltaEL/distance)*100

                except:
                    slopeDegree = 0
                    slopePercent = 0
                slopeDegreeList.append(slopeDegree)
                slopePercentList.append(slopePercent)

                # slopeFactor (退縮因子)
                if slopeDegree >= 60.0:
                    slopeFactor = 1

                elif slopeDegree >= 45.0 and slopeDegree < 60:
                    slopeFactor = round(2/3, 2)
                
                elif slopeDegree >= 15.0 and slopeDegree < 45:
                    slopeFactor = 0.5
                
                elif slopeDegree < 15.0:
                    slopeFactor = 0

                else:
                    raise TypeError
                slopeFactorList.append(slopeFactor)
        
        _detailsDict = {
            'deltaEL': deltaELList, 
            'distance': distanceList, 'distanceSum': distanceSumList,
            'slopeDegree': slopeDegreeList, 'slopePercent': slopePercentList, 'slopeFactor': slopeFactorList
        }
        _detailDF = pd.DataFrame(
            _detailsDict, 
            columns = ['deltaEL', 'distance', 'distanceSum', 'slopeDegree', 'slopePercent', 'slopeFactor']
            )
        
        # concat two DataFrame to total dataframe
        totalDataFrame = pd.concat([_coordsDF, _detailDF], axis=1)


        return totalDataFrame

    def composite(self, dataframe, rawHilltopIndex, proHilltopCoords):
        """
        if status == origin
        只將坡度做簡單的處理, 將等高線以及坡頂線外的點拉平
        if status == complex
        將坡度做複合坡處理
        規則:
        第一步:
        1.如果兩個小於15度的坡度中間存在一個大於15度的坡，則此坡將會拿掉
        第二步:
        1.依照坡度的分級標準將坡度變成複合坡
        2.由於15-45度這區間過大，因此在此範圍內，兩兩坡度相減若大於10度則不會複合
        """
        # 
        dataframe.loc[0, 'elevation'] = dataframe.loc[1, 'elevation']
        dataframe.loc[rawHilltopIndex::, 'elevation'] = dataframe['elevation'][rawHilltopIndex]
        
        if self.status == 'origin':
            finalComplexDataframe = self.generate(dataframe=dataframe)        
        
        elif self.status == 'complex':
            # find out the index that should be delete
            deleteIndex = []
            for i in range(2, rawHilltopIndex):
                if dataframe['slopeDegree'][i] > 15:
                    if dataframe['slopeDegree'][i-1] < 15 and dataframe['slopeDegree'][i+1] < 15:
                        deleteIndex.append(i)
            rawComplexDataframe = dataframe.drop(index=deleteIndex)
            complexDataframe = self.generate(dataframe=rawComplexDataframe.reset_index())

            complexIndex = []
            newHilltopIndex = complexDataframe[complexDataframe['remarks'] == '坡頂線'].index.values[0]
            for i in range(2, newHilltopIndex):
                if complexDataframe['slopeFactor'][i] == complexDataframe['slopeFactor'][i+1]:
                    # slope 介於15-45為特殊情況，另外處理
                    if complexDataframe['slopeFactor'][i] == 0.5:
                        # 計算兩坡地之間的差值
                        # 差值取絕對值並向下取整
                        deviation = np.floor(abs(
                            complexDataframe['slopeDegree'][i] - complexDataframe['slopeDegree'][i+1]
                        ))
                        # 若差值大於10則不刪除
                        if deviation > 10:
                            pass
                        else:
                            complexIndex.append(i)
                    else:
                        complexIndex.append(i)
            rawFinalComplexDataframe = complexDataframe.drop(index=complexIndex)
            finalComplexDataframe = self.generate(dataframe=rawFinalComplexDataframe.reset_index())
        else:
            raise TypeError

        # final hilltopIndex
        hilltopIndex = finalComplexDataframe[finalComplexDataframe['remarks'] == '坡頂線'].index.values[0]


        return finalComplexDataframe, hilltopIndex

    def withdraw(self, dataframe, hilltopIndex):

        withdrawList = []
        withdrawSumList = []

        withdrawSum = 0
        for i in range(len(dataframe)):
            if i <= hilltopIndex:
                withdraw = dataframe['deltaEL'][i] * dataframe['slopeFactor'][i]
                withdrawSum += withdraw
            else:
                withdraw = 0
                withdrawSum += withdraw
            withdrawList.append(withdraw)
            withdrawSumList.append(withdrawSum)

        dataframe['withdraw'] = withdrawList
        dataframe['withdrawSum'] = withdrawSumList


        return dataframe
if __name__ == '__main__':
    import os

    os.chdir(r'C:\Users\heteng\Desktop\桃園\龜山')

    profileName = '龜山剖面線.shp'
    hilltopName = '大湖坡頂線110119.shp'
    drawoutName = '龜山範圍1.28V2.shp'
    contourName = '龜山等高線_扣範圍內.shp'

    rasterName = '龜山區.tif'


    GIS = GISControl(
    profileName=profileName, hilltopName=hilltopName, 
    contourName=contourName, drawoutName=drawoutName, 
    rasterName=rasterName,
    num=0, status='origin'
    )
    print(GIS.finalDataFrame)