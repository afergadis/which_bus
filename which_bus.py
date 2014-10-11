#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# which_bus.py
#
# Copyright 2014 Aris Fergadis <fergadis.aris@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
from ladon.ladonizer import ladonize
from ladon.types.ladontype import LadonType
from ladon.compat import PORTABLE_STRING
from sklearn.neighbors import NearestNeighbors
from pandas import read_csv, read_table, DataFrame


class Route(LadonType):
    """
    Stores the stop description and a list with
    the bus lines that pass from this stop (routes).
    """
    stop_desc = PORTABLE_STRING
    route_desc = [PORTABLE_STRING]


class WhichBus(object):
    """
    This is a web service than can be accessed with the following
    interfaces: soap, soap11, jsonrpc10, jsonwsp, xmlrpc</br>
    Example using jsonwsp:</br>
    >>> from ladon.clients.jsonwsp import JSONWSPClient</br>
    >>> client = JSONWSPClient(\
    'http://localhost:8080/WhichBusService/jsonwsp/description')</br>
    >>> bus_stops = client.find_routes(\
    search_phrase="5ο ΓΥΜΝΑΣΙΟ ΑΘΗΝΑΣ", n_stops=4)</br>
    >>> print(bus_stops.response_dict['result'])</br>
    """

    def __init__(self):
        # Load data
        self.public_sector = read_table(
            "data/dhmosia_kthria/dhmosia_kthria_attikis.csv",
            index_col="ktirio_ypiresia", sep=';')
        self.stops = read_csv("data/oasa/stops.txt")
        self.routes = read_csv("data/oasa/routes.txt",
                               index_col="route_short_name")
        self.stop_times = read_csv("data/oasa/stop_times.txt",
                                   index_col="stop_id")
        # Get only the coordinates of the bus stops to make the
        # "training" data
        self.coordinates = DataFrame.as_matrix(
            self.stops, columns=["stop_lon", "stop_lat"])
        self.nbrs = NearestNeighbors().fit(self.coordinates)

    @ladonize(PORTABLE_STRING, int, rtype=[Route])
    def find_bus_stops(self, search_phrase=PORTABLE_STRING(''), n_stops=2):
        """
        <p>Searches by name of a building and the number of nearby stops.</p>

        :param search_phrase: the name of the building,
               e.g. "5ο ΓΥΜΝΑΣΙΟ ΑΘΗΝΑΣ"</br>
        :type search_phrase: str</br>
        :param n_stops: the number of the nearby stops</br>
        :type n_stops: int</br>
        :return: the names of the bus stops with the
                 bus lines that passes from them</br>
        :rtype: Route</br>
        """
        routes_results = []
        lon = self.public_sector.ix[search_phrase].longitude
        # lon has 23,7536 but we want 23.7536
        lon = lon.replace(',', '.')
        lat = self.public_sector.ix[search_phrase].latitude
        lat = lat.replace(',', '.')
        search_point = [lon.strip(), lat.strip()]
        results = self.nbrs.kneighbors(search_point, n_stops,
                                       return_distance=False)
        for r in range(n_stops):
            route_for_stop = Route()
            route_for_stop.route_desc = []
            # Find the stop id from stops
            stop_id = self.stops.ix[results[0, r]]["stop_id"]
            route_for_stop.stop_desc = "{}, {}". \
                format(self.stops.ix[results[0, r]].stop_name,
                       self.stops.ix[results[0, r]].stop_desc)
            # Find the trips ids for that stop
            trips_of_stop_id = self.stop_times.ix[stop_id]
            route_ids = []  # List with all routes from the stop
            for trip in trips_of_stop_id.trip_id:
                # trip has the form 7038869-ΤΗΛΕΜΑ-Τ5-Παρασκευή-03
                # We want the 3rd item (T5)
                route_num = trip.split('-')[2]
                # We get many trip ids which are for the same route
                # (T5) but for different days and times
                if not route_num in route_ids:
                    # We keep the route id (T5) only one time,
                    # and the rest route ids
                    route_ids.append(route_num)

            for route_id in route_ids:
                route_for_stop.route_desc +=\
                    ["{:>3s}, {}".format(route_id,
                                         self.routes.ix[route_id].route_long_name)]

            routes_results += [route_for_stop]

        return routes_results


if __name__ == "__main__":
    search = input(
        "Δώστε την ονομασία του κτιρίου (π.χ. 5ο ΓΥΜΝΑΣΙΟ ΑΘΗΝΑΣ): ")

    while True:
        try:
            n_stops = int(input("Πλήθος στάσεων προς αναζήτηση (π.χ. 3): "))
            if n_stops <= 0:
                print("Παρακαλώ δώστε αριθμό μεγαλύτερο από το μηδέν.")
            else:
                break  # We've got the number of stops
        except ValueError:
            print("Παρακαλώ δώστε αριθμό.")

    wb = WhichBus()
    find_results = wb.find_bus_stops(search, n_stops)
    for i in range(len(find_results)):
        print("Ονομασία Στάσης: {}".format(find_results[i].stop_desc))
        for route in find_results[i].route_desc:
            print("\tΓραμμή: {}".format(route))
        print()
