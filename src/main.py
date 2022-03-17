from tkinter import *
from tkinter import ttk
import tkinter as tk
from PIL import Image, ImageTk
import camera
import cv2
import serial.tools.list_ports
import serial as serial
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pandas import DataFrame
import pandas as pd
import threading
import time

Serial_port = ''
cam_id = 0
index = 0
arr = []
com_port=[]
com_desc=[]
com_portwithdesc=[]
com_dict = {}

data3 = {'time': [], 'data': []}  
df3 = DataFrame(data3,columns=['time','data'])
continuePlotting = False 
 
def change_state(): 
    global continuePlotting 
    if continuePlotting == True: 
        continuePlotting = False 
    else: 
        continuePlotting = True 
     
def serial_read():
    global data3
    global df3
    start = time.time()
    x = []
    y = []
    ser = serial.Serial(port = Serial_port, baudrate=115200,bytesize=8, timeout=0.005, stopbits=serial.STOPBITS_ONE)
    while continuePlotting:
        if(ser.in_waiting > 0):
            # Read data out of the buffer until a carraige return / new line is found
            line = ser.readline()
            # Print the contents of the serial data
            string = line.decode('Ascii')
            print(f'print raw data{string}')
            #num = re.findall(r"[-+]?\d*\.\d+|\d+", string)
            num = float(string)
            end = time.time()
            y.append(num)
            time_elapsed= end - start
            x.append(time_elapsed)
            new_data=pd.DataFrame({'time':[time_elapsed],'data':[num]})
            df3 = pd.concat([df3,new_data])
            print(f'add data to pd')
    ser.close()


def all_camera():
    global index
    global arr
    global cam_id
    global Serial_port
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

def app():
    global cam_id
    global Serial_port
    def camera_stop():
        gui_handler()
        cam1.stop_cam()

    def camera_start():
        print(f'current cam_id:{cam_id}')
        cam1.change_cam(int(cam_id))
        show_frames()
        gui_handler()
        root.mainloop()

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
            global Serial_port
            print(com_port[int(serial_combo.current())])
            Serial_port = com_port[int(serial_combo.current())]
        apply_serial_btn = Button(setup,text="Apply",command=apply_serial_setup)
        apply_serial_btn.grid(row=1,column=3)

    def show_frames():
        while continuePlotting:
            # Get the latest frame and convert into Image
            cv2image= cv2.cvtColor(cam1.getImage(),cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            # Convert image to PhotoImage
            imgtk = ImageTk.PhotoImage(image = img)
            label.imgtk = imgtk
            label.configure(image=imgtk)
            # Repeat after an interval to capture continiously
            time.sleep(.01)

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
    label.place(x=10, y=60)

    # start stop Button
    stop_btn = Button(text="Stop",command=camera_stop)
    stop_btn.grid(row=0,column=1)

    start_btn = Button(text="Start",command=camera_start)
    start_btn.grid(row=0,column=0)

    #sensor
    figure1 = plt.Figure(figsize=(6,5), dpi=100)

    ax = figure1.add_subplot(111) 
    ax.set_xlabel("X axis") 
    ax.set_ylabel("Y axis") 
    ax.grid() 
 
    graph = FigureCanvasTkAgg(figure1, master=root) 
    graph.get_tk_widget().place(x=1300, y=60)
 
    def plotter(): 
        while continuePlotting: 
            print(df3)
            df_plot = df3[-20:]
            data_x = df_plot['time']
            data_y = df_plot['data']
            ax.cla() 
            ax.grid() 
            ax.plot(data_x,data_y, marker='o', color='orange') 
            graph.draw() 
            time.sleep(0.05) 
 
    def gui_handler(): 
        change_state() 
        threading.Thread(target=serial_read).start() 
        threading.Thread(target=plotter).start()
        threading.Thread(target=show_frames).start()

    root.mainloop()

if __name__ == '__main__': 
    app() 
    # test()