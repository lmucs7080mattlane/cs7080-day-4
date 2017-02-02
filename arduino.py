from pyfirmata import Arduino, STRING_DATA
from pyfirmata.util import Iterator

class ArduinoInterface:
    def __init__(self, config):
        self.config = config
        self.button_status_handler = None
        
    def connect(self):
        device = None 
        try:
            device = self.config['device']
        except:
            device = self._autodiscover_device()
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
        self.button_status_handler(int(chr(string[0])))
        
    def attach_button_status_handler(self, func):
        self.button_status_handler = func

if __name__ == '__main__':
    import time
    arduino = ArduinoInterface({'device':'/dev/ttyACM0'})
    arduino.connect()
    
    while True:
        arduino.send_alert_update(alert=True)
        time.sleep(5)
        arduino.send_alert_update(alert=False)
        time.sleep(5)
