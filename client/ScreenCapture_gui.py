import tkinter

class Screenshot:
    def capScreen(self):
        print('cap')

    def savePic(self):
        print('saved')

    def pic(self):
        pic = tkinter.Tk()
        pic.geometry("500x420")
        pic.title("pic")

        pic_canvas = tkinter.Canvas(pic)
        pic_canvas.place(x = 15, y = 25, height = 380, width = 380)

        pic_button1 = tkinter.Button(pic, text = "Chụp", command = self.capScreen)
        pic_button1.place(x = 400, y = 25 , height = 260, width = 90)

        pic_button2 = tkinter.Button(pic, text = "Lưu", command = self.savePic)
        pic_button2.place(x = 400, y = 310 , height = 95, width = 90)

        pic.mainloop()
