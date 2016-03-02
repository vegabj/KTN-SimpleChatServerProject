import json

class MessageParser():
    def __init__(self):

        self.possible_responses = {
            'error': self.parse_error,
            'info': self.parse_info,
            'message' : self.parse_message,
            'history' : self.parse_history	
        }

    def parse(self, payload):
        payload = json.loads(payload) # decode the JSON object

        if payload['response'] in self.possible_responses:
            return self.possible_responses[payload['response']](payload)
        else:
            print "Error: Client got an illegal response"
            # Response not valid

    def parse_error(self, payload):
        return payload['timestamp']+'\t'+'Error: '+payload['content']
    
    def parse_info(self, payload):
        return payload['timestamp']+'\t'+"Server: "+payload['content']

    def parse_message(self, payload):
        return payload['timestamp']+'\t'+payload['sender']+':\t'+payload['content']

    def parse_history(self, payload):
        print "Fetching history:"
        for message in payload['content']:
            msg = json.loads(message)
            print msg['timestamp']+'\t'+msg['sender']+':\t'+msg['content']
        return ''
    
    # Include more methods for handling the different responses... 
