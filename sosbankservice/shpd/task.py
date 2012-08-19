# -*- coding: utf-8 -*-
'''
Created on 2012-08-18

@author: Alan Yan
'''
import poplib
import email,os,json
import setting, helper
from models import Log, Customer
import django.core.exceptions as exceptions
from datetime import datetime

class TaskBase(object):
           
    '''
    task base for importing and exporting data
    '''
    def __class__(self, *args, **kw):
        
        self.do(*args, **kw)
        
    def do(self, *args, **kw):
        pass
    

class ImportTaskBase(TaskBase):
    
    def __init__(self):
        
        TaskBase.__init__() 
    
    def save2db(self, details):
        
        for p in details:
            result = Customer.objects.filter(name__exact = p.get('name'), custom_no__exact= p.get('customerNo'), branch_name__exact = p.get('branchName'))
            if len(result) == 1:
                'update'
                customer = result[0]
                customer.custom_no = p.get('cardNo')
            else:
                'insert'
                customer = Customer(name=p.get('name'), 
                                    custom_no = p.get('customerNo'), 
                                    branch_name = p.get('branchName'), 
                                    card_no = p.get('cardNo'), 
                                    mobile=p.get('mobile'))
            customer.save()
    
class EmailTask(ImportTaskBase):
    
    FILE_SOURCE = '0'
    
    STATUS_DOWNLOADED = 1
    STATUS_DATA_LOADED = 2
    
    def __init__(self):
        ImportTaskBase.__init__() 
    
    def do(self, *args, **kw):
        
        multiple_data = self.import_from_emial()
        self.read_to_db(multiple_data)
    
    def read_to_db(self, multiple_data):
        
        for log, encryptedFile in multiple_data:
            
            'read data from file'
            decryptedFile = encryptedFile + '_decrypted'
            datafile = helper.SHPDDataFile(encryptedFile, decryptedFile, helper.SHPDDataFile.TYPE_RECEIVE)
            dataset = datafile.process()
            
            'save details'
            self.save2db(dataset.get('details'))
            
            'save log'
            info_dict=json.loads(log.loginfo); 
            info_dict.update(dataset.get('header')); info_dict.update(decryptedfile=decryptedFile)
            log.info = json.dumps(info_dict)
            log.status = EmailTask.STATUS_DATA_LOADED
            log.save()
    
    def import_from_emial(self):
        
        ret = []
        
        connection = self._get_connection()
        emails, total_bytes = connection.stat()
        #print("{0} emails in the inbox, {1} bytes total".format(emails, total_bytes))
        # return in format: (response, ['mesg_num octets', ...], octets)
        msg_list = connection.list()
        print(msg_list)
        
        # messages processing
        for i in range(emails):
            
            ret_item = []
            connection = self._keep_alive(connection)
            
            response = connection.retr(i+1)
            # return in format: (response, ['line', ...], octets)
            lines = response[1]
            
            str_message = email.message_from_string("\n".join(lines))
            # print("Processing " + str(i))
    
            # save attach
            file_idx = 1
            for part in str_message.walk():
                
                if part.get_content_maintype() == 'multipart':
                    continue
    
                if part.get('Content-Disposition') is None:
                    continue
                
                print(part.get_content_type())
                
                filename = part.get_filename()
                if not(filename): continue
                
                'add suffix to filename'
                suffix = datetime.now().strftime('_%y%m%H%M%S_') + "_" + str(file_idx)  + "_" + EmailTask.FILE_SOURCE
                filename = filename + suffix
                
                email_digest = connection.uidl()
                if self._check_email(email_digest):
                    fp = open(os.path.join(setting.working_dir, filename), 'wb')
                    fp.write(part.get_payload(decode=1))
                    fp.close()
                    
                    'add log'
                    info = json.dumps(dict(status=EmailTask.STATUS_DOWNLOADED, encryptedfile=filename))
                    log = Log(identitiy=email_digest, type=Log.TYPE_CHOICES[1], info=info, status=0, op_id=0)
                    log.save(); ret_item.append(log)
                    
                    ret_item.append(filename)
                    ret.append(ret_item)
                    
                file_idx += 1
        
        connection.quit()
        return ret
        
    def _check_email(self, digest):
        
        try:
            emaillog = Log.objects.get(identitiy__iexact = digest)
        except exceptions.ObjectDoesNotExist:
            return True
        
        return emaillog
    
    def _keep_alive(self,connection):
        
        try:
            connection.noop()
        except Exception:
            return self._get_connection()
        
    def _get_connection(self):
        
        connection = poplib.POP3('pop3.126.com')
        connection.set_debuglevel(1)
        connection.user(setting.USERNAME)
        connection.pass_(setting.PASS)

class UplaodFileTask(ImportTaskBase):
    def __init__(self):
        ImportTaskBase.__init__() 
        

class ExportTask(TaskBase):
    pass
    
            
    