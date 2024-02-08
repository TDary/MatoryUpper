import argparse
import os
import socket
import time
import zipfile
import gzip
import zipfile
import json
import datetime
import shutil
import re
import wmi
import random
import minio
import importlib
import threading

import traceback

def uploadTest():
    global isStop
    global udriver
    global url
    global client
    global child_url
    global gameID
    global uuID
    global client_socket
    url = '10.11.144.31:8001' # 存储服务器路径
    child_url = 'rawdata'# 存储桶名
    zhanghao = 'cdr'
    mima = 'cdrmm666!@#'
    client = minio.Minio(endpoint=url,access_key=zhanghao,secret_key=mima,secure=False)
    while True:
        time.sleep(1)
        record = udriver.profile_check()
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
                zip_files(newnamePath,zipfilePath)

                uploadObjectName = uuID + "/" + zipfile

                try:
                    if client.bucket_exists(bucket_name=child_url):  # bucket_exists：检查桶是否存在
                        pass
                    else:
                        client.make_bucket(child_url)
                        # print("存储桶创建成功")
                except Exception as err:
                    print(err)

                # start_upload_time = datetime.datetime.now()
                # upload_time.append({'name':files,'time':start_upload_time,'size':"123456"})
                # client.put_object(child_url,uploadObjectName,zipfilePath,)  content_type="application/zip"
                client.fput_object(bucket_name=child_url,object_name=uploadObjectName,file_path=zipfilePath,content_type="application/zip")
                print("上传" + zipfilePath + "到服务器成功")
                #请求解析
                rafilename = uuID+"/"+zipfile
                requestMsg = "requestanalyze?uuid="+uuID+"&rawfile="+zipfile+"&objectname="+rafilename+"&unityversion=2022.3.2f1&analyzebucket="+child_url+"&analyzetype=funprofiler"
                client_socket.sendall(requestMsg.encode())
                # 接收从服务器返回的消息
                response = client_socket.recv(2048)
                print('Received message from server:', response.decode())

                #删除源文件
                os.remove(zipfilePath)
                os.remove(newnamePath)

        if isStop == True:
            udriver.profile_stop() #发送停止采集消息
            #停止采集，并把最后一个源文件记录下来
            if len(fileslist) !=0:
                thelastFile = fileslist[len(fileslist) - 1]
                #发送停止采集消息
                #r = requests.get(upload_url + "stopanalyze?" +"uuid=" + str(uuID) + "&lastfile=" + thelastFile) # 停止信号
                stopMsg = "stopanalyze?" +"uuid=" + str(uuID) + "&lastfile=" + thelastFile
                client_socket.sendall(stopMsg.encode())
            break


#数据解析+上传设备信息
def profile():
    global url
    global gameID
    global uid
    global version
    global fileslist
    global uuID
    global version
    global device
    global client_socket
    print("发送开始采集消息")
    try:
        list1 = []

        if device == "":
            w = wmi.WMI()
            for BIOSs in w.WIN32_ComputerSystem():
                list1.append("电脑名称: %s" %BIOSs.Caption)
            for BIOS in w.Win32_BIOS():
                list1.append("主板型号: %s" %BIOS.SerialNumber)
            for processor in w.Win32_Processor():
                list1.append("CPU型号: %s" % processor.Name.strip())
            for xk in w.Win32_VideoController():
                list1.append("显卡名称: %s" %xk.name)
            deviceinfo = " ".join(list1)
            print(deviceinfo)
        else:
            result = os.popen("adb shell getprop ro.product.model").read()
            deviceinfo = result.strip()
            print(deviceinfo)

        requestUrl = "startanalyze?" + "&device="+ deviceinfo + "&gameid=" + gameID + "&uuid=" + uuID + "&unityVersion=2022.3.2f1" + "&rawFiles=" +"&bucket=rawdata&analyzeType=funprofiler&gameName=CB&caseName=ceshi&collcetorIp=10.11.144.31"
        client_socket.sendall(requestUrl.encode())
        #r = requests.get(upload_url + "startanalyze?" + "&device="+ deviceinfo + "&gameid=" + gameID + "&uuid=" + uuID + "&unityVersion=2021.3.1f1" + "&rawFiles=" +"&bucket=rawdata&anatype=funprofiler&gameName=CB&caseName=ceshi")

        print("已成功请求采集解析数据")
        return "已成功请求解析数据"

    except Exception as e:
        traceback.print_exception(e)

# def get_all_window():
#     hWndList = []

#     def winEnumHandler(hwnd, hWndList):
#         if win32gui.IsWindowVisible(hwnd):
#             hWndList.append(hwnd)

#     win32gui.EnumWindows(winEnumHandler, hWndList) 
    
#     return hWndList

# def Get_Apps(device):
#     if device == "":
#         hwndList = get_all_window()
#         titles = []
#         for hwnd in hwndList:
#             title = win32gui.GetWindowText(hwnd)
#             if len(title) > 0:
#                 titles.append(title)
#         return titles
#     else:
#         # 目前没有 ios 的截图，默认非 PC 的都是 Android
#         str_init = ''
#         all_packages = os.popen(f"adb -s {device} shell pm list packages").readlines()

#         for i in range(len(all_packages)):
#             str_init += all_packages[i]

#         package_name = re.findall('package:.*?\n',str_init,re.S)
#         packages = []

#         for package in package_name:
#             packages.append(package[8:-1])

#         return packages

#开始运行脚本
if __name__ == "__main__":
    project_name = []
    device = ''
    ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
    adbPath = os.path.join(ROOT_DIR,'adb.exe')
    screenShooter = None
    upload_url = "http://10.11.144.31:6950/"
    delete_files = ''
    gameID = ''   
    uuID = ''
    uid = ''
    isStop = False
    recordlist = []
    startTime = ''
    udriver = None
    upload_time = []
    version = ''
    app = ''


    # 服务器地址和端口
    server_addr = ('10.11.144.31',6950)

    # 创建Socket对象
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # 连接到服务器
        client_socket.connect(server_addr)
        
        print('Connected to server')

        # 发送消息到服务器
        message = 'markeid?collector'
        client_socket.sendall(message.encode())

        # 接收从服务器返回的消息
        response = client_socket.recv(2048)
        print('Received message from server:', response.decode())

    except socket.error as e:
        print('Error occurred:', str(e))
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help="ip")  #命令行参数 -i ip地址
    parser.add_argument("-s", help="devices serial")  #命令行参数 -s 设备号

    args = parser.parse_args()
    ip = args.i or ""
    device = args.s or ""

    print("您是否开启采集数据功能？y/n")
    flag = input()
    if flag == "y":
        gameID = "e40280a0"
        uid = choice()
        print("随机生成的uuid为" + uid +",是否使用？y/n")
        choicUUID = input()
        if choicUUID == "y":
            uuID = uid
        else:
            uuID = input("请输入uuid：")
            
        if device == "":
                udriver = Matory("127.0.0.1","","127.0.0.1",TCP_PORT=13000,timeout=60)
                # screenShooter = ScreenShooter(Platform.PC)
        else:
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

            udriver = AltrunUnityDriver(device,"",ip,TCP_PORT=13000,timeout=60)

        startTime = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())

        #开始采集
        temp_data = {"path":"E:\\files"}
        collectiondata={
                "collection": { #"ubox": {}
                },"data": {#"uuid": uuID,"path": "E:/CollectData"
                }}
        collection = {"ubox":json.dumps(temp_data)}
        collectiondata["collection"]=json.dumps(collection)
        collectiondata["data"]=json.dumps({"uuid": uuID,"path": "E:\\rawdata\\"})
        udriver.record_profile("",json.dumps(collectiondata))
        profile() #请求开始采集

        # 上传文件
        thread = threading.Thread(target=uploadTest)
        thread.start()

        time.sleep(60)
        isStop = True

        while True:
            time.sleep(10)
            if thread.is_alive() !=True:
                break


        #关闭连接
        # client_socket.close()
        udriver.stop()

