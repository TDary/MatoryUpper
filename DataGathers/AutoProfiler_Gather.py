import os
import time
import json
from Runner import MaRunner
from DataGathers import MinioSdk
from DataGathers import StaticData
import threading

# 控制上传模块
def GatherUploadModule(devicetype,stopEvent:threading.Event,udriver:MaRunner.MatoryConnect,gameID,uuID,gatherObj:StaticData.UnityProfile,configData,analyzetype,unityversion,gamename,casename,collectorip):
    #请求开始采集
    rawfiles = ""
    bucket = configData["minioserver"]["rawbucket"]
    res = gatherObj.SendtoBeginGather(deviceinfo=devicetype,gameID=gameID,uuID=uuID,
                                          unityversion=unityversion,rawfiles=rawfiles,bucketname=bucket,
                                          analyzetype=analyzetype,gamename=gamename,casename=casename,collectorip=collectorip) 
    client = MinioSdk.Minio_SDK(url=configData["minioserver"]["url"],bucketName=bucket,access_key=configData["minioserver"]["access_key"],secret_key=configData["minioserver"]["secret_key"])
    while not stopEvent.is_set():
        time.sleep(1)
        record = udriver.CheckProfiler()
        if record["Code"] == 200:
            datas = json.loads(record['Data'])
            fileslist = []
            if datas["profiler_gather"]!="[]":
                detailData = json.loads(datas["profiler_gather"])
                for file in detailData:
                    current_timestamp = int(time.time())
                    strcurrent_timestamp = str(current_timestamp)
                    path = os.path.join(file['path'],file['name'] + ".raw") # 本地文件路径

                    newnamePath = os.path.join(file['path'],strcurrent_timestamp + ".raw")
                    os.rename(path,newnamePath)

                    zipfile = strcurrent_timestamp +'.zip'
                    zipfilePath = os.path.join(file['path'],zipfile)

                    if zipfile not in fileslist:
                        fileslist.append(zipfile)

                    # 压缩文件夹
                    StaticData.Zip_files(newnamePath,zipfilePath)

                    uploadObjectName = uuID + "/" + zipfile

                    client.UploadItem(objName=uploadObjectName,filePath=zipfilePath,contentType="application/zip")

                    #请求解析
                    gatherObj.SendtoRequestAnalyze(uuID=uuID,zipfile=zipfile,rawfilename=uploadObjectName,
                                                unityversion=unityversion,analyzebucket=bucket,analyzetype=analyzetype)

                    #删除源文件
                    os.remove(zipfilePath)
                    os.remove(newnamePath)

    #停止采集，并把最后一个源文件记录下来
    if len(fileslist) !=0:
        thelastFile = fileslist[len(fileslist) - 1]
        #发送停止采集消息
        res = gatherObj.SendtoStopGather(uuID=uuID,lastfile=thelastFile)
        print("接受停止采集消息：" + res)


# 传绝对路径
def Get_ScreenCapture(captureFilePath,udriver):
    udriver.TakeGameScreenCapture(captureFilePath)
