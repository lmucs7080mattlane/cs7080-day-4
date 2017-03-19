import json
import requests

class CloudInterface:
    def __init__(self, config):
        self.config = config
     
    def connect(self):
        data = '{}'
        res = requests.post(
            self.config['address'] + '/login',
            data=data
        )
        if res.status_code != 200:
            raise Exception('Failed to login - {}'.format(res.status_code))

        self.session = res.json()
        print(self.session)
     
    def disconnect(self):
        requests.post(
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
        )
        if res.status_code != 200:
            raise Exception('Failed to check for alert, {}'.format(res.status_code))
        body = res.json()
        return body['response']['alerted']
        
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
