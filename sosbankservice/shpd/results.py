#!/usr/bin/env python
#coding=utf-8

import re, datetime
import csv, codecs, cStringIO

from django.utils import dateparse, simplejson
from models import Customer
from shpd.helper import restrict_field_names
from shpd.displayers import DisplayerFactory

displayer_factory = DisplayerFactory.get_instance()

class AbstractQueryResults(object):
    _model = None
    col_names_in_order = [] #we use this to control the transfer and display order, should be overridden by subclass
    col_names_to_display_names = {} #should be overridden by subclass

    def __init__(self, results):
        self.results = results

    def _trim_data(self, row, col_name):
        return unicode(row.__dict__.get(col_name, "")).strip()

    def _decorate_data_for_html_table(self, row, col_name):
        #by default, just trim the data
        return self._trim_data(row, col_name)

    def _decorate_data_for_json(self, row, col_name):
        return self._trim_data(row, col_name)

    def _decorate_data_for_csv(self, row, col_name):
        return self._trim_data(row, col_name)

    def get_html_table(self):
        head_str = ""; body_str = '"'
        col_names_in_order = self.__class__.col_names_in_order
        col_names_to_display_names = self.__class__.col_names_to_display_names
        results = self.results

        if (col_names_in_order and results):
            #col_names = [unicode(k.attname) for k in model_class._meta.fields]
            col_str = ""
            for col_name in col_names_in_order:
                display_name = col_names_to_display_names and col_names_to_display_names.get(col_name) or col_name
                col_str += ( "<th>" + display_name + "</th>" )

            head_str += ("<tr>" + col_str + "</tr>")

            for row in results:
                col_str = ""
                for col_name in col_names_in_order:
                    col_str += ( "<td>" + self._decorate_data_for_html_table(row, col_name) + "</td>" )

                body_str += ("<tr>" + col_str + "</tr>")

        ret_str = "<thead>" + head_str + "</thead>" +\
                  "<tbody>" + body_str + "</tbody>"

        return ("<table>" + ret_str + "</table>")


    def get_json(self, json_type = "custom", extra_info = {}):
        raw_map = {}
        col_names_in_order = self.__class__.col_names_in_order
        col_names_to_display_names = self.__class__.col_names_to_display_names
        results = self.results or []

        if (col_names_in_order):

            if (json_type == "custom"):
                item_data = []
                item_size = len(results)
                for row in results:
                    row_values = [] #row_values = {}
                    for col_name in col_names_in_order:
                        #row_values[col_name] = self._decorate_data_for_json(row, col_name)
                        row_values.append( self._decorate_data_for_json(row, col_name) )

                    item_data.append(row_values)

                raw_map["item_names"] = col_names_in_order
                raw_map["item_names_for_display"] = col_names_to_display_names
                raw_map["item_data"] = item_data
                raw_map["item_total"] = item_total = extra_info.get("item_total", item_size)

                raw_map["page_current"] = extra_info.get("page_current", 1)
                raw_map["page_size"] = page_size = extra_info.get("page_size", item_size)
                raw_map["page_total"] = int( (item_total + page_size - 1) / page_size )

                raw_map["order_by"] = extra_info.get("page_size", "")

        return simplejson.dumps(raw_map)


    def get_csv(self, dialect=csv.excel, encoding="utf-8" ):
        col_names_in_order = self.__class__.col_names_in_order
        col_names_to_display_names = self.__class__.col_names_to_display_names

        queue = cStringIO.StringIO()
        writer = csv.writer(queue, dialect=dialect)
        encoder = codecs.getincrementalencoder(encoding)()

        stream = cStringIO.StringIO()
        for row in self.results:
            row_values = []
            for col_name in col_names_in_order:
                col_value = self._decorate_data_for_csv( row, col_name)
                row_values.append(col_value.encode("utf-8"))

            writer.writerow(row_values)

            # Fetch UTF-8 output from the queue ...
            data = queue.getvalue()
            data = data.decode("utf-8")
            # ... and re-encode it into the target encoding
            data = encoder.encode(data)
            # write to the target stream
            stream.write(data)
            # empty queue
            queue.truncate()

        return stream.getvalue()


class CustomerQueryResults(AbstractQueryResults):
    _model = Customer
    col_names_in_order = restrict_field_names(_model,
        ["id", "name", "customer_no","branch_name", "card_no", "mobile", "service_count"])

    col_names_to_display_names = displayer_factory.get_displayer("customer_info")



class CustomerUpdateResults(object):
    def __init__(self, **kwargs):
        self.id = kwargs["id"]
        self.service_count = kwargs["service_count"]

    def get_json(self):
        return simplejson.dumps( self.__dict__ )