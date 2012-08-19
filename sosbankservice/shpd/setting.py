'''
Created on Aug 14, 2012

@author: yan
'''
import os

USERNAME = 'yanxs_hust'
PASS = 'ayan7084'
pop3_server = ''
working_dir = os.path.join(os.getcwdu(), 'data', 'workingfolder')
achive_dir = os.path.join(os.getcwdu(), 'data', 'archive')

decrypt_key = '999999'
encrypt_key = '123456'
encrypt_cmd_path = '"' + os.path.join(os.getcwd(), 'tools', 'my_des.exe') + '"'
