# -*- coding: utf-8 -*-
'''
Created on 2012-08-18

@author: Alan Yan
'''
import poplib
import email,os,json
import config, helper
from models import Log, Customer
import django.core.exceptions as exceptions
from datetime import datetime

class TaskBase(object):
           
    '''
    task base for importing and exporting data
    '''
    def __class__(self):
        
        self.do()
        
    def do(self):
        pass
    

class ImportTaskBase(TaskBase):
    
    def __init__(self):
        
        TaskBase.__init__() 
    
    def save2db(self, details):
        
        for p in details:
            result = Customer.objects.filter(name__exact = p.get(helper.SHPDDataFile.NAME), 
                                             custom_no__exact= p.get(helper.SHPDDataFile.CUSTOMER_NO), 
                                             branch_name__exact = p.get(helper.SHPDDataFile.BRANCH))
            if len(result) == 1:
                'update'
                customer = result[0]
                customer.card_no = p.get(helper.SHPDDataFile.CARD_NO)
            else:
                'insert'
                customer = Customer(name=p.get(helper.SHPDDataFile.NAME), 
                                    custom_no = p.get(helper.SHPDDataFile.CUSTOMER_NO), 
                                    branch_name = p.get(helper.SHPDDataFile.BRANCH), 
                                    card_no = p.get(helper.SHPDDataFile.CARD_NO), 
                                    mobile=p.get(helper.SHPDDataFile.MOBILE))
            customer.save()
    
class EmailTask(ImportTaskBase):
    
    FILE_SOURCE = '0'  # from email attachement
    
    STATUS_DOWNLOADED = 1
    STATUS_DATA_LOADED = 2
    
    def __init__(self):
        ImportTaskBase.__init__() 
    
    def do(self):
        
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
            
            'archive file'
            datafile.archive()
    
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
                suffix = datetime.now().strftime('_%y%m%d%H%M%S_') + "_" + str(file_idx)  + "_" + EmailTask.FILE_SOURCE
                filename = filename + suffix
                
                email_digest = connection.uidl()
                if self._check_email(email_digest):
                    fp = open(os.path.join(config.WORKING_DIR, filename), 'wb')
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
        connection.user(config.USERNAME)
        connection.pass_(config.PASS)

class UplaodFileTask(ImportTaskBase):
    
    FILE_SOURCE = '1'  # from uploaded files
    
    STATUS_DATA_LOADED = 1
    
    def __init__(self, encryptedFile, operator_id):
        
        ImportTaskBase.__init__() 
        self.encryptedFile = encryptedFile
        self.operator_id = operator_id
    
    @classmethod
    def get_encrypte_filename(cls, filename):
        return filename+datetime.now().strftime('_%y%m%H%M%S_') + "_" + UplaodFileTask.FILE_SOURCE
    
    def do(self):
        
        decryptedFile = self.encryptedFile + "_decrypted"
        datafile = helper.SHPDDataFile(self.encryptedFile, decryptedFile, helper.SHPDDataFile.TYPE_RECEIVE)
        dataset = datafile.process()
        
        'save details'
        self.save2db(dataset.get('details'))
        
        'save log'    
        info_dict={} 
        info_dict.update(dataset.get('header')); 
        info_dict.update({'decryptedfile':decryptedFile, 'encryptedfile':self.encryptedFile})
        log = Log()
        log.info = json.dumps(info_dict)
        log.identitiy = self.encryptedFile
        log.status = UplaodFileTask.STATUS_DATA_LOADED
        log.op_id = self.operator_id
        log.save()
        
        'archive file'
        datafile.archive()

class ExportTask(TaskBase):
    
    FILE_SOURCE = '2'
    
    STATUS_FILE_ENCRYPTED = 1
    STATUS_SEND_EMAIL = 2
    
    def __init__(self, customers=None, operator_id=0):
        
        ImportTaskBase.__init__() 
        self.operator_id = operator_id
        self.customers = customers
    
    def do(self):
        
        decryptedFile = "sy03_"+datetime.now().strftime('_%y%m%H%M%S_') + UplaodFileTask.FILE_SOURCE +  '_decrpyted'
        encryptedFile = 'sy03_'+datetime.now().strftime('_%y%m%d')
        
        dataset = self._get_data()
        datafile = helper.SHPDDataFile(encryptedFile, decryptedFile, dataset=dataset, file_type=helper.SHPDDataFile.TYPE_UPDATE)
        
        dataset = datafile.process()
        
        'send email'
        
        
        'save log'    
        info_dict={} 
        info_dict.update(dataset.get('header')); 
        info_dict.update({'decryptedfile':decryptedFile, 'encryptedfile':self.encryptedFile})
        log = Log()
        log.info = json.dumps(info_dict)
        log.identitiy = decryptedFile
        log.status = ExportTask.STATUS_DATA_LOADED
        log.op_id = self.operator_id
        log.save()
        
        'archive file'
        datafile.archive()
              
    def _get_data(self):
        
        if not self.customers:
            customers = Customer.objects.all()
        else:
            customers = self.customers
        details = []
        for c in customers:
            detail = { helper.SHPDDataFile.NAME:c.name,
                       helper.SHPDDataFile.CUSTOMER_NO:c.customer_no,
                       helper.SHPDDataFile.BRANCH:c.branch_name,
                       helper.SHPDDataFile.SERV_CNT:str(c.service_count),
                      }
            
            details.append(detail)
            
        dataset = dict(details=details)
        return dataset
        