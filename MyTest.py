from Runner import MaRunner
import traceback
import json
import argparse
import time
# from DataGathers import StaticData

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("-i", help="ip address")  #命令行参数 -i ip地址
        args = parser.parse_args()
        ip = args.i or ""
        udriver = MaRunner.MatoryConnect(connectip=ip,port=2666,timeout=60,log_flag=True)
        # udriver.SetDTracePath("D:/Test.snap","1200")
        # time.sleep(1)
        # udriver.StartDTrace()
        # udriver.SetCameraPosition("27.00,1.00,-46.00","0.00, 0.00, 0.00")
        # udriver.CustomGM("GetTable")
        # udriver.CustomGM("SetMaxMemory","5700")
        # time.sleep(1)
        # udriver.CustomGM("SetSnapPath","D:/myTest.snp")
        # time.sleep(1)
        # udriver.CustomGM("StartMonitor")
        # time.sleep(5)
        # udriver.FindText("选择关卡")
        udriver.ClickButtonByPath("/GameFramework/Builtin/UI/UI Form Instances/UI Group - MainMenu/UILevelSelectForm(Clone)/Levels/Scroll/Layout/LevelSelectionButton(Clone)")
        udriver.CloseConnect()
    except:
        traceback.print_exc()
        udriver.CloseConnect()