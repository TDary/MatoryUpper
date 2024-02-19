from Runner import MaRunner
import traceback
import json
import time
import Init
import argparse

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("-c",help="config file path")  #命令行参数 -c 配置文件地址
        args = parser.parse_args()
        configPath = args.c
        print(Init.LoadConfigFile(configPath))
        # udriver = MaRunner.MatoryConnect("192.168.0.107",2666,60)

        # # res = udriver.GetAllButton()["Data"]
        # # for item in json.loads(res):
        # #     if "LEVEL SELECT" in item["ButtonName"]:
        # #         id = item["InstanceId"]
        # #         udriver.ClickButtonBySimulate(id=id)  #点击UI操作
        # #         break

        # #开始采集
        # uuID = "testcdr"
        # temp_data = {"path":"D:\\files"}
        # collectiondata={"collection": {},"data": {}}
        # collection = {"profiler_gather":json.dumps(temp_data)}
        # collectiondata["collection"]=json.dumps(collection)
        # collectiondata["data"]=json.dumps({"uuid": uuID,"path": "D:\\files\\"})
        # udriver.ProfilerGather(json.dumps(collectiondata))
        # time.sleep(30)
        # udriver.StopProfilerGather()
        # time.sleep(1)
        # udriver.CloseConnect()
    except:
        traceback.print_exception()