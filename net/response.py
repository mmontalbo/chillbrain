from django.utils import simplejson as json

class ChillResponse:
    responseObject = {}
    def __init__(self, id, img):
        self.responseObject = {}
        self.responseObject['id'] = id
        self.responseObject['img'] = img
        
    def toJSON(self):
        return json.dumps(self.responseObject)
    
class ShareResponse(ChillResponse):
    def __init__(self, id, img):
        ChillResponse.__init__(self, id, img)
        self.responseObject['process_response'] = True