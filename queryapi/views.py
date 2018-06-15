from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from functools import reduce
import json
import requests
import pprint
#=====================================================================
# This is the function to split each rows by underscore to make group
#=====================================================================

def grouping(prev, current):
    mainkey = current[0].split('__')[0]
    supportkey = current[0].split('__')[1]
    if mainkey not in prev.keys():
        prev[mainkey] = [{}]
    prev[mainkey][0][supportkey] = current[1]
    return prev

def addobject(x, y):
    (key, value) = y
    x[key] = value
    return x

def items_to_dict(items):
    return reduce(addobject, items, {})

def group_underscore_key(row):
    data_with_underscore = filter(lambda item: "__" in item[0], row.items())
    data_without_underscore = items_to_dict(filter(lambda item: "__" not in item[0], row.items()))
    data_group = reduce(grouping, data_with_underscore, {})
    return {**data_without_underscore, **data_group} # Join two dict

#=====================================================================
# This is the function to group multiples rows to only one
#=====================================================================
def union(fundamental, addkey):
    key, value = addkey
    if value[0] not in fundamental[key]:
        fundamental[key].append(value[0])
    return fundamental

def join_row(prev, current):
    dataobject = filter(lambda item: isinstance(item[1], list), current.items())
    return reduce(union, dataobject, prev)

@api_view(['POST'])
def query_api(request, format=None):
    query_string = (request.body).decode("utf-8")
    base_url = 'http://localhost:10011/new/'
    appplication = 'his_b-connect'
    url = base_url + appplication
    data = requests.post(url, query_string )
    if 'cause' in data.json():
        return HttpResponse("{'error':'error'}", content_type="application/json")
    json_output = json.dumps( reduce(join_row, map(group_underscore_key, data.json() )) )
    return HttpResponse( json_output , content_type="application/json")