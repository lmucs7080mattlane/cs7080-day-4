import json
import requests

class CloudInterface:
    def __init__(self, config):
        self.config = config
     
    def connect(self):
        data = '{}'
        self.session = requests.post(
            self.config['address'] + '/login',
            data=data
        ).json()
        print(self.session)
        # TODO check status code?
     
    def disconnect(self):
        self.session = requests.post(
            self.config['address'] + '/signout',
            data=json.dumps(self.session)
        )
        # TODO check status code?
        
    def extend_session(self):
        requests.post(
            self.config['address'] + '/session',
            data=json.dumps(self.session)
        )
        # TODO check status code?
    
    @staticmethod
    def _construct_user_action(session, action):
        return {
            'session': session,
            'user_action': {
                'api': {
                    'name': 'stateful',
                    'version': 1
                },
                'action': action
            }
        }
    
    def check_for_alert(self):
        action = {
            'code': 'CHECK_IF_ALERTED'
        }
        data = self.__class__._construct_user_action(
            self.session,
            action
        )
        res = requests.post(
            self.config['address'] + '/action',
            data=json.dumps(data)
        ).json()
        return res['response']['alerted']
        
    def send_button_pressed(self):
        action = {
            'code': 'BUTTON_PRESS'
        }
        data = self.__class__._construct_user_action(
            self.session,
            action
        )
        requests.post(
            self.config['address'] + '/action',
            data=json.dumps(data)
        )
