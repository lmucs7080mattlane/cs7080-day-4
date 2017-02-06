import os
from pyfirmata import Arduino, STRING_DATA
from pyfirmata.util import Iterator

class ArduinoInterface:
    def __init__(self, config):
        self.config = config
        self.button_status_handler = None
        
    @staticmethod
    def _autodiscover_device():
        device_list = ['/dev/ttyACM{}'.format(i) for i in range(10)]
        devices = [dev for dev in device_list if os.path.exists(dev)]
        return devices[0]
        
    def connect(self):
        device = None 
        try:
            device = self.config['device']
        except KeyError:
            device = self.__class__._autodiscover_device()
        self.board = Arduino(device, baudrate=57600,timeout=100)
        Iterator(self.board).start()
        self.board.add_cmd_handler(
            STRING_DATA,
            self._button_status_handler
        )

    def send_alert_update(self, alert=True):
        self.board.send_sysex(0x01, bytes([alert]))

    def request_button_status(self):
        self.board.send_sysex(0x02, bytes([]))

    def _button_status_handler(self, *string):
        status = None
        try:
            status = int(chr(string[0]))
        except ValueError:
            print('Empty button status received: {}'.format(string))
        else:
            self.button_status_handler(status)
        
    def attach_button_status_handler(self, func):
        self.button_status_handler = func

if __name__ == '__main__':
    import time
    arduino = ArduinoInterface({})
    arduino.connect()
    
    while True:
        arduino.send_alert_update(alert=True)
        time.sleep(5)
        arduino.send_alert_update(alert=False)
        time.sleep(5)
