from ApplicationValues import AppValues 
from ApplicationInterface import MainWindow


application_values = AppValues()
#print(application_values.port1)
#print(application_values.give_ports(1))
print(application_values.give_device())
#application_values.port = 'COM_X'
#application_values.device = 'Device_X'
main_window = MainWindow()


main_window.run_window(application_values)




