#!/usr/bin/env python
#coding=utf-8

from django import forms
from django.db.models import Q


## mix-ins
from shpd.helper import is_empty_string, restrict_field_names, get_order_by_choices
from shpd.models import Customer


class CommonForm(forms.Form):
    def get_value_or_default(self, name):
        cls = self.__class__
        if (name not in cls.base_fields.keys()):
            return None

        return (self.cleaned_data[name] or cls.base_fields[name].initial)



class CommonQueryForm(CommonForm):
    _model = None
    _fields_from_model = []

    """convetion: operator should be end with OPERATOR_POSTFIX"""
    OPERATOR_POSTFIX = "_operator"
    OPERATOR_CHOICES = (
        ("exact", "=="),
        ("iexact", "== with case-insensitive"),
        ("contains", "%target%"),
        ("icontains", "%target% with case-insensitive"),
        ("startswith", "target%"),
        ("istartswith", "target% with case-insensitive"),
        ("endswith", "%target"),
        ("iendswith", "%target with case-insensitive"),
        ("gt",  ">"),
        ("gte", ">="),
        ("lt",  "<"),
        ("lte", "<="),
        ("in", "in [a,b,c, ...]"),
    )

    def get_query_conditions(self):
        cls = self.__class__()
        query_conditions = []
        if (self.is_valid()):
            for field_name in cls._fields_from_model :#self.fields.items()
                field_value = self.get_value_or_default(field_name)
                if ( not is_empty_string(field_value)) :
                    operator_name = field_name + cls.OPERATOR_POSTFIX
                    operator_value = self.get_value_or_default(operator_name)

                    #here we use django QuerySet's convetion to make the Q object
                    condition = str(field_name) + "__" + str(operator_value)
                    query_conditions.append( Q(**{condition:(field_value)}) )

        return query_conditions


class CommonOperateControlInfo(CommonForm):

    OP_CHOICES = (
        ("query", "Query Action"),
        ("create", "Create Action"),
        ("update",  "Update Action"),
        ("delete", "Delete Action"),
        )
    op = forms.ChoiceField(required=False, initial=0, choices=OP_CHOICES)



class CustomerQueryForm(CommonQueryForm):
    _model = Customer
    _fields_from_model = restrict_field_names(_model, ["name", "customer_no", "branch_name"])

    name = forms.CharField(required=False, max_length=120)
    customer_no = forms.CharField(required=False, max_length=60)
    branch_name = forms.CharField(required=False, max_length=120)

    name_operator = forms.ChoiceField(required=False, choices=CommonQueryForm.OPERATOR_CHOICES, initial="icontains")
    customer_no_operator = forms.ChoiceField(required=False, choices=CommonQueryForm.OPERATOR_CHOICES, initial="iexact")
    branch_name_operator = forms.ChoiceField(required=False, choices=CommonQueryForm.OPERATOR_CHOICES, initial="iexact")

    order_by = forms.ChoiceField(required=False, choices=get_order_by_choices(_model), initial="modified")


class CustomerQueryControlInfo(CommonForm):
    page_size = forms.IntegerField(required=False, widget=forms.HiddenInput(), initial=20)
    page_current = forms.IntegerField(required=False, widget=forms.HiddenInput(), initial=1)

    RESPONSE_TYPE_CHOICES = (
        ("html", "Html Type"),
        ("json", "Json Type"),
        ("file", "File Type")
        )
    response_type = forms.ChoiceField(required=False, initial="html", choices=RESPONSE_TYPE_CHOICES )



class CustomerUpdateForm(CommonForm):
    id = forms.CharField(max_length=255, required=True)
    service_count_delta = forms.IntegerField(required=True)


class UploadFileForm(CommonForm):
    upload_file = forms.FileField()
    #upload_notes = forms.CharField(required=False, max_length=128)