import wmi
import os
import zipfile
import uuid
import socket
import json
import time
import subprocess
from functools import lru_cache

class UnityProfile():
    def __init__(self, serverip: str, port: int, timeout=60):
        self.beginGather = "startgather?"
        self.endGather = "stopgather?"
        self.sendRequestAnalyze = "requestanalyze?"
        self.connectState = False
        self.TCP_PORT = port
        self.TCP_IP = serverip
        self.udriver = None
        while timeout > 0:
            try:
                self.udriver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.udriver.connect((self.TCP_IP, self.TCP_PORT))
                self.udriver.settimeout(timeout)

                self.connectState = True
                time.sleep(1)
                message = 'markeid?collector'
                self.udriver.sendall(message.encode())
                res = self.udriver.recv(1024).decode()
                print("连接成功，ReceiveData：" + res)
                break
            except Exception as e:
                print(e)
                timeout -= timeout
                # time.sleep(timeout)

        if timeout <= 0:
            raise Exception('Connecting Timeout，Could not connect to MasterServer on: ' + self.TCP_IP + ':' + str(self.TCP_PORT))

    # 发送开始采集消息
    def SendtoBeginGather(self, deviceinfo: str, gameID: str, uuID: str,
                          unityversion: str, rawfiles: str, bucketname: str, analyzetype: str, gamename: str, casename: str, collectorip: str):

        requestUrlStrList = [self.beginGather, "&device=", deviceinfo, "&gameid=", gameID, "&uuid=", uuID,
                      "&unityVersion=", unityversion, "&rawFiles=", rawfiles, "&bucket=", bucketname, "&analyzeType=", analyzetype,
                      "&gameName=", gamename, "&caseName=", casename, "&collcetorIp=", collectorip]
        requestUrl = "".join(requestUrlStrList)
        return self.SendMessageModule(requestUrl)

    # 发送停止采集消息
    def SendtoStopGather(self, uuID: str, lastfile: str):
        requestUrlStrList = [self.endGather, "uuid=", uuID, "&lastfile=", lastfile]
        requestUrl = "".join(requestUrlStrList)
        return self.SendMessageModule(requestUrl)

    # 发送客户端请求解析消息
    def SendtoRequestAnalyze(self, uuID: str, zipfile: str, rawfilename: str, unityversion: str, analyzebucket: str, analyzetype):
        requestUrlStrList = [self.sendRequestAnalyze, "uuid=", uuID, "&rawfile=", zipfile, "&objectname=",
                             rawfilename, "&unityversion=", unityversion, "&analyzebucket=", analyzebucket, "&analyzetype=", analyzetype]
        requestUrl = "".join(requestUrlStrList)
        return self.SendMessageModule(requestUrl)

    # 发送socket消息
    def SendMessageModule(self, msg: str):
        print("Send Msg:" + msg)
        self.udriver.sendall(msg.encode())
        response = self.udriver.recv(1024).decode()
        print("Receive Data:" + str(response))
        return response

    # 关闭socket连接
    def CloseConnect(self):
        self.udriver.close()


# 自动生成uuid
def GetUUID():
    uuid_value = uuid.uuid4().hex
    return uuid_value


# 压缩文件
def Zip_files(folder_path: str, output_path: str):
    file_name = os.path.basename(folder_path)
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(folder_path, arcname=file_name)


@lru_cache(maxsize=1)
def GetDevicesData(devicesType: str):
    """获取设备信息，使用 lru_cache 缓存结果避免重复 WMI 查询"""
    if devicesType == "PC":
        listDevice = []
        w = wmi.WMI()
        for BIOSs in w.WIN32_ComputerSystem():
            listDevice.append("电脑名称: %s" % BIOSs.Caption)
        for BIOS in w.Win32_BIOS():
            listDevice.append("主板型号: %s" % BIOS.SerialNumber)
        for processor in w.Win32_Processor():
            listDevice.append("CPU型号: %s" % processor.Name.strip())
        for xk in w.Win32_VideoController():
            listDevice.append("显卡名称: %s" % xk.name)
        deviceinfo = " ".join(listDevice)
        return deviceinfo
    elif devicesType == "Phone":
        result = subprocess.run("adb shell getprop ro.product.model", shell=True, capture_output=True, text=True, timeout=10)
        deviceinfo = result.stdout.strip()
        return deviceinfo
    else:
        print("Current type is not surpported or this type is empty.")
        return ""


def GetDeviceIP(device: str, adbPath: str):
    """通过 adb 获取设备 IP，替代废弃的 os.popen"""
    commands = [
        f'"{adbPath}" -s {device} shell ifconfig',
        f'"{adbPath}" -s {device} shell netcfg',
        f'"{adbPath}" -s {device} shell ip addr show wlan0',
    ]
    for cmd in commands:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            output = result.stdout
            if 'wlan0' in output:
                # 尝试多种格式解析
                for pattern in ['inet addr:', 'inet ']:
                    if pattern in output:
                        parts = output.split('wlan0')[1].split(pattern)[1]
                        ip = parts.split(' ')[0].split('/')[0]
                        return ip
        except Exception:
            continue
    print("Failed to get device IP, using empty string")
    return ""
