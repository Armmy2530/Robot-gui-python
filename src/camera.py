import cv2
import numpy as np

class camera:
    def __init__(self, source, width, height):
        self.source = source
        self.width = width
        self.height = height
        camera.change_res(self)
    
    def getImage(self):
        _,self.imgae = self.input.read()
        return self.imgae

    def list_ports():
        is_working = True
        dev_port = 0
        working_ports = []
        available_ports = []
        while is_working:
            camera = cv2.VideoCapture(dev_port)
            if not camera.isOpened():
                is_working = False
                print("Port %s is not working." % dev_port)
            else:
                is_reading, img = camera.read()
                w = camera.get(3)
                h = camera.get(4)
                if is_reading:
                    print("Port %s is working and reads images (%s x %s)" % (dev_port, h, w))
                    working_ports.append(dev_port)
                else:
                    print("Port %s for camera ( %s x %s) is present but does not reads." % (dev_port, h, w))
                    available_ports.append(dev_port)
            dev_port += 1
        return available_ports, working_ports

    def change_res(self):
        self.input = cv2.VideoCapture(self.source, cv2.CAP_DSHOW)
        self.input.set(3, self.width)
        self.input.set(4, self.height)
    
    def change_cam(self,change_source):
        self.input.release()
        self.source = change_source
        print(f'source:{self.source}')
        camera.change_res(self)
    def stop_cam(self):
        self.input.release() 

if __name__ == "__main__":
    camera.list_ports()