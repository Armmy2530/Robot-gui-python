from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import camera
import cv2
import serial.tools.list_ports

Serial_port = ''
cam_id = 0
running = True
index = 0
arr = []
com_port=[]
com_desc=[]
com_portwithdesc=[]
com_dict = {}

def on_start():
   global running
   running = True

def on_stop():
   global running
   running = False

def all_camera():
    global index
    global arr
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.read()[0]:
            break
        else:
            arr.append(index)
        cap.release()
        index += 1
        print(arr)
    lenght_arr = len(arr)
    return arr,lenght_arr


def showSetup():
    global cam_id
    global Serial_port
    setup = Tk()
    setup.title("Setup")
    setup.geometry("400x600+100+100")
    Label(setup,text="Camera port",font=20).grid(row=0,column=0)
    choice=StringVar(setup,value='Select camera')
    camera_combo = ttk.Combobox(setup,textvariable=choice)
    camera_combo["values"] = camera_array
    camera_combo.grid(row=0,column=1)
    def apply_cam_setup():
        global cam_id
        cam_id = int(choice.get())
        print(f'current cam_id:{cam_id}  current_selected:{choice.get()}')
        cam1.change_cam(int(cam_id))
        show_frames()
    apply_cam_btn = Button(setup,text="Apply",command=apply_cam_setup)
    apply_cam_btn.grid(row=0,column=3)

    Label(setup,text="Serial port",font=20).grid(row=1,column=0)
    choice2=StringVar(setup,value='Select port')
    serial_combo = ttk.Combobox(setup,textvariable=choice2)
    serial_combo.bind('<<ComboboxSelected>>', serial_combo.current())
    serial_combo["values"] = com_portwithdesc
    serial_combo.grid(row=1,column=1)
    choice2.set("Select port")
    def apply_serial_setup():
        print(com_port[int(serial_combo.current())])
    apply_serial_btn = Button(setup,text="Apply",command=apply_serial_setup)
    apply_serial_btn.grid(row=1,column=3)

def show_frames():
    if(running):
        # Get the latest frame and convert into Image
        cv2image= cv2.cvtColor(cam1.getImage(),cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        # Convert image to PhotoImage
        imgtk = ImageTk.PhotoImage(image = img)
        label.imgtk = imgtk
        label.configure(image=imgtk)
        # Repeat after an interval to capture continiously
        label.after(20, show_frames)

def camera_stop():
    on_stop()
    cam1.stop_cam()

def camera_start():
    print(f'current cam_id:{cam_id}')
    on_start()
    cam1.change_cam(int(cam_id))
    show_frames()
    root.mainloop()

# setup camera
camera_array,camera_number= all_camera()
cam1 = camera.camera(cam_id,1280,720)

# list port
ports = serial.tools.list_ports.comports()
for x, y, z in sorted(ports):
    print("{}: {} [{}]".format(x,y,z))
    com_port.append(x)
    com_desc.append(y)
    com_portwithdesc.append(x +" "+ y)
com_dict = dict(zip(com_port,com_desc))
print(com_portwithdesc)


print(com_dict)

#main windoes setup
root = Tk()
root.title("Robot control center")
root.geometry("1280x720+100+100")
root.configure(bg='gray')

# menu bar
menubar= Menu(root)
root.config(menu=menubar)

setting_menu = Menu(menubar)

setting_menu.add_command(label='setup',command=showSetup)
menubar.add_cascade(label='setting',menu=setting_menu)

#camera
label =Label(root,bg='gray')
label.place(x=20, y=((1080/2)-((720/2)+100)))

# start stop Button
stop_btn = Button(text="Stop",command=camera_stop)
stop_btn.grid(row=0,column=1)

start_btn = Button(text="Start",command=camera_start)
start_btn.grid(row=0,column=0)


root.mainloop()