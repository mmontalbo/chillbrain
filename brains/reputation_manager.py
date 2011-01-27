from config.chill_constants import *

class RepManager():
    def __init__(self):
        RepManager.REP_REQ = { REQUEST_ACTION_SKIP: 0.0,
                               REQUEST_ACTION_VOTE:0.0,
                               REQUEST_ACTION_SHARE : 20.0,
                               REQUEST_ACTION_REPORT: 100.0,
                               REQUEST_ACTION_UPLOAD: 500.0}
        
        RepManager.ACHIEVMENT_MSGS = { REQUEST_ACTION_SHARE : "Sharing is now enabled.",
                                       REQUEST_ACTION_REPORT: "Reporting images is now enabled.",
                                       REQUEST_ACTION_UPLOAD: "Uploading images is now enabled."}
        
        RepManager.LINKBACK_FACTOR = 0.25

    def update_rep(self, action, reputation, linkbacks = 0):
        # get rep increase for linkbacks
        inc_rep = RepManager.LINKBACK_FACTOR * linkbacks
        
        # update reputation if voting
        if action == REQUEST_ACTION_VOTE:
            inc_rep += 1.0
            
        # message if new achievment is unlocked
        msg = self.get_achievment_msg(reputation, inc_rep)
        reputation += inc_rep
        return (reputation, msg)

    # Check if the given action can be performed based on the given reputation
    def check_permission(self, action, reputation):
        if action in RepManager.REP_REQ:
            hasPermission = reputation >= RepManager.REP_REQ[action]
            if not hasPermission:
                return (hasPermission,self.get_permission_denied_msg(action))
            else:
                return(hasPermission,None)
        else:
            logging.error("No reputation requirement defined for: "+action)
            return (False,None)

    # Get any new achievment messages
    def get_achievment_msg(self,reputation,inc_rep):
        msg = None
        for action,req in RepManager.REP_REQ.iteritems():
            if reputation < req and (reputation + inc_rep) >= req:
                return RepManager.ACHIEVMENT_MSGS[action]
        return msg

    # Construct an appropriate permission denied error message
    def get_permission_denied_msg(self, action):
        return "Need "+str(RepManager.REP_REQ[action])+" rep to "+action+"."