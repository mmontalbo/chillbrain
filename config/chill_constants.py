from config import chill_config

REDDIT_PICS = "http://reddit.com/r/pics"
REDDIT_FUNNY = "http://reddit.com/r/funny"
REDDIT_WTF = "http://reddit.com/r/wtf"
REDDIT_ADVICE_ANIMALS = "http://reddit.com/r/adviceanimals"

sources_list = [REDDIT_PICS, REDDIT_FUNNY, REDDIT_WTF, REDDIT_ADVICE_ANIMALS]

REQUEST_ACTION_VOTE = 'vote'
REQUEST_ACTION_SKIP = 'skip'
REQUEST_ACTION_SHARE = 'share'
REQUEST_ACTION_REPORT = 'report'
REQUEST_ACTION_UPLOAD = 'upload'
request_actions_list = [REQUEST_ACTION_VOTE, REQUEST_ACTION_SKIP, REQUEST_ACTION_SHARE, REQUEST_ACTION_REPORT, REQUEST_ACTION_UPLOAD]

# URL configuration
if chill_config.isDebug():
    BASE_URL = 'http://localhost:8080/'
else:
    BASE_URL = 'http://usechillbrain.appspot.com/'

SHARE_URL = BASE_URL + "enter?"
IMG_URL = BASE_URL + "img?"
IMG_URL_TEMPLATE = IMG_URL + "h=%s"
LOGIN_REDIRECT_URL = BASE_URL + ""
