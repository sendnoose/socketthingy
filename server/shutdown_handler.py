import os
import time
import threading
import traceback
from handler_state import HandlerState

class ShutdownHandler:
    def __init__(self):
        pass

    def Execute(self, reqCode, data):
        try:
            if (data == "S"):
                os.system("shutdown /s /t 3")
                return HandlerState.SUCCEEDED, None
            elif (data == "L"):
                def LogOutIn3():
                    time.sleep(3)
                    os.system("shutdown /l")
                thread = threading.Thread(target=LogOutIn3)
                thread.start()
                return HandlerState.SUCCEEDED, None
            else:
                return HandlerState.INVALID, None

        except Exception as e:
            traceback.print_exc()
            return HandlerState.FAILED, None

if __name__ == '__main__':
    a = ShutdownHandler()
    a.Execute()