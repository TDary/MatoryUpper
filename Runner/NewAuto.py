import time
import socket
import traceback
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
                GetServerVersion(self.udriver)

                response = self.udriver.recv(2048)
                print(response)
            except Exception as e:
                print(e)
                print('MatoryServer not running on port ' + str(self.TCP_PORT) +
                      ', retrying (timing out in ' + str(timeout) + ' secs)...')
                timeout -= timeout
                # time.sleep(timeout)

        if timeout <= 0:
            raise Exception('Could not connect to MatoryServer on: '+ self.TCP_IP +':'+ str(self.TCP_PORT))

    def ProfilerGather(self,args)->None:
        message = {
            'FuncName':'Gather_Profiler',
            'FuncArgs':['Gather_Profiler','1',args]
        }
        msg = json.dumps(message)
        self.udriver.sendall(msg.encode())

    def CloseConnect(self)->None:
        self.udriver.close()

def GetServerVersion(self)->None:
    message = {
        'FuncName':'GetSdkVersion',
        'FuncArgs':[]
    }
    msg = json.dumps(message)
    self.udriver.sendall(msg.encode())


if __name__ == "__main__":
    try:
        udriver = MatoryConnect("10.11.144.31",2666,60)

        # time.sleep(1)
        # message = {
        #     'FuncName':'GetSdkVersion',
        #     'FuncArgs':[]
        # }
        # msg = json.dumps(message)
        # udriver.sendall(msg.encode())

        #开始采集
        # uuID = "testcdr"
        # temp_data = {}
        # collectiondata={
        #         "collection": { #"ubox": {}
        #         },"data": {#"uuid": uuID,"path": "E:/CollectData"
        #         }}
        # collection = {"profiler_gather":{}}
        # collectiondata["collection"]=json.dumps(collection)
        # collectiondata["data"]=json.dumps({"uuid": uuID,"path": "E:\\rawdata\\"})
        # udriver.ProfilerGather(json.dumps(collectiondata))

        # response = udriver.recv(2048)
        # print(response)
        # udriver.CloseConnect()
    except:
        traceback.print_exception()