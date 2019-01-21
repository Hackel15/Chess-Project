from tkinter import Tk, Label, Button
import threading
import time

class StatusChecker(threading.Thread):
    """
    The thread that will check player moves
    """
    def __init__(self, n):
        super().__init__()
        self.n = n

    def run(self):
        t = int(time.time())
        while (t % 2 == 0):
            print ("Thread " + str(self.n) + ": odd time")
            t = int(time.time())
        
class MyFirstGUI:
    def __init__(self, master):
        self.count = 0
        self.master = master
        master.title("A simple GUI")

        self.label = Label(master, text="This is our first GUI!")
        self.label.pack()

        self.greet_button = Button(master, text="Greet", command=self.greet)
        self.greet_button.pack()

        self.close_button = Button(master, text="Close", command=master.quit)
        self.close_button.pack()

        self.openTimeThread_button = Button(master, text="Get Time", command=self.runThread)
        self.openTimeThread_button.pack()

    def greet(self):
        print("Greetings!")

    def runThread(self):
        thread = StatusChecker(self.count)
        thread.start()
        
        del(thread)
        self.count+=1
          

root = Tk()
my_gui = MyFirstGUI(root)
root.mainloop()
root.quit()
