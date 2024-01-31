from Runner import MaRunner
import traceback
import json
import argparse
import time

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("-i", help="ip")  #命令行参数 -i ip地址
        parser.add_argument("-s", help="devices serial")  #命令行参数 -s 设备号

        args = parser.parse_args()
        ip = args.i or ""
        device = args.s or ""

        udriver = MaRunner.MatoryConnect(device=device,connectip=ip,port=2666,timeout=60)

        filepath = "D:/testfirst.snap"
        res = udriver.TakeMemorySnapShot("All",filepath)

        # res = udriver.GetAllButton()["Data"]
        # for item in json.loads(res):
        #     if "LEVEL SELECT" in item["ButtonName"]:
        #         id = item["InstanceId"]
        #         udriver.ClickButtonBySimulate(id=id)  #点击UI操作
        #         break

        #开始采集
        # uuID = "testcdr"
        # temp_data = {"path":"E:/files"}
        # collectiondata={"collection": {},"data": {}}
        # collection = {"profiler_gather":json.dumps(temp_data)}
        # collectiondata["collection"]=json.dumps(collection)
        # collectiondata["data"]=json.dumps({"uuid": uuID,"path": "E:/files/"})
        # udriver.ProfilerGather(json.dumps(collectiondata))
        # time.sleep(30)
        # udriver.StopProfilerGather()
        time.sleep(1)
        udriver.CloseConnect()
    except:
        traceback.print_exception()