import json
import Runner.MaRunner

# 加载读取配置文件json
def LoadConfigFile(jsonPath:str):
    with open(jsonPath,"r",encoding="utf-8") as f:
        # print(type(f))
        ConfigData = json.load(f)
        f.close()
    return ConfigData