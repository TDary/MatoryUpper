import json

# 加载读取配置文件json
def LoadConfigFile(jsonPath: str):
    with open(jsonPath, "r", encoding="utf-8") as f:
        ConfigData = json.load(f)
    return ConfigData
