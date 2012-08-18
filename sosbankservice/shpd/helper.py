'''
Created on Aug 14, 2012

@author: yan
'''

import getpass, poplib
import email,os
import setting

class Task(object):
    
    def __class__(self, *args, **kw):
        
        self.do(*args, **kw)
        
    def do(self, *args, **kw):
        pass
        
class EmailTask(Task):
    
    def __init__(self):
        pass 
    
    def do(self, *args, **kw):
        self.import_from_emial()
    
    def import_from_emial(self):
        
        connection = poplib.POP3('pop3.126.com')
        connection.set_debuglevel(1)
        connection.user(setting.USERNAME)
        connection.pass_(setting.PASS)
        
        emails, total_bytes = connection.stat()
        print("{0} emails in the inbox, {1} bytes total".format(emails, total_bytes))
        # return in format: (response, ['mesg_num octets', ...], octets)
        msg_list = connection.list()
        print(msg_list)
    
        # messages processing
        for i in range(emails):
            
            response = connection.retr(i+1)
            # return in format: (response, ['line', ...], octets)
            lines = response[1]
            
            str_message = email.message_from_string("\n".join(lines))
            # print("Processing " + str(i))
    
            # save attach
            for part in str_message.walk():
                
                if part.get_content_maintype() == 'multipart':
                    continue
    
                if part.get('Content-Disposition') is None:
                    continue
                
                print(part.get_content_type())
                
                filename = part.get_filename()
                if not(filename): continue
                
                
    
                fp = open(os.path.join(setting.working_dir, filename), 'wb')
                fp.write(part.get_payload(decode=1))
                fp.close
        
        connection.quit()