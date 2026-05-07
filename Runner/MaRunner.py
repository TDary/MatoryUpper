import socket
import time
import json
from Runner import *

class MatoryConnect(object):
    def __init__(self, device="", connectip="127.0.0.1", port=2666, timeout=60, log_flag=False):
        '''
        :param connectip: Hostname of a socket service.
        :param port: TCP Port of machine.
        '''
        self.TCP_IP = connectip
        self.TCP_PORT = port
        self.connect = False
        self.udriver = None
        self.log_flag = log_flag

        original_timeout = timeout
        connect_timeout = 5
        while timeout > 0:
            try:
                self.udriver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.udriver.settimeout(connect_timeout)

                for p in range(self.TCP_PORT, self.TCP_PORT + 5):
                    try:
                        self.udriver.connect((connectip, p))
                        self.TCP_PORT = p
                        break
                    except ConnectionRefusedError:
                        print(f"连接{p}失败，尝试下一个端口")

                self.udriver.settimeout(original_timeout)
                self.connect = True
                time.sleep(1)
                print("获取SDK版本号——")
                print("Sdk Version:" + self.GetServerVersion()["Data"])
                break
            except Exception as e:
                print(e)
                print('MatoryServer not running on port ' + str(self.TCP_PORT) +
                      ', retrying (timing out in ' + str(timeout) + ' secs)...')
                time.sleep(connect_timeout)
                timeout -= connect_timeout

        if timeout <= 0:
            raise Exception('Connecting Timeout，Could not connect to MatoryServer on: ' + self.TCP_IP + ':' + str(self.TCP_PORT))

    def _build_message(self, func_name, func_args=None):
        """构建消息字典，避免共享实例变量导致竞态条件"""
        return {
            'FuncName': func_name,
            'FuncArgs': func_args or []
        }

    def _recv_full_response(self):
        """循环接收直到拿到完整 JSON，避免 64KB 截断"""
        chunks = []
        while True:
            data = self.udriver.recv(65536).decode()
            if not data:
                raise ConnectionError("Socket connection closed by remote end while receiving response")
            chunks.append(data)
            try:
                json.loads("".join(chunks))
                return "".join(chunks)
            except json.JSONDecodeError:
                continue

    def SendMessageModule(self, message):
        msg = json.dumps(message)
        if self.log_flag:
            print("Send Msg:" + msg)
        self.udriver.sendall(msg.encode())
        resData = self._recv_full_response()
        if self.log_flag:
            print("Receive Data:" + str(resData))
        response = json.loads(resData)
        return response

    def ProfilerGather(self, args):
        return self.SendMessageModule(self._build_message('Gather_Profiler', ['Gather_Profiler', '1', args]))

    def StopProfilerGather(self):
        return self.SendMessageModule(self._build_message('Gather_Profiler', ['Gather_Profiler', '0']))

    def CloseConnect(self) -> None:
        self.udriver.close()

    def GetServerVersion(self):
        return self.SendMessageModule(self._build_message('GetSdkVersion'))

    def GetGameVersion(self):
        return self.SendMessageModule(self._build_message('GetGameVersion'))

    def FindText(self, textname: str):
        return self.SendMessageModule(self._build_message('Find_Text', [textname]))

    def GetAllButton(self):
        return self.SendMessageModule(self._build_message('Find_AllButton'))

    def CheckProfiler(self):
        return self.SendMessageModule(self._build_message('Check_Profiler'))

    def GetProjectHierarchy(self):
        return self.SendMessageModule(self._build_message('Get_Hierarchy'))

    def GetProjectInspector(self, objId: int):
        return self.SendMessageModule(self._build_message('Get_Inspector', [str(objId)]))

    def ClickButtonByPath(self, UIPath: str):
        return self.SendMessageModule(self._build_message('ClickOne', ['click', UIPath, 'path']))

    def ClickButtonById(self, id: int):
        return self.SendMessageModule(self._build_message('ClickOne', ['click', str(id), 'id']))

    def ClickButtonBySimulate(self, id: int):
        return self.SendMessageModule(self._build_message('ClickOneBySimulate', ['left', str(id)]))

    def TakeMemorySnapShot(self, type: str, filePath: str):
        return self.SendMessageModule(self._build_message('CaptureMemorySnap', [type, filePath]))

    def TakeGameScreenCapture(self, filePath: str):
        return self.SendMessageModule(self._build_message('GetScreenShot', [filePath]))

    def CustomGM(self, *value):
        gmargs = list(value)
        return self.SendMessageModule(self._build_message('gm', gmargs))

    def SetGameObjectState(self, objectname: str, value: bool):
        return self.SendMessageModule(self._build_message('SetGameObjectState', [objectname, str(value)]))

    def StartPerfData(self, outputpath: str, sample_arg: int):
        return self.SendMessageModule(self._build_message('PerformanceData_Start', [outputpath, str(sample_arg)]))

    def StopPerfData(self):
        return self.SendMessageModule(self._build_message('PerformanceData_Stop'))

    def GetOnePerfData(self):
        return self.SendMessageModule(self._build_message('PerformanceData_GetOne'))

    def StartUIRecord(self):
        return self.SendMessageModule(self._build_message('Start_UIRecord'))

    def StopUIRecord(self):
        return self.SendMessageModule(self._build_message('Stop_UIRecord'))

    def StartDTrace(self):
        return self.SendMessageModule(self._build_message('Start_DTracker'))

    def SetDTracePath(self, filePath: str, maxMemory: float):
        return self.SendMessageModule(self._build_message('Set_DTrackerLimit', [filePath, str(maxMemory)]))
