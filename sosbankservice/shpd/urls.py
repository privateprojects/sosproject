#!/usr/bin/env python
#coding=utf8

from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r"^time/$", 'shpd.views.current_datetime'), #should use the full path
    url(r"^customer_info/$", 'shpd.views.operate_customer_info'),
    url(r"^upload_customer_report/$", 'shpd.views.upload_customer_report'),
)