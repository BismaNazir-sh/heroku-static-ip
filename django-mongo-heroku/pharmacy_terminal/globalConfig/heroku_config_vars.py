
try:
    import environ

    env = environ.Env()
    environ.Env.read_env()
except:
    pass

try:
    CONFIG_APP_NAME = env.str('APP_NAME', default="pharmacy-terminal-dev")
except:
    CONFIG_APP_NAME = "pharmacy-terminal-dev"

try:
    APP_DOMAIN = env.str('APP_DOMAIN', default="dev-ship.5axis.health")
except:
    APP_DOMAIN = "dev-ship.5axis.health"

try:
    GB_APP_HEROKU_DOMAIN = env.str('GB_APP_HEROKU_DOMAIN', default="global-backend-development.herokuapp.com")
except:
    GB_APP_HEROKU_DOMAIN = "global-backend-development.herokuapp.com"

try:
    APP_HEROKU_DOMAIN = env.str('APP_HEROKU_DOMAIN', default="pharmacy-terminal-dev-776c45c40a72.herokuapp.com")
except:
    APP_HEROKU_DOMAIN = "pharmacy-terminal-dev-776c45c40a72.herokuapp.com"



try:
    CONFIG_MONGO_URI = env.str('MONGO_URI', default="mongodb://dev:oaiipv8wyg912urtn@202.163.113.3:27017/sea-turtle")
except:
    CONFIG_MONGO_URI = "mongodb://dev:oaiipv8wyg912urtn@202.163.113.3:27017/sea-turtle"


try:
    CONFIG_REDIS_URL = env.str('REDIS_URL', default="rediss://:p7c6dc45036b21c6434f37258dcb62459d68512b36071c92498bb435a27df2002@ec2-54-86-76-171.compute-1.amazonaws.com:22439")
except:
    CONFIG_REDIS_URL = "rediss://:p7c6dc45036b21c6434f37258dcb62459d68512b36071c92498bb435a27df2002@ec2-54-86-76-171.compute-1.amazonaws.com:22439"    

try:
    QUOTAGUARDSTATIC_URL = env.str('QUOTAGUARDSTATIC_URL')
except:
    QUOTAGUARDSTATIC_URL = ''

    
FEDEX_API = ""
FEDEX_CLIENT_ID = ""
FEDEX_CLIENT_SECRET = ""
FEDEX_ACCOUNT_NUMBER = ""