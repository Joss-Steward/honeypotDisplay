import os
from configparser import SafeConfigParser

def init():
    ConfigFilePath = os.path.dirname(os.path.realpath(__file__)) + '/config.ini'
    print("Looking for config file at: " + ConfigFilePath)

    parser = SafeConfigParser()
    parser.read(ConfigFilePath)

    global ConnectionString 
    ConnectionString = parser.get('PostgreSQL', 'ConnectionString')
    
    global DebugEnabled
    DebugEnabled = parser.getboolean('Etc', 'Debug')