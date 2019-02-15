import tkinter as tk
from tkinter import *

def hello(t):

    for i in range(3):
        Label(t,text="Done").grid(row=i)
        e=Entry(t)
        e.grid(row=i,column=1)

root=tk.Tk()
btn=tk.Button(root,text="Hello",command=hello(root))

root.mainloop()