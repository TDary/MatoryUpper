from Runner.MaRunner import MatoryConnect
import traceback

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