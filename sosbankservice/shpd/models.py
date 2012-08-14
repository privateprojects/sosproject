from django.db import models

# Create your models here.

class customers(models.Model):
    
    # 姓名|客户号|分行名称|卡号|充值点数|手机号
    name = models.CharField(max_length=120)
    custom_no = models.CharField(max_length=60)
    branch_name = models.CharField(max_length=120)
    mobile = models.CharField(max_length=20)
    service_count = models.IntegerField() 
    comments=models.TextField()
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

class log(models.Model):
    
    TYPE_CHOICES = (
        (1, 'Import data from email.'),
        (2, 'Import data from file uploaded.'),
        (3, 'Export data and transfer data automatically.'),
        (4, 'Export data and transfer data manually.'),
    )
    
    identitiy = models.CharField(max_length=120)
    type = models.SmallIntegerField(choices=TYPE_CHOICES)
    info = models.TextField()
    op_date = models.DateTimeField(auto_now_add=True)
    op_id = models.IntegerField()
         
