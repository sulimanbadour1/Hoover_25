from tiradar import TI_AWR1642BOOST, TIRadarVisualisation
import time

class TIRadarWindow():
     def __init__(self, port):
        self.layout = [[sg.Text("Control Device: "),sg.Button("Start device", key = '-START_DEV-'), sg.Button("Stop ", key = '-STOP_DEV-')],
                       [sg.Button ("Stop device", key = '-STOP_DEV-')],
                       [sg.Button("Reset device", key = '-RESET_DEV-', disabled= True)],
                       [sg.Text("Measured data", key = '-MEASUREMENTS-'), sg.Text(" 0 ", key = '-DATA-')],
                       [sg.Output(size = (80,80), key = '-OUTPUT-'), sg.Button("Send",key = '-BUTTON-')]
                       ]
        self.window = sg. Window("TIRadarWindow", self.layout, size=[600,500], finalize=True)

        #creting device object
        self.device = TI_AWR1642BOOST(None, port, timeout=3)
        self.plot = TIRadarVisualisation
        self.device_started = False
        self.device_running = False
        #other attributes used in window
    
     def receive_data(self):
        measure = self.device.read_parse_data()
        self.plot.plot_data(measure)
        self.window.write_event_value('-UPDATE-', measure) #creating new event which generates 'measure data'
        time.sleep(0.01)
    
     def start_device(self):

        self.device.startSensor()
        self.plot.init_plot()
        self.device_started = True
        #measure_thread = threading.Thread(target = self.receive_data)
        #measure_thread.start()

        


     def run_window(self):
        while True:
            event, values = self.window.read(timeout = 10)
            self.window.Refresh()

            if self.device_started == True:
                self.receive_data()

            if event == '-UPDATE-':
                measured_data = values[event]
                self.window['-DATA-'].update(measured_data)
            if event == '-START_DEV-':
                self.start_device()
                #self.run_window()
            
            if event == '-STOP_DEV-':
                self.device.stopSensor()
                self.device_started = False
                self.window['-RESET_DEV-'].update(disabled = False)
                #self.run_window()

            
            if event == '-RESET_DEV-':
                self.device.reset()

            if event == '-BUTTON-':
                print("Button was pressed")

            
            if event == sg.WIN_CLOSED:
                self.device.disconnect()
                break


        self.window.close()