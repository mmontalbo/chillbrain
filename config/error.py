from django.utils import simplejson as json

class BaseError(Exception):
    errorMessage = ""
    errorCode = -1
    def __init__(self, message, code):
        self.errorMessage = message
        self.errorCode = code
        
    def asJSON(self):
        return json.dumps({ 'error' : { 'msg' : self.errorMessage, 'code' : self.errorCode } })
        
class PermissionError(BaseError):
    def __init__(self):
        self.errorMessage = "Login to share."
        self.errorCode = 100     
