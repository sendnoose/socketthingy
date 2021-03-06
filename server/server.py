import socket
import os
import time
import traceback
from pathlib import Path

from handler_state import HandlerState
from directory_handler import DirectoryHandler
from screen_handler import ScreenHandler
from info_handler import InfoHandler
from livestream_handler import LivestreamHandler
from shutdown_handler import ShutdownHandler
from process_handler import ProcessHandler
from application_handler import ApplicationHandler
from input_handler import InputHandler
from registry_handler import RegistryHandler

HEADER = 64
FORMAT = "utf-8"

HOST = "0.0.0.0"
PORT = 6666
BACKLOG = 1

KEYLOG_FILE_PATH = os.path.join(Path(__file__).parent.absolute(),"logged_key.txt")

class ServerProgram:
    QUIT_PROGRAM = 0
    CONTINUE_PROGRAM = 1

    def __init__(self):
        self.currHandler = None

        # Only accepts one client
        self.clientSocket = None
        self.address = None
        self.connected = False

    def __del__(self):
        if self.serverSocket != None:
            self.serverSocket.close()
        if self.clientSocket != None:
            self.clientSocket.close()

    def OpenServer(self, host=HOST, port=PORT, backlog=BACKLOG):
        '''Open the server at (host, port) for backlog ammount of unaccepted connections
        Parameters:
            host (str): host part
            port (int): port
            backlog (int): backlog number
        '''
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.currHandler = None
        self.serverSocket.bind((host, port))
        self.serverSocket.listen(backlog)
        self.clientSocket, self.address = self.serverSocket.accept()
        self.connected = True
        print(f'Connected to {self.address}')

    def CloseServer(self):
        '''Close the server associated with the program and close the clientSocket'''
        self.connected = False
        self.serverSocket.close()
        self.clientSocket.close()
        self.clientSocket = self.address = None

    def Run(self):
        '''
        Enable the main loop of the Program, enable the Program to receive and handle messages from client
         via the client socket.
        Can only be called when A client is connected
        '''
        if not self.clientSocket:
            print("No client is connected, exitting")

        while True:
            req = self.ReceiveMessage()
            if not req:
                print("No messages sent")
                time.sleep(0.5)
                self.CloseServer()
                break
            state = self.HandleRequest(req)

            if state == ServerProgram.QUIT_PROGRAM:
                time.sleep(0.5)
                self.CloseServer()
                break

    def ReceiveMessage(self):
        '''
        Receive messages send through client socket, blocking the program/thread.
        Returns:
            str: if any message is received.
            None: if any errors occur or no message is received
        '''
        try:
            message_length = self.clientSocket.recv(HEADER).decode(FORMAT)
            if message_length:
                length = int(message_length)
                bytesReceived = 0
                chunks = []
                while bytesReceived < length:
                    message = self.clientSocket.recv(length - bytesReceived)
                    bytesReceived += len(message)
                    chunks.append(message)

                message = b''.join(chunks)
                return message
        except Exception as e:
            traceback.print_exc()

        return None

    def SendMessage(self, string, byteData=None):
        '''
        Send a message to client
        Parameters:
            string (str): the request
            binaryData (bytes, None): additional data in binary form, will be attatched to the request, separate by a single b' '
        Returns:
            True: if the message is sent properly
            False: if any errors occurs
        '''
        try:
            req = string.encode(FORMAT)
            if byteData:
                req += b' ' + byteData

            length = len(req)
            header = str(length).encode(FORMAT)
            header += b' ' * (HEADER - len(header))

            bytes_sent = self.clientSocket.send(header)
            assert bytes_sent == HEADER, "Length of message sent does not match that of the actual message"

            bytes_sent = self.clientSocket.send(req)
            assert bytes_sent == length, "Length of message sent does not match that of the actual message"

            return True
        except Exception as e:
            traceback.print_exc()

        return False

    def HandleRequest(self, byteRequest):
        '''
        Handle request sent by client.
        Request is handled, then passed to SendMessage to send a reply with appropriate data to client, this step is blocking.
        Parameters:
            requestString (str): the reqeust string
        Returns:
            int: either ServerProgram.CONTINUE or ServerProgram.QUIT_PROGRAM
        '''
        immediate = False
        request, data = self.SplitRequest(byteRequest)

        state = HandlerState.INVALID
        extraInfo = None

        if (type(self.currHandler) != DirectoryHandler or request != "TRANSFER") and data:
            data = data.decode(FORMAT)
            
        print(request, data if data and len(data) < 512 else (len(data) if data else ''))
        # FINISH request exits the current handler
        # EXIT request finishes the program
        if request == "FINISH":
            if self.currHandler:
                self.currHandler = None
                state = HandlerState.SUCCEEDED
            else:
                self.SendMessage("INVALID", None)
        elif request == "EXIT":
            self.currHandler = None
            self.SendMessage("SUCCEEDED", None)
            return ServerProgram.QUIT_PROGRAM
        # If no handler is currently active
        elif not self.currHandler:
            # SHUTDOWN and SCREENSHOT are immeditate handlers
            if request == "SHUTDOWN":
                self.currHandler = ShutdownHandler()
                immediate = True
            elif request == "SCREENSHOT":
                self.currHandler = ScreenHandler()
                immediate = True
            elif request == "INFO":
                self.currHandler = InfoHandler()
                immediate = True
            # The rest needs additional requests and looping
            else:
                immediate = False
                state = HandlerState.SUCCEEDED
                if request == "PROCESS":
                    self.currHandler = ProcessHandler()
                elif request == "APPLICATION":
                    self.currHandler = ApplicationHandler()
                elif request == "KEYLOG":
                    self.currHandler = InputHandler(KEYLOG_FILE_PATH)
                elif request == "REGISTRY":
                    self.currHandler = RegistryHandler()
                elif request == "DIRECTORY":
                    self.currHandler = DirectoryHandler()
                elif request == "LIVESTREAM":
                    self.currHandler = LivestreamHandler(self, self.serverSocket, ScreenHandler())

        # Else let current handler handle request
        else:
            state, extraInfo = self.currHandler.Execute(request, data)

        if self.currHandler and immediate:
            state, extraInfo = self.currHandler.Execute("", data)
            self.currHandler = None
            immediate = False

        print(state, extraInfo if extraInfo and len(extraInfo) < 512 else (len(extraInfo) if extraInfo else ''))

        if request == "SHUTDOWN" and state == HandlerState.SUCCEEDED:
            self.SendMessage("SUCCEEDED", extraInfo)
            return ServerProgram.QUIT_PROGRAM

        if state == HandlerState.SUCCEEDED:
            self.SendMessage("SUCCEEDED", extraInfo)
        elif state == HandlerState.FAILED:
            self.SendMessage("FAILED", extraInfo)
        else:
            self.SendMessage("INVALID", extraInfo)

        return ServerProgram.CONTINUE_PROGRAM

    def SplitRequest(self, byteRequest):
        '''
        Split a byteRequest request into 2 part: base request and extraData
        Parameters:
            byteRequest (bytes): a string request
        Returns:
            (str | None, bytes | None): 2 strings if request is splitable, 1 string if not and (None, None) if request is empty
        '''
        byteRequest = byteRequest.strip()
        a = byteRequest.split(b' ', 1)
        if len(a) == 2:
            return a[0].decode(FORMAT), a[1]
        elif len(a) == 1:
            return a[0].decode(FORMAT), None
        else:
            return None, None


if __name__ == "__main__":
    program = ServerProgram()
    program.OpenServer(HOST, PORT, BACKLOG)
    program.Run()