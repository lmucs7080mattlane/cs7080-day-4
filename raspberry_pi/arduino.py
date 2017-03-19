import os

# For documentation on pyfirmata and the firmata protocol, go to 
# https://media.readthedocs.org/pdf/pyfirmata/latest/pyfirmata.pdf
# https://github.com/firmata/protocol
# (and google)
from pyfirmata import Arduino, STRING_DATA
from pyfirmata.util import Iterator

class ArduinoInterface:
    def __init__(self, config):
        self.config = config
        self.button_status_handler = None
        
    @staticmethod
    def _autodiscover_device():
        # This code looks for an Arduino device called '/dev/ttyACM0', failing
        # this it looks for a device called '/dev/ttyACM1', and then 
        # '/dev/ttyACM2' and so on...
        # If you want to run multiple Arduinos from one Raspberry Pi, you will
        # need to identify them manually as is done with the 
        # self.config['device'] config item. You can find all connected devices
        # in the terminal by typing 'ls /dev/ttyACM*'
        device_list = ['/dev/ttyACM{}'.format(i) for i in range(10)]
        devices = [dev for dev in device_list if os.path.exists(dev)]
        return devices[0]
        
    def connect(self):
        # Connect to Arduino
        device = None 
        try:
            # If self.config['device'] is set, we'll use this as the address
            # of the device
            device = self.config['device']
        except KeyError:
            # If this config item is not set, try to 'autodiscover' the device
            device = self.__class__._autodiscover_device()

        # Connect to the Arduino
        self.board = Arduino(device, baudrate=57600,timeout=100)
        Iterator(self.board).start()

        # Set this classes '_handle_string_data' method
        # as the function that handles STRING_DATA messages
        # from the raspberry pi
        self.board.add_cmd_handler(
            STRING_DATA,
            self._handle_string_data
        )

    def send_alert_update(self, alert=True):
        # Send the ALERT command (0x01) with a single byte 'alert' as a
        # parameter
        self.board.send_sysex(0x01, bytes([alert]))

    def request_button_string_status(self):
        # Send the REQUEST_BUTTON_STRING command (0x02) to ask the Raspberry Pi
        # to send its current sensor data.
        self.board.send_sysex(0x02, bytes([]))

    def request_button_integer_status(self):
        # Send the REQUEST_BUTTON_INTEGER command (0x03) to ask the Raspberry Pi
        # to send its current sensor data.
        self.board.send_sysex(0x03, bytes([]))

    def _handle_string_data(self, *string):
        command = None
        try:
            command = string[0]
        except ValueError:
            print('Empty command received: {}'.format(string))
        else:
            if command == 1:
                # Command code is BUTTON_STRING (0x01).
                # Call the attached sensor data handler method
                # with the sensor data (all data after the command code).
                self.button_string_handler(bytes(string[2::2]).decode('ascii'))
            if command == 2:
                # Command code is BUTTON_INTEGER (0x02).
                # Call the attached sensor data handler method
                # with the sensor data (all data after the command code).
                self.button_integer_handler(int(bytes(string[2::2]).decode('ascii')))
        
    def attach_button_string_handler(self, func):
        # Take the parameter function and call it whenever we receive button
        # string data.
        self.button_string_handler = func
        
    def attach_button_integer_handler(self, func):
        # Take the parameter function and call it whenever we receive button
        # integer data.
        self.button_integer_handler = func

if __name__ == '__main__':
    import time
    arduino = ArduinoInterface({})
    arduino.connect()

    def handle_button_string_data(data):
        print("Button String Data: '{}'".format(data))
    def handle_button_integer_data(data):
        print("Button Integer Data: {}".format(data))
    arduino.attach_button_string_handler(handle_button_string_data)
    arduino.attach_button_integer_handler(handle_button_integer_data)
    
    while True:
        arduino.send_alert_update(alert=True)
        time.sleep(2)
        arduino.send_alert_update(alert=False)
        time.sleep(2)
        arduino.request_button_string_status()
        arduino.request_button_integer_status()
        time.sleep(2)
