import serial

class series:
    serialString = ""    
    def __init__(self, source, baudrate, timeout):
        self.source = source
        self.baudrate = baudrate
        self.timeout = timeout
    def connect(self):
        self.port = serial.Serial(port = self.source, baudrate=self.baudrate,bytesize=8, timeout= self.timeout, stopbits=serial.STOPBITS_ONE)
                # The b at the beginning is used to indicate bytes!

