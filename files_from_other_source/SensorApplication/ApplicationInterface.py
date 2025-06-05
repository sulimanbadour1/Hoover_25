import PySimpleGUI as sg
from serial.tools.list_ports import comports
import os
from adafruit_rplidar import RPLidarException
import threading
import time

class AppWindow:
    def __init__(self):

        self.layout = []
        self.window = sg. Window("AppWindow", self.layout, size=[600,200], background_color= self.color)

    def run_window(self):
        while True:
            event, values = self.window.read()

            if event == sg.WIN_CLOSED:
                break

class MainWindow(AppWindow):
    def __init__(self):
        self.enable_TryButton = True 
        self.layout_column = [
            [sg.Button("Settings", key = '-SETTINGS-',size = (16,1))],
            [sg.Button("Start", key = '-START-', size = (16,1))]
            ]
        self.layout = [
            [sg.Column(self.layout_column, element_justification= 'center', expand_x=True)],
            [sg.Output(size = (80,20), key = '-OUTPUT-')],
            [sg.Button("Send",key = '-BUTTON-')],
            [sg.Column([[sg.Button("Exit", key = '-EXIT-',)]], element_justification='right',expand_x = True)]
        ]

        self.settings_window = None
        self.device_window = None
        self.values = None

        self.window = sg. Window("Sensor Apllication", self.layout, size=[600,600], enable_close_attempted_event= True,
                               button_color = '#424242', titlebar_text_color='black', default_button_element_size=(10,1))

   
    def run_window(self,other):
        while True:
            event, values = self.window.read()
                
            if event == '-SETTINGS-':
                self.settings_window = SettingWindow()
                self.settings_window.settings_set_values(other)
                print("Settings finished")
                #print ("Set device: " + other.give_device())
                #print ("Set port 1: " + other.give_ports())
                #print ("Set port 2: " + other.give_ports(2))
                self.run_window(other)


            if event == '-START-':
                """if other.give_device() == "No device selected":
                    print ("Select device")
                elif other.give_device () == "RPLidarA2":
                    if other.give_ports() == "No port selected":
                        print ("Select port")
                elif other.give_device () == "RadarTIAWR1642":
                    if other.give_ports() == "No port selected" or other.give_ports(2) == "No port selected":
                        print ("Select both ports")
                else:"""
                self.evaluate_device(other)
                try:
                    self.device_window.run_window()
                except AttributeError:
                    print("AttributeError: Select device.")
                self.run_window(other)
            
            if event == '-BUTTON-':
                print("Button was pressed")
                execfile('PY_Stopwatch.py')
                """self.info(other)
                self.run_window(other)"""
                
        
            
            if event == '-EXIT-' or event == sg.WIN_CLOSED:
                break

            return 1

        # self.window.close()
        return 1
    
    def evaluate_device(self, other):
        device_name = other.give_device()
        port1 = other.give_ports()
        port2 = other.give_ports(2)

        if device_name == "No device selected":
            print ("Select device")
        elif device_name == "RPLidarA2":
            if port1 == "No port selected":
                print ("Select port")
        elif device_name == "RadarTIAWR1642":
            if port1 == "No port selected" or port2 == "No port selected":
                print ("Select both ports")

        if device_name == "RPLidarA2":
            port1 = other.give_ports(1)
            try:
                self.device_window = RPLidarWindow(port1)
            except RPLidarException:
                print("RPLidar Exception: Unable to connect to the port. Check port settings.")
        elif device_name == "RadarTIAWR1642":
            port1 = other.give_ports()
            port2 = other.give_ports(2)
            self.device_window = TIRadarWindow(port1, port2)
            #call window for RPLidar
    
    def info(self, other):
        print ("Set device: " + other.give_device())
        print ("Set port 1: " + other.give_ports())
        print ("Set port 2: " + other.give_ports(2))

                
    

class SettingWindow(AppWindow):

    def __init__(self):
        self.port_list = [["Select_port...", ""]] #List of available ports
        self.port_table_title=["Port specification", "Port Name"]
        self.device_list = ["RPLidarA2", "RadarTIAWR1642"] #List of available ports
        self.device_table_title=["Port specification", "Port Name"]
        
        self.port1_chosen = "No port chosen" #chosen port but not confirmed
        self.port2_chosen = "No port chosen" #chosen port but not confirmed
        self.device_chosen = "No device chosen"
        self.port1_set  = "No port set"
        self.port2_set  = "No port set"
        self.device_set = "No device set"
        self.combo_value = "No device chosen"
        self.selected_row_number = "x"
        

        self.layout = [
        [sg.Combo(self.device_list, size = (30,4), default_value = "Select device",key = '-COMBO-'), sg.Button("Confirm device", key = '-CONFIRM_DEV-')],
        [sg.Button("Choose port", key = '-SELECT_PORT-', disabled= True),sg.Button("Confirm port1", key = '-CONFIRM_PORT_1-', disabled=True),sg.Button("Confirm port2", key = '-CONFIRM_PORT_2-', disabled=True)],
        [sg.Table(self.port_list, key='-PORT_TABLE-', expand_x=True,headings = self.port_table_title, enable_click_events=True,  background_color= 'white', text_color='black')],
        [sg.Output(size = (80,5), key = '-OUTPUT-')],
        [sg.Button("OK", key = "-OK1-"), sg.Button("CANCEL")]
        ]

        self.window = sg. Window("Settings", self.layout, size=[600,600], enable_close_attempted_event= False)
        
    def find_ports(self):
        """Clears all ports saved in setiings window configuration and finds available ports.
        
        Returns:
        List: list of available ports"""

        #Clearing previous ports from the tribute 'port_list' of the settings window
        self.port_list.clear()

        #Finding available ports with help of pyserial comport function and appending them to the list
        for port in comports():
            self.port_list.append([port, port.name])

        #Condition when no port was found
        if len(self.port_list) == 0:
            self.port_list.append(["No port available.", "No port"]) #default values if no port is found
            self.port_list_empty = True
        else:
            self.port_list_empty = False

        #return self.port_list
    
    def set_device(self, device_set):
        self.device_set = device_set
    
    def set_port(self, port_number, port_name: str):
        if port_number == 1:
            self.port1_set = port_name
        elif port_number == 2:
            self.port2_set = port_name


    def settings_set_values(self, other):
        self.run_window()
        other.set_device(self.device_set)
        other.set_port(1,self.port1_set)
        if self.device_set == "RadarTIAWR1642":
            other.set_port(2,self.port2_set)
        #self.window.close()
        return 1

    def reset_chosen_ports(self):
        self.port1_chosen = "No port chosen" 
        self.port2_chosen = "No port chosen"


    def run_window(self):

        while True:
            event, values = self.window.read()

            if event == '-CONFIRM_DEV-':
                combo_value = self.window['-COMBO-'].get()
                self.window['-SELECT_PORT-'].update(disabled = False)
                self.device_chosen = combo_value
                print("Chosen device" + self.device_chosen)
                self.run_window()

            if event == "-SELECT_PORT-":
                self.find_ports()
                print(self.port_list)
                #self.window['-PORT_TABLE-'].Update(enable_click_events = True)
                self.window['-PORT_TABLE-'].update(self.port_list)
                self.window['-CONFIRM_PORT_1-'].update(disabled = False)
                if self.device_chosen == "RadarTIAWR1642":
                    self.window['-CONFIRM_PORT_2-'].update(disabled = False)
                self.run_window()             

            
            if '+CLICKED+' in event:
                self.selected_row_number = event[2][0]
                print("Selected port: "+ str(self.selected_row_number))
                self.run_window()
            

            if event == '-CONFIRM_PORT_1-':
                try:
                    self.port1_chosen= self.port_list[self.selected_row_number][1]
                except TypeError:
                    print("TypeError: Select port in the table and than click on button 'Confirm port 1'.")
                print("Chosen port 1:   " + self.port1_chosen)
                self.run_window()


            if event == '-CONFIRM_PORT_2-':
                try:
                    self.port2_chosen= self.port_list[self.selected_row_number][1]
                except TypeError:
                    print("TypeError: Select port in the table and than click on button 'Confirm port 2'.")
                print("Chosen port 2:   " + self.port2_chosen)   
                self.run_window()

            if event == "-OK1-":
                if self.port1_chosen != "No port chosen" and  self.port1_chosen != "No port" and self.port1_chosen != "":
                    #self.set_port(1,self.port1_chosen)
                     self.port1_set  = self.port1_chosen
                
                if self.port2_chosen != "No port chosen" and  self.port2_chosen != "No port" and self.port2_chosen != "":
                    #self.set_port(2,self.port2_chosen)
                    self.port2_set  = self.port2_chosen
                    
                if self.device_chosen != "No device chosen" and self.device_chosen != "Select device" :
                    self.device_set = self.device_chosen
                #print(self.device_set + self.port1_set + self.port2_set)
                #event = sg.WIN_CLOSED
                #self.reset_chosen_ports()
            
            if event == sg.WIN_CLOSED:
                break
            if event == "-CANCEL-":
                self.window.close()

            return 1 #necessary otherwise error NoneType is not iterable occurs
        
        #self.window.close()
        print("Closing settings finished")
        return 1
        
    def settings_info(self):
        info_settings = """
        Please select device in combo box. Then click on 'Confirm device'. Click on 'Choose port'.
        The available ports will be shown in the table. 

        RP Lidar uses just one port. Please click on port in the table. Order of selecting device and 
        TI Radar uses two ports. Please
        """
        return info_settings


class SensorWindow(AppWindow):
     def __init__(self):
        #import library for device 
        self.layout = [sg.Button("Start device")]
        self.window = sg. Window("AppWindow", self.layout, size=[600,200])
        #create device

     def run_window(self,other):
        while True:
            event, values = self.window.read()

            if event == sg.WIN_CLOSED:
                break

        self.window.close()

class RPLidarWindow(SensorWindow):
     def __init__(self, port):
        from adafruit_rplidar_AK  import RPLidar 
        self.layout = [[sg.Text("Control Device: "),sg.Button("Start device", key = '-START_DEV-'), sg.Button("Stop ", key = '-STOP_DEV-')],
                       [sg.Button ("Stop device", key = '-STOP_DEV-')],
                       [sg.Text("MOTOR CONTROL:"),sg.Button("Start motor", key =  '-START_MOTOR-'), sg.Button("Stop motor", key =  '-STOP_MOTOR-')],
                       [sg.Button("Reset device", key = '-RESET_DEV-', disabled= True)],
                       [sg.Text("Measured data", key = '-MEASUREMENTS-'), sg.Text(" 0 ", key = '-DATA-')],
                       [sg.Output(size = (80,80), key = '-OUTPUT-'), sg.Button("Send",key = '-BUTTON-')]
                       ]
        self.window = sg. Window("RPLidarWindow", self.layout, size=[600,600], finalize=True)

        #creting device object
        self.device = RPLidar(None, port, timeout=3)
        self.device_started = False
        self.device_running = False
        #other attributes used in window
        self.angle_storage = []
        self.distance_storage = []
    
     def receive_data(self):
        measure = self.device.once_measurements(max_buf_meas = 500)
        self.window.write_event_value('-UPDATE-',measure)
        time.sleep(0.01)
    
     def start_device(self):
        try:
            self.device.start()
            self.device_started = True
            #measure_thread = threading.Thread(target = self.receive_data)
            #measure_thread.start()
        except RPLidarException:
            print("RPLidarException: Device already started.")
        


     def run_window(self):
        while True:
            event, values = self.window.read(timeout = 10)
            self.window.Refresh()

            if self.device_started == True:
                self.receive_data()

            if event == '-UPDATE-':
                measured_data = values[event]
                self.window['-DATA-'].update(measured_data)
                print(f"Angle: {measured_data[2]}, distance: {measured_data[3]}, quality:  {measured_data[1]}")
            if event == '-START_DEV-':
                self.start_device()
                #self.run_window()
            
            if event == '-STOP_DEV-':
                self.device.stop()
                self.device_started = False
                self.window['-RESET_DEV-'].update(disabled = False)
                #self.run_window()

            if event == '-START_MOTOR-':
                self.device.start_motor()
            
            if event == '-STOP_MOTOR-':
                self.device.stop_motor()
            
            if event == '-RESET_DEV-':
                self.device.reset()

            if event == '-BUTTON-':
                print("Button was pressed")

            
            if event == sg.WIN_CLOSED:
                self.device.disconnect()
                break


        self.window.close()

class TIRadarWindow(SensorWindow):
     def __init__(self, port1):
        from adafruit_rplidar import RPLidar 
        self.layout = [[sg.Text("Control Device: "),sg.Button("Start device", key = '-START_DEV-'), sg.Button("Stop ", key = '-STOP_DEV-')],
                       [sg.Button ("Stop device", key = '-STOP_DEV-')],
                       [sg.Text("MOTOR CONTROL:"),sg.Button("Start motor", key =  '-START_MOTOR-'), sg.Button("Stop motor", key =  '-STOP_MOTOR-')],
                       [sg.Button("Reset device", key = '-RESET_DEV-')]
                       ]
        self.window = sg. Window("AppWindow", self.layout, size=[600,200])
        self.device = RPLidar(None, port1, timeout=3)
        #create device

     def run_window(self):
        while True:
            event, values = self.window.read()

            if event == '-START_DEV-':
                self.device.start()
            
            if event == '-STOP_DEV-':
                self.device.stop()

            if event == '-START_MOTOR-':
                self.device.start_motor()
            
            if event == '-STOP_MOTOR-':
                self.device.stop_motor()
            
            if event == '-RESET_DEV-':
                self.device.reset()
            
            if event == sg.WIN_CLOSED:
                break

            self.window.refresh()

        self.window.close()
    