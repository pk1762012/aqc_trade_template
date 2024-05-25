import os
from . import auth
import time
import configparser

dir_path = os.path.dirname(os.path.realpath(__file__))

conf_file_path = dir_path+'/configuration.ini'
config = configparser.RawConfigParser()
config.read(conf_file_path)

def get_env():
    return config
def get_cookie():
    cookie_path = dir_path+'/cookie.txt'
    f = open(cookie_path,'r')
    cookie_ = f.readline()
    f.close()
    return cookie_

def write_cookie(cookie):
    cookie_path = dir_path+'/cookie.txt'
    f = open(cookie_path,'w')
    f.write(cookie)
    f.close()

def get_jwt():
    jwt_path = dir_path+'/jwt.txt'
    f = open(jwt_path,'r')
    jwt_ = f.readline()
    f.close()
    return jwt_

def write_jwt(jwt):
    jwt_path = dir_path+'/jwt.txt'
    f = open(jwt_path,'w')
    f.write(jwt)
    f.close()

auth = auth.EncryptionClient()

def time_milli_second(expiry_time=False):
    if expiry_time:
        return int((time.time()+24*3600)*1000.0)  ##assuming expiry time is 24 hr from now
    return int(time.time()*1000.0)