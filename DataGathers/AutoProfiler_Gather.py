import os
import time
import json
import StaticData
import traceback
from Runner import MaRunner
import MinioSdk

# 控制采集和上传模块
def GatherUploadModule(isStop,udriver,gameID,uuID,gatherObj,ConfigData,analyzetype,unityversion):
    bucket = ConfigData["minioserver"]["rawbucket"]
    client = MinioSdk.Minio_SDK(url=ConfigData["minioserver"]["url"],bucketName=bucket,access_key=ConfigData["minioserver"]["access_key"],secret_key=ConfigData["minioserver"]["secret_key"])
    while True:
        time.sleep(1)
        record = udriver.CheckProfiler()
        fileslist = []
        if record["ubox"]!=[]:
            datas = json.loads(record["ubox"])
            for file in datas:
                current_timestamp = int(time.time())

                path = os.path.join(file['path'],file['name'] + ".raw") # 本地文件路径

                newnamePath = os.path.join(file['path'],str(current_timestamp) + ".raw")
                os.rename(path,newnamePath)

                zipfile = str(current_timestamp) +'.zip'
                zipfilePath = os.path.join(file['path'],zipfile)

                if zipfile not in fileslist:
                    fileslist.append(zipfile)

                # 压缩文件夹
                StaticData.Zip_files(newnamePath,zipfilePath)

                uploadObjectName = uuID + "/" + zipfile

                client.UploadItem(objName=uploadObjectName,filePath=zipfilePath,contentType="application/zip")

                #请求解析
                rawfilename = uuID+"/"+zipfile
                gatherObj.SendtoRequestAnalyze(socketObj=gatherObj,uuID=uuID,zipfile=zipfile,rawfilename=rawfilename,
                                               unityversion=unityversion,analyzebucket=bucket,analyzetype=analyzetype)

                #删除源文件
                os.remove(zipfilePath)
                os.remove(newnamePath)

        if isStop == True:
            udriver.profile_stop() #发送停止采集消息
            #停止采集，并把最后一个源文件记录下来
            if len(fileslist) !=0:
                thelastFile = fileslist[len(fileslist) - 1]
                #发送停止采集消息
                gatherObj.SendtoStopGather(socketObj=gatherObj,uuID=uuID,lastfile=thelastFile)
            break


#数据解析+上传设备信息
def AnalyzeToProfile(gameID,unityversion,gatherObj,uuID,devicetype,ConfigData):
    try:
        rawfiles = ""
        analyzetype = "funprofiler"
        deviceinfo = StaticData.GetDevicesData(devicetype)
        res = gatherObj.SendtoBeginGather(sokcetObj=gatherObj,deviceinfo=deviceinfo,gameID=gameID,uuID=uuID,
                                          unityversion=unityversion,rawfiles=rawfiles,bucketname=ConfigData["minioserver"]["rawbucket"],
                                          analyzetype=analyzetype,gamename="CB",casename="ceshi",collectorip="192.168.0.110") 
        return res

    except Exception as e:
        traceback.print_exception(e)

# 传绝对路径
def Get_ScreenCapture(captureFilePath,udriver):
    udriver.TakeGameScreenCapture(captureFilePath)
