# -*- coding: utf-8 -*-
from django.db import models

# Create your models here.

class Customer(models.Model):
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=120)  # 姓名
    customer_no = models.CharField(max_length=60)  #客户号
    branch_name = models.CharField(max_length=120)  #分行名称
    card_no = models.CharField(max_length=100) #卡号
    service_expire = models.IntegerField()    #充值点数/服务期限
    mobile = models.CharField(max_length=20)  #手机号
    identifier = models.CharField(max_length=12)   # 客户ID后6位
     
    service_count = models.IntegerField()   # 服务次数
    comments=models.TextField()
    
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

class Log(models.Model):
    
    TYPE_CHOICES = (
        (1, 'Import data from email.'),
        (2, 'Import data from file uploaded.'),
        (3, 'Export data and transfer data automatically.'),
        (4, 'Export data and transfer data manually.'),
    )
    
    identitiy = models.CharField(max_length=120)
    type = models.SmallIntegerField(choices=TYPE_CHOICES)
    info = models.TextField()
    status = models.SmallIntegerField()
    op_date = models.DateTimeField(auto_now_add=True)
    op_id = models.IntegerField()
         
