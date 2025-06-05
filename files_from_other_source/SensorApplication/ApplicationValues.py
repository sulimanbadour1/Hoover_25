class AppValues:
    def __init__(self):
        self.port1 = "No port selected"
        self.port2 = "No port selected"
        self.baudrate_port1 = 115200
        self.baudrate_port2 = 115200
        self.device = "No device selected"
        self.device_list = ["RPLidarA2", "RadarTIAWR1642"] 

    def set_port(self, port_number: int, port: str):
        port_number = port_number
        if port_number == 1:
            self.port1 = port
            #print("Set port 1: "+self.port1)
        elif port_number ==2:
            self.port2 = port
            #print("Set port 2: "+self.port2)
        return 1


    def set_device(self, device: str):
        self.device = device
        return 1
    
    def set_baudrate(self, port_number: int, baudrate: int):
        """
        Assigns baudrate to the port defined by the number of port

        Input:
        port_numer: number of port which should have assigned baudrate
        baudrate: value of the baudrate
        """

        if port_number == 1:
            self.baudrate_port1 = baudrate
        elif port_number ==2:
            self.baudrate_port2 = baudrate
        return 1
        
    def give_ports(self, port_number = 1):
        """
        Returns the value of set ports. 
        Returned port is specified by the given number in the parameter (default is 1).
        """
        port = "No port selected"
        if self.device == "RPLidarA2":
            port = self.port1
        elif self.device == "RadarTIAWR1642" and port_number == 1:
            port =  self.port1
        elif self.device == "RadarTIAWR1642" and port_number == 2:
            port = self.port2
        return port

    def give_device(self):
        """
            Returns the value of set device. 
        """
        device = self.device
        return device

