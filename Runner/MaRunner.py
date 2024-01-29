import socket
import time
import json

class MatoryConnect(object):
    def __init__(self,connectip="127.0.0.1",port=2666,timeout=60,log_flag=False):
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
        response = json.loads(self.udriver.recv(65536).decode())
        print("Receive Data:"+str(response))
        return response

    '''
    发送采集消息模块
    '''
    def ProfilerGather(self,args)->None:
        self.message['FuncName'] = 'Gather_Profiler'
        self.message['FuncArgs'] = ['Gather_Profiler','1',args]
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
    触发一次UI单击操作,通过路径触发
    '''
    def ClickButtonByPath(self,UIPath):
        self.message['FuncName'] = 'ClickOne'
        self.message['FuncArgs'] = ['leftclick',f'{UIPath}','path']
        return self.SendMessageModule(self.message)
    
    '''
    触发一次UI单击操作,通过InstanceId触发
    '''
    def ClickButtonById(self,id):
        self.message['FuncName'] = 'ClickOne'
        self.message['FuncArgs'] = ['leftclick',f'{id}','id']
        return self.SendMessageModule(self.message)
