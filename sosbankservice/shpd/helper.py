# -*- coding: utf-8 -*-
'''
Created on Aug 14, 2012

@author: yan
'''
import setting
import os, shutil
from datetime import datetime

class SHPDDataFile(object):
    
    '报文编号'
    TYPE_RECEIVE = '1' # 提供给供应商的充值点数报文
    TYPE_REPLY = '2'   # 服务商回复给积分系统报文
    TYPE_UPDATE = '3'  # 更新龙腾卡号报文
    
    'header fields'
    TYPE = 'BAOWBH'
    PARTNER = 'DANWBH'
    COUNT = 'ZONGBS' 
    RPT_DATE = 'CHUZRQ'
    
    'detail fields'
    NAME = 'name'
    CUSTOMER_NO = 'customerNo'
    BRANCH = 'branchName'
    CARD_NO = 'cardNo'
    MOBILE = 'mobile'
    SERV_CNT = 'serviceCount'
    
    def __init__(self, 
                 file_encrypted, 
                 file_decrypted, 
                 dataset = None,
                 file_type = TYPE_RECEIVE):
        
        self.file_encrypted = file_encrypted 
        self.file_decrypted = file_decrypted
        self.dataset = dataset  
        self.file_type = file_type
        
    def process(self):
        
        if self.file_type == SHPDDataFile.TYPE_RECEIVE or self.file_type == SHPDDataFile.TYPE_UPDATE:
            
            if self.encrypt(encrypt = False):    #decrypt
                
                'read file'
                self._read_from_file()
                
            else:
                'send alerting email'
            
        elif self.file_type == SHPDDataFile.TYPE_REPLY:
            
            if self.dataset:
                
                'write to file'
                self._write_to_file()
                
                'encrypt'
                self.encrypt(encrypt=True)
                
        return self.dataset
        
    def archive(self):
        
        'achive encrypted file'
        filename = os.path.basename(self.file_encrypted)
        des = os.path.join(setting.achive_dir, filename)
        shutil.move(self.file_encrypted, des)
        
        'achive decrypted file'
        filename = os.path.basename(self.file_decrypted)
        des = os.path.join(setting.achive_dir, filename)
        shutil.move(self.file_decrypted, des)
        
    def _read_from_file(self):
        
        with open(self.file_decrypted, 'r') as f:
            
            lines = f.readlines()
            headerLines = lines[0,3]
            detailLines = lines[5,]
            
            header = {}
            filetype = (headerLines[0].split(":")[1]).strip(); header[SHPDDataFile.TYPE] = filetype
            partner = (headerLines[1].split(":")[1]).strip(); header[SHPDDataFile.PARTNER]=partner 
            count = (headerLines[2].split(":")[1]).strip(); header[SHPDDataFile.COUNT]=count 
            report_date = (headerLines[3].split(":")[1]).strip(); header[SHPDDataFile.RPT_DATE]=report_date 
            
            self.file_type = filetype
            
            details = []
            detail = {}
            for ln in detailLines:
                
                values = ln.split('|')
                
                if filetype == self.TYPE_RECEIVE:
                    detail[SHPDDataFile.NAME] = values[0].strip()
                    detail[SHPDDataFile.CUSTOMER_NO] = values[1].strip()
                    detail[SHPDDataFile.BRANCH] = values[2].strip()
                    detail[SHPDDataFile.CARD_NO] = values[3].strip()
                    detail[SHPDDataFile.MOBILE] = values[5].strip()
                elif filetype == self.TYPE_UPDATE:
                    detail[SHPDDataFile.NAME] = values[0].strip()
                    detail[SHPDDataFile.CUSTOMER_NO] = values[1].strip()
                    detail[SHPDDataFile.BRANCH] = values[2].strip()
                    detail[SHPDDataFile.CARD_NO] = values[3].strip() 
                else:
                    pass
                
                details.append(detail)
            
            self.dataset = {'header':header, 'details':details}
    
    def _write_to_file(self):
        
        SOS_PARTNER_CODE = '03'
        
        with open(self.file_decrypted, 'w') as f:
            
            header = {}
            details = self.dataset.get('details')
            
            headerlines = []
            detaillines = []
            
            count = len(details)
            rpt_date = datetime.now().strftime('%Y%m%d')
            
            headerlines.append(':'.join(self.TYPE,self.TYPE_REPLY))
            headerlines.append(':'.join(self.PARTNER, SOS_PARTNER_CODE) )
            headerlines.append(':'.join(self.COUNT, count))
            headerlines.append(':'.join(self.RPT_DATE, rpt_date))
            
            header[self.TYPE]=self.TYPE_REPLY
            header[self.PARTNER]= SOS_PARTNER_CODE
            header[self.COUNT]= count
            header[self.RPT_DATE]= rpt_date
            
            for detail in details:
                
                name = detail.get(SHPDDataFile.NAME)
                customer = detail.get(SHPDDataFile.CUSTOMER_NO)
                branch = detail.get(SHPDDataFile.BRANCH)
                cardno = detail.get(SHPDDataFile.CARD_NO)
                servCount = detail.get(SHPDDataFile.SERV_CNT)
                point1 = '0'
                point2 = '0'
                point3 = '0'
                line = '|'.join(name,customer,branch,cardno,servCount,point1,point2,point3)
                                
                detaillines.append(line)
            
            'write header'
            f.write('\n'.join(headerlines))
            f.write('====================================\n')
            f.write('\n'.join(detaillines))
        
        self.dateset['header'] = header
        
    def encrypt(self, encrypt=True):
        
        '''
        if encrypt is true, encrypt the file. otherwise decrypt file
        '''
        if encrypt:
            source_file = self.file_decrypted
            target_file = self.file_encrypted
            secret_key = setting.encrypt_key
        else:
            source_file = self.file_encrypted
            target_file = self.file_decrypted
            secret_key = setting.decrypt_key
        
        args = ' -u ' + secret_key + " " + source_file + " " + target_file
        cmd = setting.encrypt_cmd_path + " " + args
        
        print cmd
        
        x=os.popen(cmd)
        
        for i in x.readlines():  
            # TODO how to jugde if decryption has been performed correctly??
            # return False
            pass
        
        return True
