import time

class UselessMachine:
    def __init__(self, config, arduino, cloud):
        self.config = config
        self.arduino = arduino
        self.cloud = cloud
     
    def _handle_button(self, button_pressed):
        if button_pressed:
            print('button_pressed')
            self.cloud.send_button_pressed()
     
    def start(self):
        self.arduino.attach_button_status_handler(self._handle_button)
        self.arduino.connect()
        self.cloud.connect()
        try:
            while True:
                self.cloud.extend_session()
                time.sleep(self.config['loop_delay_s'])
                alert = self.cloud.check_for_alert()
                self.arduino.send_alert_update(alert=alert)
                if alert:
                    print(alert)
                self.arduino.request_button_status()
        except:
            self.cloud.disconnect()
            raise

if __name__ == '__main__':
    from arduino import ArduinoInterface
    from cloud import CloudInterface
    arduino = ArduinoInterface({'device':'/dev/ttyACM2'})
    cloud = CloudInterface({'address':'http://192.168.0.25:8080'})
    UselessMachine({'loop_delay_s':1}, arduino, cloud).start()
    
