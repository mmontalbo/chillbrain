from config.chill_constants import *

class RepManager():
    def __init__(self):
        RepManager.REP_REQ = { REQUEST_ACTION_SKIP: 0.0,
                               REQUEST_ACTION_VOTE:0.0,
                               REQUEST_ACTION_SHARE : 30.0,
                               REQUEST_ACTION_REPORT: 300.0,
                               REQUEST_ACTION_UPLOAD: 3000.0}
        
        RepManager.ACHIEVMENT_MSGS = { REQUEST_ACTION_SHARE : "Sharing is now enabled.",
                                       REQUEST_ACTION_REPORT: "Reporting images is now enabled.",
                                       REQUEST_ACTION_UPLOAD: "Uploading images is now enabled."}

        RepManager.DENIED_MSGS = { REQUEST_ACTION_SHARE : "Sharing requires "+RepManager.REP_REQ.REQUEST_ACTION_SHARE+" rep.",
                                   REQUEST_ACTION_REPORT: "Reporting images requires "+RepManager.REP_REQ.REQUEST_ACTION_REPORT+" rep.",
                                   REQUEST_ACTION_UPLOAD: "Uploading images requires "+RepManager.REP_REQ.REQUEST_ACTION_UPLOAD+" rep."}
        
        RepManager.LINKBACK_FACTOR = 0.25

    def update_rep(self, action, reputation, linkbacks = 0):
        # get rep increase for linkbacks
        inc_rep = RepManager.LINKBACK_FACTOR * linkbacks
        
        # update reputation if voting
        if action == REQUEST_ACTION_VOTE:
            inc_rep += 1.0
            
        # message if new achievment is unlocked
        msgs = self.get_achievment_msg(reputation, inc_rep)
        reputation += inc_rep
        return (reputation, msgs)

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
        msgs = []
        for action,req in RepManager.REP_REQ.iteritems():
            if reputation < req and (reputation + inc_rep) >= req:
                msgs.append(RepManager.ACHIEVMENT_MSGS[action])
        return msgs

    # Construct an appropriate permission denied error message
    def get_permission_denied_msg(self, action):
        return RepManager.DENIED_MSGS.action
