from Runner import MaRunner
import traceback
import json
import argparse
import time
from DataGathers import StaticData

if __name__ == "__main__":
    try:

        parser = argparse.ArgumentParser()
        parser.add_argument("-i", help="ip address")  #命令行参数 -i ip地址
        args = parser.parse_args()
        ip = args.i or ""
        udriver = MaRunner.MatoryConnect(connectip=ip,port=2666,timeout=60)

        udriver.CustomGM("PlayEffect","skillfx1_5","2")
        time.sleep(3)
        udriver.CloseConnect()
    except:
        traceback.print_exception()