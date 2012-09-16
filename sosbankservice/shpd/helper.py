# -*- coding: utf-8 -*-
'''
Created on Aug 14, 2012

@author: yan
'''
import config
import os, shutil
from datetime import datetime
    
class SHPDDataFile(object):
    
    '报文编号'
    TYPE_RECEIVE = '1' # 提供给供应商的充值点数报文
    TYPE_REPLY = '2'   # 服务商回复给积分系统报文
    TYPE_UPDATE = '3'  # 更新龙腾卡号报文
    
    'parter code of SOS'
    SOS_PARTNER_CODE = '03'  # this assigned by protocol and unchangeable
    
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
    SERV_EXPIRE = 'serviceExpire'
    IDENTIFIER = 'identifier'
    
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
                'send alerting email'  #TODO
            
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
        des = os.path.join(config.ACHIVE_DIR, filename)
        shutil.move(self.file_encrypted, des)
        
        'achive decrypted file'
        filename = os.path.basename(self.file_decrypted)
        des = os.path.join(config.ACHIVE_DIR, filename)
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
                    # FOR DOC TYPE 1 提供给供应商的充值点数报文格式
                    detail[SHPDDataFile.NAME] = values[0].strip()   # 姓名
                    detail[SHPDDataFile.CUSTOMER_NO] = values[1].strip()   # 客户号
                    detail[SHPDDataFile.BRANCH] = values[2].strip()  # 分行名称
                    detail[SHPDDataFile.CARD_NO] = values[3].strip() # 龙腾卡号
                    detail[SHPDDataFile.SERV_EXPIRE] = values[4].strip() # 充值点数/服务期限
                    detail[SHPDDataFile.MOBILE] = values[5].strip()  # 手机号
                    detail[SHPDDataFile.IDENTIFIER] = values[5].strip()  # 证件号末6位
                elif filetype == self.TYPE_UPDATE:
                    # FOR DOC TYPE 3 更新龙腾卡号报文格式 
                    detail[SHPDDataFile.NAME] = values[0].strip()   # 姓名
                    detail[SHPDDataFile.CUSTOMER_NO] = values[1].strip()   # 客户号
                    detail[SHPDDataFile.BRANCH] = values[2].strip()   # 分行名称
                    detail[SHPDDataFile.CARD_NO] = values[3].strip()   # 更新龙腾卡号
                else:
                    pass
                
                details.append(detail)
            
            self.dataset = {'header':header, 'details':details}
    
    def _write_to_file(self):
        
        with open(self.file_decrypted, 'w') as f:
            
            header = {}
            details = self.dataset.get('details')
            
            headerlines = []
            detaillines = []
            
            count = len(details)
            rpt_date = datetime.now().strftime('%Y%m%d')
            
            headerlines.append(':'.join(self.TYPE,self.TYPE_REPLY))    # BAOWBH（报文编号）
            headerlines.append(':'.join(self.PARTNER, SHPDDataFile.SOS_PARTNER_CODE) )    # DANWBH（单位编号）
            headerlines.append(':'.join(self.COUNT, count))  # ZONGBS（总笔数）
            headerlines.append(':'.join(self.RPT_DATE, rpt_date))  # CHUZRQ（出账日期）
            
            header[self.TYPE]=self.TYPE_REPLY
            header[self.PARTNER]= SHPDDataFile.SOS_PARTNER_CODE
            header[self.COUNT]= count
            header[self.RPT_DATE]= rpt_date
            
            for detail in details:
                
                name = detail.get(SHPDDataFile.NAME)  # 姓名
                customer = detail.get(SHPDDataFile.CUSTOMER_NO)  # 客户号
                branch = detail.get(SHPDDataFile.BRANCH) #分行名称
                cardno = detail.get(SHPDDataFile.CARD_NO)  # 卡号
                servCount = detail.get(SHPDDataFile.SERV_CNT) #上月使用点(次)数
                point1 = '0'    # 本月充值点数
                point2 = '0'    # 当月可用点数
                point3 = '0'    # 累计充值点数
                line = '|'.join(name,customer,branch,cardno,servCount,point1,point2,point3)  
                                
                detaillines.append(line)
            
            'write header'
            f.write('\n'.join(headerlines))
            f.write('-----------------------------------\n')
            f.write('\n'.join(detaillines))
        
        self.dateset['header'] = header
        
    def encrypt(self, encrypt=True):
        
        '''
        if encrypt is true, encrypt the file. otherwise decrypt file
        '''
        if encrypt:
            source_file = self.file_decrypted
            target_file = self.file_encrypted
            secret_key = config.ENCRYPT_KEY
        else:
            source_file = self.file_encrypted
            target_file = self.file_decrypted
            secret_key = config.DECRYPT_KEY
        
        args = ' -u ' + secret_key + " " + source_file + " " + target_file
        cmd = config.ENCRYPT_CMD_PATH + " " + args
        
        print cmd
        
        x=os.popen(cmd)
        
        for i in x.readlines():  
            # TODO how to jugde if decryption has been performed correctly??
            # return False
            pass
        
        return True

def is_empty_string(target):
    return target is None or len(unicode(target).strip()) <= 0

def get_field_names(model_class):
    return [i.attname for i in model_class._meta.fields]

def get_order_by_choices(model_class):
    return [(i.attname, i.attname) for i in model_class._meta.fields]

def restrict_field_names(model_class, field_name_list):
    ori_set = set([i.attname for i in model_class._meta.fields])
    target_set = set(field_name_list)
    delta_set = target_set - ori_set
    if (len(delta_set) > 0):
        bad_names = ",".join(list(delta_set))
        raise Exception("%s is not in model %s!"%(bad_names, model_class.__name__))

    return field_name_list
