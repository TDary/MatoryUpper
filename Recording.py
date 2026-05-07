from Runner import MaRunner
from Matory.Command import UIRecordController
import traceback
import argparse
import threading

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("-i", help="ip address")
        args = parser.parse_args()
        ip = args.i or ""
        udriver = MaRunner.MatoryConnect(connectip=ip, port=2666, timeout=60)

        stop_event = threading.Event()
        controller = UIRecordController(udriver)
        record_thread = threading.Thread(target=controller.run, args=(stop_event,), daemon=True)
        record_thread.start()

        stop_event.wait()

        udriver.CloseConnect()
        print("程序退出")
    except KeyboardInterrupt:
        pass
    except:
        traceback.print_exc()
        udriver.CloseConnect()