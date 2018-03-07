#!/usr/bin/env python3
# Integrate VLC Window in main Window
# Add Icon to all Buttons
# TopLevel window on top always
# Display & Live Edit Dirlist.ini file
# Undo last operation Button

import os,sys
import time
from tkinter import Label, Tk, Frame, Button, messagebox, StringVar, Radiobutton, filedialog, Entry, GROOVE, RIDGE, Scrollbar, VERTICAL, Listbox, E, W, N, NW, END, Toplevel, Menu
from tkinter.ttk import Progressbar
import subprocess
import shutil
from send2trash import send2trash
import psutil

root = Tk()

# Main Frame
frame = Frame(root, height=800, width=700, bd=3, relief=RIDGE)
frame.grid()

# Sub Frames
frame1 = Frame(frame, height=50, width=500, bd=3, relief=GROOVE)
frame1.grid(row=0, column=0, columnspan=2, sticky=NW)

frame3 = Frame(frame, height=300, width=400, bd=3, relief=GROOVE)
frame3.grid(row=1, column=0, sticky=N)

frame4 = Frame(frame, height=300, width=100, bd=3, relief=GROOVE)
frame4.grid(row=0, column=1, rowspan=2, sticky=N)

# Output Logs Box
scrollbar = Scrollbar(frame3, orient=VERTICAL, cursor='sb_v_double_arrow')
listbox = Listbox(frame3, height=40, width=63, yscrollcommand=scrollbar.set)
listbox.xview_scroll(3, "pages")
listbox.yview_scroll(3, "pages")
scrollbar.config(command=listbox.yview)
listbox.grid(row=0, column=0)
scrollbar.grid(row=0, column=1, sticky=E, ipady=288)


# Variables
array,playlist,MODES = [],[],[]
m,d,curr = 0,0,0

# Populate Directory List
try:
    array = [line.rstrip('\n') for line in open('dirlist.ini')]
except FileNotFoundError:
    print("Error: dirlist.ini not found. Please create the file.")
    sys.exit()

for i in range(len(array)):
    MODES.append(array[i].split('\t'))

def filesize(file):
    size = os.path.getsize(file)
    sizeinmb = size/1000000
    sizeflt = "{:.2f}".format(sizeinmb)
    return sizeflt

def lb(text):
    listbox.insert(END, text)
    listbox.yview(END)

# Various Functions
def browse():
    try:
        global playlist, current, d, m
        playlist = []
        current,d,m = 0,0,0
        try:
            dir = filedialog.askdirectory(parent=frame, initialdir='/data/.folder/', title='Please select a directory')
        except:
            dir = filedialog.askdirectory(parent=frame, initialdir=os.getcwd(), title='Please select a directory')
        en.delete(0,END)
        en.insert(0,dir)
        for filename in os.listdir(en.get()):
                if os.path.isfile(os.path.join(en.get(), filename)):
                    playlist.append(os.path.join(en.get(), filename))
        lb("Total no of Files: "+str(len(playlist)))
    except FileNotFoundError:
        lb("Error: Directory not selected")
    lb("")

def openfolder():
    if en.get():
        if os.path.isdir(en.get()):
            path = 'nautilus "%s"' %en.get()
            subprocess.Popen(path, shell=True)
            lb("Directory opened: "+en.get())
        else:
            lb("Error: Directory does not exists")
    else:
        lb("Error: Directory not selected")
    lb("")

def ls_dir():
    if en.get():
        count = [name for name in os.listdir(en.get()) if os.path.isfile(os.path.join(en.get(), name))]
        if (len(count)==0):
            lb("Error: No Files in Directory")
        else:
            lb("File List:")
            for i in range(len(count)):
                lb(str(i+1)+ ". " + count[i] + " " + "["+ filesize(en.get()+"/"+count[i]) + "MB" + "]")
    else:
        lb("Error: Directory not selected")
    lb("")

def stats():
    try:
        count = len([name for name in os.listdir(en.get()) if os.path.isfile(os.path.join(en.get(), name))])
    except:
        count = "No Files"
    lb("File Operation Stats:")
    lb("Initial Count: "+str(len(playlist)))
    lb("Current Count: "+str(count))
    lb("Deleted: "+str(d))
    lb("Moved: "+str(m))
    lb("")

def play(delta):
    global current
    if en.get():
        if not (0 <= current + delta < len(playlist)):
            lb("Info: End of Playlist")
            lb("")
            bar['value'] = 100
            return
        current += delta
        song = 'vlc -q "%s" 2> /dev/null' %playlist[current]
        if os.path.isfile(playlist[current]):
            lb(str(current+1)+": "+"VLC: "+playlist[current]+ " " + "["+ filesize(playlist[current]) + "MB" + "]")
            bar['value'] = int((current/len(playlist))*100)
            subprocess.Popen(song, shell=True)
        else:
            lb("Error: File not found: "+(playlist[current]).split('/')[-1])
            lb("")
    else:
        lb("Error: Directory not selected")
        lb("")

def move(mode):
    if en.get():
        if os.path.isdir(mode):
            try:
                if os.path.isfile(playlist[current]):
                    frame4.config(cursor="watch")
                    frame4.update()
                    shutil.move(playlist[current], mode)
                    lb("Moved: "+playlist[current]+" => "+mode)
                    lb("")
                    frame4.config(cursor="")
                    global m
                    m += 1
                    play(+1)
                else:
                    lb("Error: Source file does not exist: "+(playlist[current]).split('/')[-1])
            except shutil.Error:
                lb("Error: "+(playlist[current]).split('/')[-1]+": already exists at destination: "+mode)
                frame4.config(cursor="")
            except FileNotFoundError:
                lb("Error: File not found: "+(playlist[current]).split('/')[-1])
                frame4.config(cursor="")
        else:
            lb("Error: Directory does not exist: "+mode)
    else:
        lb("Error: Directory not selected")
    lb("")

def movedir():
    if en.get():
        if os.path.isdir(v.get()):
            res1 = messagebox.askyesno('Confirmation','Do you want to Move all files?')
            if res1:
                try:
                    frame4.config(cursor="watch")
                    frame4.update()
                    shutil.move(en.get(), v.get())
                    frame4.config(cursor="")
                    lb("Moved: "+en.get()+" => "+v.get())
                except shutil.Error:
                    lb("Error: "+en.get()+": already exists at destination: "+v.get())
            else:
                lb("Info: Operation to delete all files cancelled")
        else:
            lb("Error: Directory does not exist: "+v.get())
    else:
        lb("Error: Directory not selected")
    lb("")

def delete():
    if en.get():
        send2trash(playlist[current])
        lb("Deleted: "+playlist[current])
        lb("")
        global d
        d += 1
        play(+1)
    else:
        lb("Error: Directory not selected")
    lb("")

def deleteall():
    if en.get():
        res2 = messagebox.askyesno('Confirmation','Do you want to Delete all files?')
        if res2:
            lb("Deleted All files: ")
            for i in range(len(playlist)):
                 try:
                     send2trash(playlist[i])
                     lb(" -  "+playlist[i])
                     global d
                     d += 1
                 except:
                     lb(" -  "+"Already Deleted: "+playlist[i])
        else:
            lb("Info: Operation to delete all files cancelled")
    else:
        lb("Error: Directory not selected")
    lb("")

def del_dir():
    if en.get():
        try:
            if os.listdir(en.get()) == []:
                os.rmdir(en.get())
                lb("Directory Deleted: "+ en.get())
            else:
                lb("Directory not empty: Contains "+ str(len(os.listdir(en.get()))) + " files")
        except FileNotFoundError:
            lb("Error: Directory not found, probably already deleted")
    else:
        lb("Error: Directory not selected")
    lb("")

def clear():
    listbox.delete(0, END)

def exit():
    for proc in psutil.process_iter():
        if proc.name() == "vlc":
            proc.kill()
    root.quit()

def browse2():
    try:
        dir = filedialog.askdirectory(parent=frame, initialdir='/media/system/Data/Vids/', title='Please select a directory')
    except:
        dir = filedialog.askdirectory(parent=frame, initialdir=os.getcwd(), title='Please select a directory')    
    en3.delete(0,END)
    en3.insert(0,dir)

def save():
    if en2.get() and en3.get():
        f = open('dirlist.ini','a')
        f.write(en2.get()+"\t"+en3.get()+"\r")
        f.close()
        lb("Saved Directory: "+en2.get()+" "+en3.get())
    else:
        lb("Error: Directory/Name not selected")
    lb("")

def delentry():
    f = open('dirlist.ini','r')
    l = f.readlines()
    if en4.get():
        n = int(en4.get())-1
    else:
        lb("Error: Number not entered")
        return
    try:
        lb("Removing Listed Directory: " + l[n])
        line = l[0:n] + l[n+1:]
        f.close()
        f2 = open('dirlist.ini','w')
        for i in line:
            f2.write(i)
        f2.close()
    except IndexError:
        lb("Error: Invalid Number Entered")
    lb("")

def vmode(delta):
    global curr
    if not (0 <= curr + delta < len(MODES)):
        lb("Info: End of Directory List")
        lb("")
        return
    curr += delta
    v.set(MODES[curr][1])

# Keyboard Binding related functions
def playnext(event):
    play(+1)

def playprev(event):
    play(-1)
    
def playcurr(event):
    play(0)

def br(event):
    browse()

def mv(event):
    move()

def delt(event):
    delete()

def modeup(event):
    vmode(-1)
    
def modedown(event):
    vmode(+1)

def about():
    lb("Email: amanjosan2008@gmail.com")


#Save Directory list Section
def dirlist():
    win1 = Toplevel()
    win1.title("Directory Operations")
    win1.geometry('600x130')

    frame5 = Frame(win1, height=800, width=700, bd=3, relief=GROOVE)
    frame5.grid()

    frame6 = Frame(win1, height=800, width=700, bd=3, relief=GROOVE)
    frame6.grid()

    Label(frame5, text="Insert Directory").grid(row=0, column=0, rowspan=1, columnspan=8)

    global en2, en3, en4
    en2 = Entry(frame5, width=10)
    en2.grid(row=1, column=0, rowspan=1, columnspan=1, sticky=W)

    en3 = Entry(frame5, width=40)
    en3.grid(row=1, column=1, rowspan=1, columnspan=4, sticky=W)

    Button(frame5, text="Browse", command=browse2).grid(row=1, column=5, rowspan=1, columnspan=1, ipadx=10)
    Button(frame5, text="Save", command=save).grid(row=1, column=6, rowspan=1, columnspan=1, ipadx=10)

    Label(frame6, text="Remove Directory").grid(row=2, column=0, rowspan=1, columnspan=8)
    en4 = Entry(frame6, width=10)
    en4.grid(row=3, column=0, rowspan=1, columnspan=1, sticky=W)

    Button(frame6, text="Del Entry", command=lambda: delentry()).grid(row=3, column=1, rowspan=1, columnspan=1, ipadx=10)
    Button(frame6, text='Quit', command=win1.destroy).grid(row=3, column=6, rowspan=1, columnspan=1, ipadx=15)

# Menu Configuration
menu = Menu(frame)

item1 = Menu(menu, tearoff=0)
item1.add_command(label='Browse', command=browse)
item1.add_command(label='Explore', command=openfolder)
item1.add_separator()
item1.add_command(label='Exit', command=exit)

item2 = Menu(menu, tearoff=0)
item2.add_command(label='Edit Dirlist', command=dirlist)
item2.add_separator()
item2.add_command(label='Move Dir', command=movedir)
item2.add_command(label='Delete All', command=deleteall)
item2.add_command(label='Delete Dir', command=del_dir)

item3 = Menu(menu, tearoff=0)
item3.add_command(label='List Files', command=ls_dir)
item3.add_command(label='Stats', command=stats)
item3.add_command(label='Clear Logs', command=clear)

item4 = Menu(menu, tearoff=0)
item4.add_command(label='About', command=about)

menu.add_cascade(label='File', menu=item1)
menu.add_cascade(label='Operations', menu=item2)
menu.add_cascade(label='Options', menu=item3)
menu.add_cascade(label='Help', menu=item4)

root.config(menu=menu)

# Buttons Config:
Button(frame1, text='Play (\u23CE)',  command=lambda: play(0), width=7).grid(row=0, column=0)
Button(frame1, text='Prev (\u2190)', command=lambda: play(-1), width=7).grid(row=0, column=1)
Button(frame1, text='Next (\u2192)', command=lambda: play(+1), width=7).grid(row=0, column=2)

# Entry Box
en = Entry(frame1)
en.grid(row=0, column=3, columnspan=4, sticky=W, ipadx=50)

# Directory buttons
v = StringVar()

i = 0
try:
    for text, mode in MODES:
        b = Button(frame4, text=text, textvariable=mode, command=lambda mode=mode: move(mode), width=10)
        b.grid(row=i, sticky=W)
        i += 1
except ValueError:
    lb("Error: Data in Dirlist.ini not correctly formatted")

if i ==0:
    lb("Error: No Directories found in Dirlist.ini")

# Buttons with Directory operations
Button(frame4, text='Delete (X)', command=lambda: delete(), width=10, fg="red").grid(row=i+1)
#Button(frame4, text='Move Dir', command=lambda: movedir(), width=10, fg="red").grid(row=i+2)
#Button(frame4, text='Del All', command=lambda: deleteall(), width=10, fg="red").grid(row=i+3)
#Button(frame4, text='Del Dir', command=lambda: del_dir(), width=10, fg="red").grid(row=i+4)

lb("Ready, Log Output:")
lb("")

# Progress Bar
bar = Progressbar(frame3, length=450)
bar.grid(row=1)

# Validate Directories
try: 
    for i in range(len(MODES)):
        if os.path.exists(MODES[i][1]):
            pass
        else:
            lb("Error: Directory does not exist: "+MODES[i][0]+" - "+MODES[i][1])
    lb("")
except:
    pass

#root.geometry('830x450')
root.title("Video Collection Manager")
root.bind('<Return>', playcurr)
root.bind('<Left>', playprev)
root.bind('<Right>', playnext)
root.bind('z', mv)
root.bind('x', delt)
root.bind('b', br)
root.bind('<Up>', modeup)
root.bind('<Down>', modedown)

try:
    img = PhotoImage(file='icon.png')
    root.tk.call('wm', 'iconphoto', root._w, img)
except:
    lb("icon.png file not found")

root.mainloop()

