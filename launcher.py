import multiprocessing
import tkinter as tk
from tkinter.constants import *
from tkinter.ttk import *
from tkinter import Menu
from PIL import ImageTk, Image
import os
from tktooltip import ToolTip
from datetime import datetime
import orjson

with open("config.json",'r') as config:
  data = orjson.loads(config.read())

YEAR = datetime.now().year
OWNER = data['owner']
NAME = data['name']
CUSTOM_COLOR = data['custom_color']
DISCORD_DARK = data['discord_dark']
LENGTH = data['length']
WIDTH = data['width']
SCRIPT = data['script']
PHOTO = data['photo']

if __name__ == "__main__":
  l = 0

  processes = []

  for i in range(99):
    command = os.system
    args = f"python3 {SCRIPT}.py"
    processes.append(multiprocessing.Process(target=command,args=(args,)))


  def run_bot():
    global l
    t = processes[l]
    t.start()
    l += 1

  def stop_bot():
    f = open("STOP_SIGN",'w')
    f.close()

  count = 0

  root = tk.Tk()

  style = Style()

  root.title(f"{NAME}")

  root.geometry(f"{WIDTH}x{LENGTH}")

  style.configure('W.TLabel',font=('calibri',8),state='focus',bg=DISCORD_DARK)

  root.resizable(False,False)

  icon = ImageTk.PhotoImage(Image.open("assets/schtabtag.ico"))

  root.iconphoto(False, icon)

  frame=tk.Frame(root,height=600,width=600,bg=DISCORD_DARK)

  frame.place(relwidth=1,relheight=1)

  photo = Image.open(PHOTO)

  photo = photo.resize((300,300), Image.ANTIALIAS)

  photo = ImageTk.PhotoImage(photo)

  thumb = Label(frame,image=photo,background=DISCORD_DARK)

  ind = ImageTk.PhotoImage(Image.open("assets/invisible.png").resize((16,16), Image.ANTIALIAS))

  thumb_ind = Label(frame,image=ind,background=DISCORD_DARK)

  thumb_ind.place(anchor="center",relx=0.5,rely=0.65)

  #thumb.pack(fill='both')
  thumb.place(anchor='center',relx=0.5,rely=0.35)

  status = Label(frame,text="Offline",background=DISCORD_DARK,foreground="white")

  status.place(anchor="center",relx=0.5,rely=0.62)

  credits = Label(frame, text=f"Credits: {OWNER} © {YEAR}",style="W.TLabel",background=DISCORD_DARK,foreground="white")

  credits.place(relx=0.009,rely=0.976)

  def update_ind():
    files = os.listdir()
    for i in files:
      if i == "READY":
        idle = ImageTk.PhotoImage(Image.open("assets/idle.png").resize((16,16), Image.ANTIALIAS))
        thumb_ind.configure(image=idle)
        thumb_ind.image=idle
        status.configure(text="Idle")
        indicator.configure(text=f"{NAME} is Online")
        os.remove("READY")
        break
    root.after(1000,update_ind)

  def start():
    button_start.configure(state=DISABLED)
    button_exit.configure(state=DISABLED)
    button_stop.configure(state=NORMAL)
    indicator.configure(text=f"{NAME} is Getting ready...")
    on = ImageTk.PhotoImage(Image.open("assets/online.png").resize((16,16), Image.ANTIALIAS))
    thumb_ind.configure(image=on)
    thumb_ind.image=on
    filemenu.entryconfig("Start",state=DISABLED)
    filemenu.entryconfig("Exit",state=DISABLED)
    status.configure(text="Online")
    run_bot()
    update_ind()

  def stop():
    button_stop.configure(state=DISABLED)
    button_start.configure(state=NORMAL)
    button_exit.configure(state=NORMAL)
    root.after_cancel(update_ind)
    indicator.configure(text=f"{NAME} is Offline")
    off = ImageTk.PhotoImage(Image.open("assets/invisible.png").resize((16,16), Image.ANTIALIAS))
    thumb_ind.configure(image=off)
    thumb_ind.image=off
    status.configure(text="Offline")
    filemenu.entryconfig("Stop",state=DISABLED)
    stop_bot()

  indicator = Label(frame,text=f"{NAME} is down",background=DISCORD_DARK,foreground="white")

  indicator.place(anchor=CENTER,relx=0.5,rely=0.85)

  button_exit = tk.Button(frame,text="Exit",fg=CUSTOM_COLOR,bg=DISCORD_DARK,relief=SOLID,command=root.destroy,state=NORMAL,width=10,activeforeground=DISCORD_DARK,activebackground=CUSTOM_COLOR,underline=0)

  button_exit.place(anchor=CENTER,relx=0.30,rely=0.9)

  button_stop = tk.Button(frame,text="Stop",fg=CUSTOM_COLOR,bg=DISCORD_DARK,relief=SOLID,command=stop,state=DISABLED,width=10,activeforeground=DISCORD_DARK,activebackground=CUSTOM_COLOR,underline=0)

  button_stop.place(anchor=CENTER,relx=0.5,rely=0.9)

  button_start = tk.Button(frame,text="Start",fg=CUSTOM_COLOR,bg=DISCORD_DARK,relief=SOLID,state=NORMAL,width=10,command=start,activeforeground=DISCORD_DARK,activebackground=CUSTOM_COLOR,underline=0)

  button_start.place(anchor=CENTER,relx=0.70,rely=0.9)

  ToolTip(button_start, msg=f"Start {NAME}",delay=1.0,parent_kwargs={"bg": "black", "padx": 1, "pady": 1},fg="#ffffff", bg="#1c1c1c", padx=1, pady=1)
  ToolTip(button_stop, msg=f"Stop {NAME}",delay=1.0,parent_kwargs={"bg": "black", "padx": 1, "pady": 1},fg="#ffffff", bg="#1c1c1c", padx=1, pady=1)
  ToolTip(button_exit, msg="Exit the application",delay=1.0,parent_kwargs={"bg": "black", "padx": 1, "pady": 1},fg="#ffffff", bg="#1c1c1c", padx=1, pady=1)
    
  menubar = Menu(root,bg=DISCORD_DARK,relief=SOLID,fg="white",activebackground='black',activeforeground='white')
  filemenu = Menu(menubar, tearoff=0,bg=DISCORD_DARK,relief=SOLID,fg='white')
  filemenu.add_command(label="Start", command=start,underline=0)
  filemenu.add_command(label="Stop", command=stop, state=DISABLED,underline=0)
  filemenu.add_separator()
  filemenu.add_command(label="Exit", command=root.destroy,underline=0)
  menubar.add_cascade(label=f"{NAME}", menu=filemenu)


  root.config(menu=menubar)

  root.mainloop()
