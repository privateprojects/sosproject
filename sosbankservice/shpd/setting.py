'''
Created on Aug 14, 2012

@author: yan
'''
import os

USERNAME = 'yanxs_hust'
PASS = '775800'
pop3_server = 'pop3.163.com'
working_dir = os.path.join(os.getcwdu(), 'data', 'workingfolder')
achive_dir = os.path.join(os.getcwdu(), 'data', 'archive')

decrypt_key = '999999'
encrypt_key = '123456'
encrypt_cmd_path = '"' + os.path.join(os.getcwd(), 'tools', 'my_des.exe') + '"'
