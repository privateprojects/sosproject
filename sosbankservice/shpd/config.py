'''
Created on Aug 14, 2012

@author: yan
'''
import os

USERNAME = 'yanxs_hust'
PASS = 'ayan7084'
POP3_SERVER = ''
SHPD_DIR = os.path.dirname(os.path.abspath(__file__))
WORKING_DIR = os.path.join(SHPD_DIR, 'data', 'workingfolder')
ACHIVE_DIR = os.path.join(SHPD_DIR, 'data', 'archive')
STATICFILES_DIR = os.path.join(SHPD_DIR, '../static')
TEMPLATES_DIR = os.path.join(SHPD_DIR, '../templates')


DECRYPT_KEY = '999999'
ENCRYPT_KEY = '123456'
ENCRYPT_CMD_PATH = '"' + os.path.join(os.getcwd(), 'tools', 'my_des.exe') + '"'

DB_SCHEMA = "sosbankservice"
DB_USER = "root"
DB_PASSWORD = "zimbra" #"1234"
DB_HOST = "localhost"
DB_PORT = "7306" #"3306"

LANGUAGE = "en"