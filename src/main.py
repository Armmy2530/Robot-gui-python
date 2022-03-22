from logging import warning
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

bg_color = "#3b3838"
Text_color = "#ffffff"
bg2_color = "#525252"
bg3_color = "#9e9e9e"
line_color = "#4570be"

plt.rcParams.update({'text.color': Text_color,
                     'axes.labelcolor': Text_color,
                     'axes.titlecolor': Text_color,
                     'grid.color' : bg2_color,
                     'xtick.color': bg3_color,
                     'xtick.labelcolor':Text_color,
                     'ytick.color': bg3_color,
                     'ytick.labelcolor':Text_color,
                     'hatch.color': bg2_color,
                     'legend.edgecolor': bg2_color,
                     'scatter.edgecolors':bg2_color})

df = DataFrame()
df_last= DataFrame()
continuePlotting = False 
 
def change_state(): 
    global continuePlotting 
    if continuePlotting == True: 
        continuePlotting = False 
    else: 
        continuePlotting = True 

def serial_list():
    global com_dict
    global com_desc
    global com_portwithdesc
    com_dict = []
    com_desc = []
    com_portwithdesc = []
    ports = serial.tools.list_ports.comports()
    for x, y, z in sorted(ports):
        print("{}: {} [{}]".format(x,y,z))
        com_port.append(x)
        com_desc.append(y)
        com_portwithdesc.append(x +" "+ y)
    com_dict = dict(zip(com_port,com_desc))
    print(com_portwithdesc)

def serial_read():
    global df
    global df_last
    warning = False
    start = time.time()
    ser = serial.Serial(port = Serial_port, baudrate=115200,bytesize=8, timeout=0.01, stopbits=serial.STOPBITS_ONE)
    while continuePlotting:
        if(ser.in_waiting > 0):
            # Read data out of the buffer until a carraige return / new line is found
            line = ser.readline()
            # Print the contents of the serial data
            string = line.decode('utf-8').rstrip()
            end = time.time()
            time_elapsed= end - start
            string = (f'time:{time_elapsed},') +string
            n_dict , d_dict =sort_name_and_data(string,",",":")
            df = pd.concat([df,dict_data(n_dict,d_dict)])
            if(not(df.empty)):
                df_last=df.tail(1)
            if(df_last.iloc[0]['radioactive'] == -1 and df_last.iloc[0]['voltage'] == -1 and df_last.iloc[0]['connection'] == -1):
                if(not(warning)):
                    tk.messagebox.showwarning(title="Disconnected", message="Don't get any data from robot")
                    warning = True
            else:
                warning = False
    ser.close()

def split_data(data,index):
    x=[] 
    x = data.split(index)
    return x

def sort_name_and_data(data,index_name,index_data):
    name  = []
    value = []
    x=split_data(data,index_name)
    for i in x:
        y=split_data(i,index_data)
        name.append(y[0])
        try:
            value.append(float(y[1]))
        except:
            value.append(y[1])
    # for n in range(0,len(name)):
    #     print(f'{name[n]} : {value[n]}')
    return name,value

def dict_data(dict_name,dict_data):
    res = {dict_name[i]: [dict_data[i]] for i in range(len(dict_name))}
    # print(res)
    new_data=pd.DataFrame(res)
    # print(new_data)
    return new_data

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
        if(not(continuePlotting)):
            pass
        gui_handler()
        cam1.stop_cam()

    def camera_start():
        if(continuePlotting):
            camera_stop()
        print(f'current cam_id:{cam_id}')
        cam1.change_cam(int(cam_id))
        gui_handler()

    def showSetup():
        global cam_id
        global Serial_port
        serial_list()
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
            cam1.stop_cam()
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
        if(continuePlotting):
            # Get the latest frame and convert into Image
            cv2image= cv2.cvtColor(cam1.getImage(),cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            # Convert image to PhotoImage
            imgtk = ImageTk.PhotoImage(image = img)
            label.imgtk = imgtk
            label.configure(image=imgtk)
            # Repeat after an interval to capture continiously
            label.after(20, show_frames)

    # setup camera
    camera_array,camera_number= all_camera()
    cam1 = camera.camera(cam_id,1280,720)

    #Serial list
    serial_list()
    print(com_dict)

    #main windoes setup
    root = Tk()
    root.title("Robot control center")
    root.geometry("1280x720+100+100")
    root.configure(bg=bg_color)

    # menu bar
    menubar= Menu(root)
    root.config(menu=menubar)

    setting_menu = Menu(menubar)

    setting_menu.add_command(label='setup',command=showSetup)
    menubar.add_cascade(label='setting',menu=setting_menu)

    #camera
    radio_n = Label(root, text = "Camera")
    radio_n.config(font =("circular", 32),bg=bg_color,fg=Text_color)
    radio_n.place(x=30, y=40)
    label =Label(root,bg=bg_color)
    label.place(x=10, y=100)

    # start stop Button
    stop_btn = Button(text="Stop",command=camera_stop)
    stop_btn.grid(row=0,column=1)

    start_btn = Button(text="Start",command=camera_start)
    start_btn.grid(row=0,column=0)

    #sensor plotter
    radio_n = Label(root, text = "Radioactive sensor")
    radio_n.config(font =("circular", 30),bg=bg_color,fg=Text_color)
    radio_n.place(x=1350, y=60)
    figure1 = plt.Figure(figsize=(6,5), dpi=100,facecolor = bg_color)
    ax = figure1.add_subplot(111) 
    # ax.title('Radioactive sensor')
    ax.set_xlabel("Sensor value") 
    ax.set_ylabel("Time(s)") 
    ax.margins(x=0, y=-0.25)
    ax.set_facecolor(bg2_color)
    graph = FigureCanvasTkAgg(figure1, master=root) 
    graph.get_tk_widget().place(x=1300, y=100)

    #sensor text
    voltage = "STOP"
    connection = "Disconnected"
    voltage_n = Label(root, text = "Voltage sensor")
    voltage_n.config(font =("circular", 28),bg=bg_color,fg=Text_color)
    voltage_n.place(x=1350, y=615)
    voltage_v = Label(root, text=voltage,anchor='e')
    voltage_v.config(font =("circular", 28),bg=bg_color,fg=Text_color)
    voltage_v.place(x=1350, y=665)

    Connection_n = Label(root, text = "Connection status")
    Connection_n.config(font =("circular", 28),bg=bg_color,fg=Text_color)
    Connection_n.place(x=1350, y=765)
    Connection_v = Label(root, text=connection,anchor='e')
    Connection_v.config(font =("circular", 28),bg=bg_color,fg=Text_color)
    Connection_v.place(x=1350, y=815)

    def plotter(): 
        global df_last 
        while (continuePlotting): 
            df_plot = df[-20:]
            data_x = df_plot['time']
            data_y = df_plot['radioactive']
            if(df_last.iloc[0]['connection'] == -1):
                continue
            else:
                ax.cla() 
                ax.grid() 
                ax.plot(data_x,data_y, marker='o', color='orange') 
                graph.draw() 
                time.sleep(0.05) 
    def sensor_update():
        global voltage
        global connection
        while (continuePlotting): 
            if(df_last.empty or df_last.iloc[0]['voltage'] == -1 or df_last.iloc[0]['connection'] == -1):
                voltage_v.config(text = "Disconnected")
                Connection_v.config(text = "Disconnected")
            else:
                voltage = str(df_last.iloc[0]['voltage'])
                voltage_v.config(text = voltage)
                Connection_v.config(text = "Connected")
                
    def gui_handler(): 
        change_state() 
        threading.Thread(target=show_frames).start()
        threading.Thread(target=serial_read).start() 
        time.sleep(5)
        threading.Thread(target=plotter).start()
        threading.Thread(target=sensor_update).start()


    root.mainloop()

if __name__ == '__main__': 
    app() 
    # test()