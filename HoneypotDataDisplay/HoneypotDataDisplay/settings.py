import os
from configparser import SafeConfigParser

def init():
    ConfigFilePath = os.path.dirname(os.path.realpath(__file__)) + '/config.ini'
    print(ConfigFilePath)

    parser = SafeConfigParser()
    parser.read(ConfigFilePath)

    print(parser.get('PostgreSQL', 'ConnectionString'))

    global ConnectionString 
    ConnectionString = parser.get('PostgreSQL', 'ConnectionString')
    
    global DebugEnabled
    DebugEnabled = parser.getboolean('Etc', 'Debug')