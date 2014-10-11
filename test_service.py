# -*- coding: utf-8 -*-
"""
Tests the which_bus_service. The server should be started.
If not, please run runserver.py first.
"""
from ladon.clients.jsonwsp import JSONWSPClient
import pprint


def print_result(jsonwsp_resp):
    if jsonwsp_resp.status == 200:
        pprint.pprint(jsonwsp_resp.response_dict['result'], indent=2)
    else:
        print("A problem occurred while communicating with the service:\n")
        print(jsonwsp_resp.response_body)

client = JSONWSPClient('http://localhost:8080/WhichBus/jsonwsp/description')
bus_stops = client.find_bus_stops(search_phrase="5ο ΓΥΜΝΑΣΙΟ ΑΘΗΝΑΣ", n_stops=4)
print_result(bus_stops)
