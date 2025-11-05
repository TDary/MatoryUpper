import socket
import time
import json
from Runner import *

class MatoryConnect(object):
    def __init__(self,device="",connectip="127.0.0.1",port=2666,timeout=60,log_flag=False):
        '''
        :param connectip: Hostname of a socket service.
        :param port: TCP Port of machine.
        '''
        self.TCP_IP = connectip
        self.TCP_PORT = port
        self.connect = False
        self.udriver = None
        self.message = {
            'FuncName':'',
            'FuncArgs':[]
        }
        while timeout > 0:
            try:
                self.udriver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                for _ in range(5):
                    try:
                        self.udriver.connect((connectip, port))
                        self.udriver.settimeout(timeout)
                        break
                    except ConnectionRefusedError:
                        print(f"连接{TCP_PORT}失败 尝试连接{TCP_PORT+1}")
                        TCP_PORT+=1

                self.connect = True
                time.sleep(1)
                print("获取SDK版本号——")
                print("Sdk Version:"+self.GetServerVersion()["Data"])
                break
            except Exception as e:
                print(e)
                print('MatoryServer not running on port ' + str(self.TCP_PORT) +
                      ', retrying (timing out in ' + str(timeout) + ' secs)...')
                timeout -= timeout
                # time.sleep(timeout)

        if timeout <= 0:
            raise Exception('Connecting Timeout，Could not connect to MatoryServer on: '+ self.TCP_IP +':'+ str(self.TCP_PORT))

    '''
    发送消息封装函数模块
    '''
    def SendMessageModule(self,message):
        msg = json.dumps(message)
        print("Send Msg:"+msg)
        self.udriver.sendall(msg.encode())
        resData = self.udriver.recv(65536).decode()
        print("Receive Data:"+str(resData))
        response = json.loads(resData)
        return response

    '''
    发送开始采集消息模块
    '''
    def ProfilerGather(self,args):
        self.message['FuncName'] = 'Gather_Profiler'
        self.message['FuncArgs'] = ['Gather_Profiler','1',args]
        return self.SendMessageModule(self.message)

    '''
    发送停止采集消息模块
    '''
    def StopProfilerGather(self):
        self.message['FuncName'] = 'Gather_Profiler'
        self.message['FuncArgs'] = ['Gather_Profiler','0']
        return self.SendMessageModule(self.message)

    '''
    关闭连接
    '''
    def CloseConnect(self)->None:
        self.udriver.close()

    '''
    获取Sdk版本
    '''
    def GetServerVersion(self)->None:
        self.message['FuncName'] = 'GetSdkVersion'
        self.message['FuncArgs'] = []
        return self.SendMessageModule(self.message)

    '''
    获取游戏引擎版本
    '''
    def GetGameVersion(self)->None:
        self.message['FuncName'] = 'GetGameVersion'
        self.message['FuncArgs'] = []
        return self.SendMessageModule(self.message)

    '''
    寻找文本内容UI
    '''
    def FindText(self,textname:str):
        self.message['FuncName'] = 'Find_Text'
        self.message['FuncArgs'] = [f'{textname}']
        return self.SendMessageModule(self.message)

    '''
    获取当前所有Button按钮
    '''
    def GetAllButton(self):
        self.message['FuncName'] = 'Find_AllButton'
        self.message['FuncArgs'] = []
        return self.SendMessageModule(self.message)

    '''
    检查一下采集中的生成数据
    '''
    def CheckProfiler(self):
        self.message['FuncName'] = 'Check_Profiler'
        self.message['FuncArgs'] = []
        return self.SendMessageModule(self.message)

    '''
    获取Unity中的Hierarchy面板信息
    '''
    def GetProjectHierarchy(self):
        self.message['FuncName'] = 'Get_Hierarchy'
        self.message['FuncArgs'] = []
        return self.SendMessageModule(self.message)

        '''
    获取Unity中的Inspector面板信息
    '''
    def GetProjectInspector(self,objId:int):
        self.message['FuncName'] = 'Get_Inspector'
        self.message['FuncArgs'] = [f'{objId}']
        return self.SendMessageModule(self.message)

    '''
    触发一次UI单击操作,通过路径触发
    '''
    def ClickButtonByPath(self,UIPath:str):
        self.message['FuncName'] = 'ClickOne'
        self.message['FuncArgs'] = ['leftclick',f'{UIPath}','path']
        return self.SendMessageModule(self.message)
    
    '''
    触发一次UI单击操作,通过InstanceId触发
    '''
    def ClickButtonById(self,id:int):
        self.message['FuncName'] = 'ClickOne'
        self.message['FuncArgs'] = ['click',f'{id}','id']
        return self.SendMessageModule(self.message)

    '''
    触发一次点击事件，通过模拟鼠标形式
    '''
    def ClickButtonBySimulate(self,id:int):
        self.message['FuncName'] = 'ClickOneBySimulate'
        self.message['FuncArgs'] = ['left',f'{id}']
        return self.SendMessageModule(self.message)

    '''
    触发一次内存快照截取
    '''
    def TakeMemorySnapShot(self,type:str,filePath:str):
        self.message['FuncName'] = 'CaptureMemorySnap'
        self.message['FuncArgs'] = [f'{type}',f'{filePath}']
        return self.SendMessageModule(self.message)
    
    '''
    截取一次游戏屏幕截图
    '''
    def TakeGameScreenCapture(self,filePath:str):
        self.message['FuncName'] = 'GetScreenShot'
        self.message['FuncArgs'] = [f'{filePath}']
        return self.SendMessageModule(self.message)

    '''
    调用游戏自定义GM
    '''
    def CustomGM(self,*value):
        allargs = ','.join(value)
        gmargs = allargs.split(',')
        self.message["FuncName"] = 'gm'
        self.message['FuncArgs'] = gmargs
        return self.SendMessageModule(self.message)

    '''
    设置UnityGameObject对象激活与失活
    '''
    def SetGameObjectState(self,game_objectName:str,value:bool):
        self.message['FuncName'] = 'SetGameObjectState'
        self.message['FuncArgs'] = [f'{game_objectName}',f'{value}']
        return self.SendMessageModule(self.message)

    '''
    性能数据采集开始
    '''
    def Performance_Start(self,filePath:str,sample_arg:int):
        self.message['FuncName'] = 'PerformanceData_Start'
        self.message['FuncArgs'] = [f'{filePath}',f'{sample_arg}']
        return self.SendMessageModule(self.message)
    
    '''
    性能数据采集结束
    '''
    def Performance_Stop(self):
        self.message['FuncName'] = 'PerformanceData_Stop'
        self.message['FuncArgs'] = []
        return self.SendMessageModule(self.message)
    
    '''
    获取一帧性能数据
    '''
    def Performance_GetOne(self):
        self.message['FuncName'] = 'PerformanceData_GetOne'
        self.message['FuncArgs'] = []
        return self.SendMessageModule(self.message)
    
    '''
    设置主相机位置点
    '''
    def SetCameraPosition(self,position:str,rotation:str):
        self.message['FuncName'] = 'SetCamera'
        self.message['FuncArgs'] = [f'{position}',f'{rotation}']
        return self.SendMessageModule(self.message)
    
    '''
    设置游戏物体激活与失活
    '''
    def SetGameObjectState(self,objectname:str,value:bool):
        self.message['FuncName'] = 'SetGameObjectState'
        self.message['FuncArgs'] = [f'{objectname}',f'{value}']
        return self.SendMessageModule(self.message)
    
    '''
    开始采集性能数据,输出结果路径以及采样模式，1为每帧写入模式，0为不写入需自己获取单帧
    '''
    def StartPerfData(self,outputpath:str,sample_arg:int):
        self.message['FuncName'] = 'PerformanceData_Start'
        self.message['FuncArgs'] = [f'{outputpath}',f'{sample_arg}']
        return self.SendMessageModule(self.message)

    '''
    停止采集性能数据
    '''
    def StopPerfData(self):
        self.message['FuncName'] = 'PerformanceData_Stop'
        self.message['FuncArgs'] = []
        return self.SendMessageModule(self.message)

    '''
    获取一帧性能数据
    '''
    def GetOnePerfData(self):
        self.message['FuncName'] = 'PerformanceData_GetOne'
        self.message['FuncArgs'] = []
        return self.SendMessageModule(self.message)

    '''
    开始UI录制
    '''
    def StartUIRecord(self):
        self.message['FuncName'] = 'Start_UIRecord'
        self.message['FuncArgs'] = []
        return self.SendMessageModule(self.message)

    '''
    停止UI录制
    '''
    def StopUIRecord(self):
        self.message['FuncName'] = 'Stop_UIRecord'
        self.message['FuncArgs'] = []
        return self.SendMessageModule(self.message)
    
    '''
    开始DTrace追踪
    '''
    def StartDTrace(self):
        self.message['FuncName'] = 'Start_DTracker'
        self.message['FuncArgs'] = []
        return self.SendMessageModule(self.message)
    
    '''
    设置DTrace内存以及快照路径
    '''
    def SetDTracePath(self,filePath:str,maxMemory:float):
        self.message['FuncName'] = 'Set_DTrackerLimit'
        self.message['FuncArgs'] = [f'{filePath}',f'{maxMemory}']
        return self.SendMessageModule(self.message)
    
    # def 