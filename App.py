from Runner import MaRunner
from DataGathers import StaticData
from DataGathers import AutoProfiler_Gather
import traceback
import json
import time
import Init
import argparse
import os
import threading

#开始运行脚本
if __name__ == "__main__":
    try:
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
        parser.add_argument("-c", help="Config file path")  #配置文件路径

        args = parser.parse_args()
        ip = args.i or ""
        device = args.s or ""
        analyzetype = args.at or ""
        configPath = args.c or ""
        configData = Init.LoadConfigFile(configPath)
        print(configData)
        gatherObj = StaticData.UnityProfile(serverip="10.11.145.125",port="6950",timeout=60)  #连接Master服务器
        
        print("您是否开启采集数据功能？y/n")
        flag = input()
        if flag == "y":
            gameID = "e40280a0"
            uid = StaticData.GetUUID()
            print("随机生成的uuid为" + str(uid) +",是否使用？y/n")
            choicUUID = input()
            if choicUUID == "y":
                uuID = uid
            else:
                uuID = input("请输入uuid：")
                
            if device == "":
                    udriver = MaRunner.MatoryConnect(device=device,connectip="127.0.0.1",port=2666,timeout=60)
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

                udriver = MaRunner.MatoryConnect(device,ip,por=13000,timeout=60)

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

            # 采集上传文件处理逻辑
            thread = threading.Thread(target=AutoProfiler_Gather.GatherUploadModule(devicetype=devicetype,isStop=isStop,udriver=udriver,gameID=gameID,uuID=uuID,
                                                                                    gatherObj=gatherObj,ConfigData=configData,analyzetype=analyzetype,unityversion=unityversion,
                                                                                    gamename="MechaBREAK",casename="ceshi",collectorip="10.11.145.125"))
            thread.start()

            time.sleep(60)
            isStop = True
            udriver.StopProfilerGather() #结束采集消息信号

            while True:
                time.sleep(10)
                if thread.is_alive() !=True:
                    break


            #关闭连接
            gatherObj.CloseConnect()
            udriver.CloseConnect()
    except:
        traceback.print_exception()