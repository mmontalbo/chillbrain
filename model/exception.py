
class PermissionException(Exception):
    _action = None
    
    def __init__(self, action):
        self._action = action
    
    def __str__(self):
        return "Permission Exception: User does not have permission for the action %s" % self._action
    
    def __unicode__(self):
        return self.__str__()