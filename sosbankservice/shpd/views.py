#!/usr/bin/env python
#coding=utf8

import datetime, urllib

from django.http import HttpResponse
from django.template import  RequestContext
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.views.decorators.csrf import csrf_exempt
import os

from models import Customer
from shpd.results import CustomerQueryResults, CustomerUpdateResults
from forms import UploadFileForm, CustomerQueryForm, CustomerQueryControlInfo, CustomerUpdateForm, CommonOperateControlInfo
from shpd import config

def commons_reponse(*args, **kwargs):
    response = HttpResponse(*args, **kwargs)
    response["P3P"] = 'CP="IDC DSP COR ADM DEVi TAIi PSA PSD IVAi IVDi CONi HIS OUR IND CNT"'
    return response

def response_with_error(msg):
    #todo: uniform the error format into json

    msg = ("Error! " + msg)
    return HttpResponse(msg)


def response_in_json(json):
    return HttpResponse(json, mimetype='application/json')


def response_as_file(request, raw_data, mime_type, filename):
    response = HttpResponse(raw_data)

    mime_type = mime_type or 'application/octet-stream'
    response['Content-Type'] = mime_type
    response['Content-Length'] = len(raw_data)
    response['Content-Encoding'] = "utf-8"
    filename_header = 'filename*=UTF-8\'\'%s' % urllib.quote(filename.encode('utf-8'))

    # To inspect details for the below code, see http://greenbytes.de/tech/tc2231/
    #    if u'WebKit' in request.META['HTTP_USER_AGENT']:
    #        # Safari 3.0 and Chrome 2.0 accepts UTF-8 encoded string directly.
    #        filename_header = 'filename=%s' % filename.encode('utf-8')
    #    else:  # elif u'MSIE' or u'Mozilla' in request.META['HTTP_USER_AGENT']
    #        # IE < 7 does not support internationalized filename at all. so filename should be english
    #        # For others like Firefox, we follow RFC2231 (encoding extension in HTTP headers).
    #        filename_header = 'filename*=UTF-8\'\'%s' % urllib.quote(filename.encode('utf-8'))

    response['Content-Disposition'] = 'attachment; ' + filename_header
    return response

def current_datetime(request):
    now = datetime.datetime.now()
    text = "now: %s"%now
    return HttpResponse(text)



def query_customer_info(request):
    #request.REQUEST = request.POST or request.GET
    if (len(request.REQUEST.keys()) > 0):
        form = CustomerQueryForm(request.REQUEST)

        if (not form.is_valid()):
            return response_with_error("invalid request data")

        response_type = ""
        control_info = CustomerQueryControlInfo(request.REQUEST)
        extra_info = {}

        start = 0
        end = None #means no limit
        if ( control_info.is_valid() ):
            page_size = control_info.get_value_or_default("page_size")
            if (page_size <= -1):
                page_current = 1
            else:
                page_current = control_info.get_value_or_default("page_current")
                start = (page_current-1) * page_size
                end = start+page_size

            response_type = control_info.get_value_or_default("response_type")
            extra_info["page_size"] = page_size
            extra_info["page_current"] = page_current

        q = form.get_query_conditions()
        if (len(q) > 0):
            results = Customer.objects.filter(*q)

            total_num = extra_info["item_total"] = results.count()

            order_by = form.get_value_or_default("order_by")
            results = results.order_by(order_by)[start:end]
            results = CustomerQueryResults(results);


            if (response_type == "json"):
                json_data = results.get_json(extra_info=extra_info)
                return response_in_json(json_data)


            elif (response_type == "file"):
                csv_data = results.get_csv()
                return response_as_file(request, csv_data, "text/csv", "search_all_results.csv")

            else: # (response_type == "html"):
                json_data = results.get_json(extra_info=extra_info)
                return render_to_response( "query_customer_info.html",
                        {"customer_query_form":form,
                         "meta_map": json_data
                    },
                    context_instance=RequestContext(request)
                )



    return render_to_response( "query_customer_info.html",
            {"customer_query_form":CustomerQueryForm(),
             "meta_map": {}
        },
        context_instance=RequestContext(request)
    )


def update_customer_info(request):
    if (len(request.REQUEST.keys()) <= 0):
        return response_with_error("no request data")

    form = CustomerUpdateForm(request.REQUEST)
    if (not form.is_valid()):
        return response_with_error("invalid request data")

    id = form.cleaned_data["id"]
    service_count_delta = form.cleaned_data["service_count_delta"]
    if (service_count_delta not in [1, -1]) :
        return response_with_error("service_count_delta should be 1 or -1")

    try:
        customer_record = Customer.objects.get(id=id)
        service_count = customer_record.service_count + service_count_delta
        Customer.objects.filter(id=id).update(service_count=service_count)
    except ObjectDoesNotExist:
        return response_with_error("no such customer record with id:" + str(id))
    except MultipleObjectsReturned:
        return response_with_error("multiple customer records returned with id:" + str(id))

    results = CustomerUpdateResults(id=id, service_count=service_count)
    results = response_in_json(results.get_json())
    return results


def dumb(request):
    return response_with_error("not implemented")


@csrf_exempt
def operate_customer_info(request):
    #django 1.4 is still not support RESTful api, has not 'PUT' or 'DELETE'

    if (request.method == "GET" ):
        return query_customer_info(request)

    elif (request.method == "POST"):
        control_info = CommonOperateControlInfo(request.REQUEST)
        if (control_info.is_valid()):
            op = control_info.cleaned_data["op"]
            handler = globals().get(op + "_customer_info") or dumb
            return handler(request)

        else:
            results = "invalid operate type"

    else:
        results = "invalid access method"

    return response_with_error(results)





def upload_customer_report(request):
    result = ""

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if (form.is_valid()):
            upload_file = request.FILES['upload_file']
            filename = upload_file.name
            store_path = os.path.join(config.WORKING_DIR, filename)
            store_file = open(store_path, "wb")

            #upload_file.read()
            for content in upload_file.chunks():
                store_file.write(content)
                #print content[:100]

            store_file.close()
            #result = filename + " is uploaded successfully"
            result = "ok"
        else:
            result = "invalid upload"

        return HttpResponse(result)

    else:
        form = UploadFileForm()
        return render_to_response( "upload_customer_report.html",
                {"upload_customer_report_form":form },
            context_instance=RequestContext(request) )

