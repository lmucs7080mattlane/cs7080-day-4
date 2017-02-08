import time
import traceback

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
            print(traceback.format_exc())
            self.cloud.disconnect()
            raise

if __name__ == '__main__':
    from arduino import ArduinoInterface
    from cloud import CloudInterface
    import sys

    device = sys.argv[1]
    url = sys.argv[2]

    print('Configured to use device {}'.format(device))
    arduino = ArduinoInterface({'device': device})

    print('Configured to use server {}'.format(url))
    cloud = CloudInterface({'address': url})

    UselessMachine({'loop_delay_s':1}, arduino, cloud).start()
    
