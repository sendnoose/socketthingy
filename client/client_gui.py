import tkinter
from tkinter.messagebox import showinfo

from client import ClientState
from client import ClientProgram

from ProcessRunning_gui import ProcessRunning, ApplicationRunning
from Keystroke_gui import Keystroke
from Registry_gui import Registry
from ScreenCapture_gui import Screenshot

# def remove_text(event):
#     event.widget.delete(0, "end")

class ClientGUI():
    def __init__(self):   
        self.clientProgram = ClientProgram()
        self.process_gui = ProcessRunning(self.clientProgram)
        self.app_gui = ApplicationRunning(self.clientProgram)
        self.keystroke_gui = Keystroke(self.clientProgram)
        self.registry_gui = Registry(self.clientProgram)
        self.screenshot_gui = Screenshot(self.clientProgram)
        pass

    def Connect(self, host):
        state = self.clientProgram.Connect(host)
        if state == True:
            showinfo(title = '', message = 'Kết nối đến server thành công')
        else:
            showinfo(title = '', message = 'Lỗi kết nối đến server')

    def Disconnect(self):
        state = self.clientProgram.Disconnect()
        # handle error?

    def OnShutdownButton(self):
        state, _ = self.clientProgram.MakeRequest("SHUTDOWN")
        if state == ClientState.SUCCEEDED:
            # Bên server chuẩn bị tắt máy thì client mình làm gì nhỉ
            pass
        else:
            #Handle, in không thể liên lạc với server chẳng hạn
            pass

    def OnExitButton(self):
        # Ngắt kết nối
        state, _ = self.clientProgram.MakeRequest("EXIT")
        if state == ClientState.SUCCEEDED:
            self.Disconnect()
            pass
        else:
            
            pass
        self.MainWindow.destroy()

    def ShowWindow(self):
        self.MainWindow = tkinter.Tk()
        self.MainWindow.title("Client")

        self.MainWindow.geometry("470x400")

        IPBox = tkinter.Entry(self.MainWindow)
        IPBox.insert(0, "Nhập IP")
        # self.clientgui_textbox.bind("<Button-1>", remove_text)
        IPBox.place(x = 10, y = 20, height = 25, width = 300)
        
        clientgui_button1 = tkinter.Button(self.MainWindow, text = 'Kết nối', command = lambda: self.Connect(IPBox.get()))
        clientgui_button1.place(x = 320, y = 20, height = 25, width = 120)

        clientgui_button2 = tkinter.Button(self.MainWindow, text = 'Process Running', wraplength = 60, command = self.process_gui.OnStartGUI)
        clientgui_button2.place(x = 10, y = 65, height = 300, width = 100)

        clientgui_button3 = tkinter.Button(self.MainWindow, text = 'App Running', command = self.app_gui.OnStartGUI)
        clientgui_button3.place(x = 120, y = 65, height = 100, width = 190)

        clientgui_button4 = tkinter.Button(self.MainWindow, text = 'Tắt máy', wraplength = 30, command = self.OnShutdownButton)
        clientgui_button4.place(x = 120, y = 175, height = 80, width = 70)

        clientgui_button5 = tkinter.Button(self.MainWindow, text = 'Chụp màn hình', command = self.screenshot_gui.OnStartGUI)
        clientgui_button5.place(x = 200, y = 175, height = 80, width = 110)

        clientgui_button6 = tkinter.Button(self.MainWindow, text = 'Sửa registry', command = self.registry_gui.OnStartGUI)
        clientgui_button6.place(x = 120, y = 265, height = 100, width = 250)

        clientgui_button7 = tkinter.Button(self.MainWindow, text = 'Keystroke', command = self.keystroke_gui.OnStartGUI)
        clientgui_button7.place(x = 320, y = 65, height = 190, width = 120)

        clientgui_button8 = tkinter.Button(self.MainWindow, text = 'Thoát', command = self.OnExitButton)
        clientgui_button8.place(x = 380, y = 265, height = 100, width = 60)

        self.MainWindow.mainloop()

if __name__ == '__main__':
    a = ClientGUI()
    a.ShowWindow()