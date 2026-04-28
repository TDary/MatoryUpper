import os
import time
import json
import queue
import threading
from Runner import MaRunner
from DataGathers import MinioSdk
from DataGathers import StaticData

# 控制上传模块
def GatherUploadModule(devicetype, stopEvent: threading.Event, udriver: MaRunner.MatoryConnect, gameID, uuID, gatherObj: StaticData.UnityProfile, configData, analyzetype, unityversion, gamename, casename, collectorip):
    # 请求开始采集
    rawfiles = ""
    bucket = configData["minioserver"]["rawbucket"]
    res = gatherObj.SendtoBeginGather(deviceinfo=devicetype, gameID=gameID, uuID=uuID,
                                      unityversion=unityversion, rawfiles=rawfiles, bucketname=bucket,
                                      analyzetype=analyzetype, gamename=gamename, casename=casename, collectorip=collectorip)
    client = MinioSdk.Minio_SDK(url=configData["minioserver"]["url"], bucketName=bucket,
                                access_key=configData["minioserver"]["access_key"], secret_key=configData["minioserver"]["secret_key"])

    # 生产者-消费者 pipeline：压缩与上传并行执行
    task_queue = queue.Queue(maxsize=4)
    fileslist = []

    def producer():
        """扫描文件并压缩入队"""
        while not stopEvent.is_set():
            record = udriver.CheckProfiler()
            if record["Code"] == 200:
                datas = json.loads(record['Data'])
                if datas["profiler_gather"] != "[]":
                    detailData = json.loads(datas["profiler_gather"])
                    for file in detailData:
                        current_timestamp = int(time.time())
                        strcurrent_timestamp = str(current_timestamp)
                        path = os.path.join(file['path'], file['name'] + ".raw")
                        if not os.path.exists(path):
                            print(f"文件 {path} 不存在，跳过当前文件")
                            continue
                        newnamePath = os.path.join(file['path'], strcurrent_timestamp + ".raw")
                        os.rename(path, newnamePath)

                        zipfile_name = strcurrent_timestamp + '.zip'
                        zipfilePath = os.path.join(file['path'], zipfile_name)

                        # 压缩
                        StaticData.Zip_files(newnamePath, zipfilePath)

                        uploadObjectName = uuID + "/" + zipfile_name
                        task_queue.put({
                            'zipfile_name': zipfile_name,
                            'zipfilePath': zipfilePath,
                            'uploadObjectName': uploadObjectName,
                            'rawPath': newnamePath
                        })
            time.sleep(1)
        # 生产结束，发送哨兵值通知消费者退出
        task_queue.put(None)

    def consumer():
        """从队列取任务，上传并请求分析"""
        while True:
            task = task_queue.get()
            if task is None:
                break
            try:
                client.UploadItem(objName=task['uploadObjectName'], filePath=task['zipfilePath'], contentType="application/zip")
                gatherObj.SendtoRequestAnalyze(uuID=uuID, zipfile=task['zipfile_name'],
                                               rawfilename=task['uploadObjectName'],
                                               unityversion=unityversion, analyzebucket=bucket, analyzetype=analyzetype)
                fileslist.append(task['zipfile_name'])
            finally:
                # 清理文件
                if os.path.exists(task['zipfilePath']):
                    os.remove(task['zipfilePath'])
                if os.path.exists(task['rawPath']):
                    os.remove(task['rawPath'])
                task_queue.task_done()

    # 启动 pipeline：1 个生产者 + 1 个消费者
    prod_thread = threading.Thread(target=producer, daemon=True)
    cons_thread = threading.Thread(target=consumer, daemon=True)
    cons_thread.start()
    prod_thread.start()
    prod_thread.join()   # 等待生产者结束
    cons_thread.join()   # 等待队列消费完毕

    # 停止采集，把最后一个源文件记录下来
    if len(fileslist) != 0:
        thelastFile = fileslist[-1]
        res = gatherObj.SendtoStopGather(uuID=uuID, lastfile=thelastFile)
        print("接受停止采集消息：" + res)


# 传绝对路径
def Get_ScreenCapture(captureFilePath, udriver):
    udriver.TakeGameScreenCapture(captureFilePath)
