from Runner import MaRunner
import traceback
import json
import argparse
import time

if __name__ == "__main__":
    try:
        testList = ["asa","asasasaasas","iamtest"]
        print("".join(testList))
    except:
        traceback.print_exception()