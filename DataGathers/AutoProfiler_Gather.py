import argparse
import os
import time
import json
import threading
import StaticData
import traceback
import Runner.MaRunner
import MinioSdk

# 控制采集和上传模块
def GatherUploadModule():
    global isStop
    global udriver
    global gameID
    global uuID
    global gatherObj
    global ConfigData
    global analyzetype
    global unityversion
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
def AnalyzeToProfile():
    global gameID
    global uid
    global unityversion
    global gatherObj
    global uuID
    global device
    global devicetype
    global ConfigData
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
def Get_ScreenCapture(captureFilePath):
    global udriver
    udriver.TakeGameScreenCapture(captureFilePath)

#开始运行脚本
if __name__ == "__main__":
    project_name = []
    device = ''
    ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
    adbPath = os.path.join(ROOT_DIR,'adb.exe')
    screenShooter = None
    delete_files = ''
    gameID = ''   
    uuID = ''
    uid = ''
    isStop = False
    recordlist = []
    startTime = ''
    udriver = None
    upload_time = []
    app = ''
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help="ip address")  #命令行参数 -i ip地址
    parser.add_argument("-s", help="devices serial")  #命令行参数 -s 设备号
    parser.add_argument("-at", help="Analyze type.This supported funprofiler or simple") # 解析类型

    args = parser.parse_args()
    ip = args.i or ""
    device = args.s or ""
    analyzetype = args.at or ""

    jsonPath = "./Config.json"

    with open(jsonPath,"r",encoding="utf-8") as f:
        print(type(f))
        ConfigData = json.load(f)
        f.close()

    gatherObj = StaticData.UnityProfile(serverip="10.11.144.31",port="6950",timeout=60)  #连接采集服务器
    
    print("您是否开启采集数据功能？y/n")
    flag = input()
    if flag == "y":
        gameID = "e40280a0"
        uid = StaticData.GetUUID()
        print("随机生成的uuid为" + uid +",是否使用？y/n")
        choicUUID = input()
        if choicUUID == "y":
            uuID = uid
        else:
            uuID = input("请输入uuid：")
            
        if device == "":
                udriver = Runner.MaRunner.MatoryConnect(device=device,connectip="127.0.0.1",port=2666,timeout=60)
                devicetype = "PC"
        else:
            devicetype = "Android"
            if ip == "":
                try:
                    res = os.popen(f"{adbPath} -s {device} shell ifconfig").read()
                    ip = res.split('wlan0')[1].split('inet addr:')[1].split(' ')[0]
                except:
                    try:
                        res = os.popen(f'{adbPath} -s {device} shell netcfg').read()
                        ip = res.split('wlan0')[1].split('UP')[1].split('/')[0].split()[0]
                    except:
                        res = os.popen(f'{adbPath} -s {device} shell netstat').read()
                        ip = res.split('udp')[1].split(':bootpc')[0].split(' ')[-1]

            udriver = Runner.MaRunner.MatoryConnect(device,ip,por=13000,timeout=60)

        startTime = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())

        # 获取游戏包版本
        unityversion = udriver.GetGameVersion()

        # 开始采集
        temp_data = {"path":"D:\\files"}
        collectiondata={"collection": {},"data": {}}
        collection = {"profiler_gather":json.dumps(temp_data)}
        collectiondata["collection"]=json.dumps(collection)
        collectiondata["data"]=json.dumps({"uuid": uuID,"path": "D:\\files\\"})
        udriver.ProfilerGather(json.dumps(collectiondata))
        AnalyzeToProfile() #请求开始采集

        # 上传文件并处理采集逻辑
        thread = threading.Thread(target=GatherUploadModule)
        thread.start()

        time.sleep(60)
        isStop = True

        while True:
            time.sleep(10)
            if thread.is_alive() !=True:
                break


        #关闭连接
        gatherObj.CloseConnect()
        udriver.CloseConnect()

